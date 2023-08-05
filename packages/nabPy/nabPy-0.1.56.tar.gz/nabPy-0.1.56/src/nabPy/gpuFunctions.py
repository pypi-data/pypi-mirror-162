#this file contains the GPU version of the various functions
#it is not always imported. The script basicFunctions determines if this is imported or not

import numpy as np
import sys, os
import dask.array as da
import matplotlib.pyplot as plt

import cupy
import cupyx
from cupyx.scipy.fft import get_fft_plan
import cupy_backends
from cupy.cuda import cufft
import numba
from numba import vectorize, cuda, jit

cupy.cuda.set_allocator(None)
cupy.cuda.set_pinned_memory_allocator(None)

from . import basicFunctions as bf

@cuda.jit("(float32[:,:], int32[:], int32, int32, float32, int32, int32, int32, complex64[:])")
def __extractTrapCuspResultsGPU(filtered, maxlocs, rise, top, percentage, shift, mean, batchsize, out):
	j = cuda.grid(1)
	if j < batchsize:
		wave = filtered[j]
		wavelen = filtered.shape[1]
		maxloc = maxlocs[j]
		maxval = wave[maxloc]
		threshold = maxval * percentage
		#find upwards cross point
		#iterate from the max location back towards beginning
		i = maxloc
		found = False
		leftCross = None
		rightCross = None
		while i >= maxloc - rise - top and found == False and i >= 0:
			if wave[i] >= threshold and wave[i-1] <= threshold:
				found = True 
				leftCross = i
			i-= 1
		rightCross = None
		found = False
		i = maxloc
		while i <= maxloc + rise + top and found == False and i <= wavelen-1:
			if wave[i-1] >= threshold and wave[i]<= threshold:
				found = True
				rightCross = i
			i+=1
		#now use these to extract the results
		if rightCross is None or leftCross is None:
			out[j] = np.complex64(complex(np.nan, np.nan))
		else:
			midpoint = (leftCross + rightCross)/2
			ener = 0
			if mean == 0:
				out[j] = np.complex64(complex(wave[int(midpoint)+shift],  midpoint - top/2 - rise))
			else:
				t = 0.0
				loc = int(midpoint+shift)
				for k in range(mean):
					t+=wave[loc+k]
				out[j] = np.complex64(complex(t/float(mean), midpoint - top/2 - rise))

def gpuTrapCuspFilterImplementation(waves, method='trap', rise=625, top=100, tau=1250, percentage=0.8, pretrigger = 800, shift = 0, mean = 0, numStreams = 2, batchsize=2048):
	"""
	This is a GPU-based implementation of the filtering routine using either the trapezoidal filter or the cusp filter depending on what the user requests. 
	
	Parameters
	----------
	waves: np.ndarray or dask.ndarray
		Input waveforms
	
	inputFilter: np.ndarray
		The filter input to the function
	
	rise, top, tau: see Nab.bf.defineSingleTrap
	
	percentage: between 0 and 1
		threshold cross percentage used for extraction
	
	pretrigger: int
		length of window of waveform before the daq trigger expected location
	
	shift: int
		energy extraction point
	
	minBatchSize: int
		the smallest a batch can be. Based on the HDF5 chunking behavior. This is the HDF5 chunk size
	"""
	#iterate over the chunks in the dask array
	if type(waves) == np.ndarray:
		waves = da.asarray(waves, chunks = {0: batchsize, 1: -1})
	#now create the various arrays and plans
	#get chunk sizes and waveform length information
	numWaves, waveformLength = waves.shape
	if method=='trap':
		inputFilter = bf.defineSingleTrap(rise, top, tau)
	elif method=='cusp':
		inputFilter = bf.defineCuspFilter(rise, top, tau)
	filterLength = len(inputFilter)
	padLength = waveformLength + filterLength - 1
	padLength = cupyx.scipy.fft.next_fast_len(padLength) #does the clever padding trick to improve performance
	while padLength % 2 != 0:
		padLength = cupyx.scipy.fft.next_fast_len(padLength+1)
	#figure out the Dask chunk size
	blockSize = waves.blocks[0].shape[0]
	outputSize = (blockSize, padLength)
	
	#pad the filter
	paddedFilt = np.zeros(outputSize[1], dtype=np.float32)
	paddedFilt[:len(inputFilter)] = inputFilter[:]
	#now scale the filter to match the behavior of the FFT algorithm
	paddedFilt[:] = paddedFilt[:]/float(padLength)
	gpuFiltFFTBatchedStreams = []
	gpuBatchWaveformsStreams = []
	gpuBatchWaveformsPaddedStreams = []
	fftPlanStreams = []
	gpuBatchWaveformsFFTStreams = []
	fftPlanReverseStreams = []
	cudaStreams = []
	pinnedBatches = []
	meansStreams = []
	gpuResultsStreams = []
	maxlocsStreams = []
	for i in range(numStreams): #create the cuda streams and storage containers
		s = cupy.cuda.Stream(non_blocking=True)#first initialize the stream
		cudaStreams.append(s)
		with s: #set us to using that particular stream
			#move the filter to the GPU and calculate it's FFT
			gpuFilt = cupy.array(paddedFilt)
			#define the FFT plan for the filter
			filtrFFTPlan = cupy.cuda.cufft.Plan1d(outputSize[1], cupy.cuda.cufft.CUFFT_R2C, 1)
			#create the output array from this function
			gpuFiltFFT = filtrFFTPlan.get_output_array(gpuFilt)
			#now calculate the fft of this filter
			filtrFFTPlan.fft(gpuFilt, gpuFiltFFT, cupy.cuda.cufft.CUFFT_FORWARD)
			#configure this to work for batched multiplications
			gpuFiltFFTBatched = cupy.array(gpuFiltFFT)[:,cupy.newaxis]
			gpuFiltFFTBatched = gpuFiltFFTBatched.repeat(blockSize, axis=1)
			gpuFiltFFTBatchedStreams.append(gpuFiltFFTBatched.T)
			#now configure the storage spaces on the GPU
			batch = cupyx.zeros_pinned(outputSize, dtype=np.float32)#allocate pinned host memory, size of the original waveforms with padding. Also force conversion to 32-bit at this stage
			pinnedBatches.append(batch)
			#Allocate empty space for the GPU to hold the waveforms
			gpuBatchWaveforms = cupy.empty(outputSize, dtype=cupy.float32)
			gpuBatchWaveformsStreams.append(gpuBatchWaveforms)
			#define the FFT Plan that will be followed for the forward transform
			fftPlan = cupy.cuda.cufft.Plan1d(gpuBatchWaveforms.shape[1], cupy.cuda.cufft.CUFFT_R2C, gpuBatchWaveforms.shape[0])
			fftPlanStreams.append(fftPlan)
			#get the space for the FFT waveforms to live in
			gpuBatchWaveformsFFT = fftPlan.get_output_array(gpuBatchWaveforms)
			gpuBatchWaveformsFFTStreams.append(gpuBatchWaveformsFFT)
			#define the plan for the reverse FFT plan to be followed
			fftPlanReverse = cupy.cuda.cufft.Plan1d(gpuBatchWaveforms.shape[1], cupy.cuda.cufft.CUFFT_C2R, gpuBatchWaveforms.shape[0])
			fftPlanReverseStreams.append(fftPlanReverse)
			#storage space for the mean values
			means = cupy.empty(waves.blocks[0].shape[0], dtype=np.float32)
			meansStreams.append(means)
			maxlocs = cupy.empty(blockSize, dtype=np.int32)
			maxlocsStreams.append(maxlocs)
			gpuResults = cupy.empty(blockSize, dtype=np.complex64)
			gpuResultsStreams.append(gpuResults)
			del gpuFilt
			del filtrFFTPlan
			del gpuFiltFFT
	#now set up the cuda blocks and whatnot
	threadsperblock = 512 #set up the blocks
	blockspergrid = int(np.ceil(blockSize/threadsperblock))
	#store the current location in the process
	currLoc = 0
	#store the overall results
	results = np.zeros(numWaves, np.csingle)
	for i in range(0, waves.numblocks[0], numStreams):
		#grab each block of memory
		blocks = []
		for j in range(numStreams):
			if i + j < waves.numblocks[0]:
				blocks.append(waves.blocks[i+j])
		#start up the first set of operations, then queue up the second set
		#should be able to do dumb streams here
		for j in range(len(blocks)):
			with cudaStreams[j]:
				pinnedBatches[j][:blocks[j].shape[0],:waveformLength] = blocks[j].compute() #move to the storage in pinned memory
				gpuBatchWaveformsStreams[j].set(pinnedBatches[j]) #move to the GPU
				#calculate the means of the waveforms
				cupy.mean(gpuBatchWaveformsStreams[j][:,:pretrigger], axis = 1, out = meansStreams[j])
				#shift the waveform by the pretrigger region mean
				cupy.subtract(gpuBatchWaveformsStreams[j], meansStreams[j][:,None], out=gpuBatchWaveformsStreams[j])
				#reset the padding region to 0
				gpuBatchWaveformsStreams[j][:,waveformLength:] = 0
				#calculate the FFT
				fftPlanStreams[j].fft(gpuBatchWaveformsStreams[j], gpuBatchWaveformsFFTStreams[j], cupy.cuda.cufft.CUFFT_FORWARD)
				#now multiply the FFT waveform data with the FFT filter
				cupy.multiply(gpuBatchWaveformsFFTStreams[j], gpuFiltFFTBatchedStreams[j], out=gpuBatchWaveformsFFTStreams[j])
				#do the inverse FFT operation
				fftPlanReverseStreams[j].fft(gpuBatchWaveformsFFTStreams[j], gpuBatchWaveformsStreams[j], cupy.cuda.cufft.CUFFT_INVERSE)
				#now to do the extraction
				cupy.argmax(gpuBatchWaveformsStreams[j], axis=1, out = maxlocsStreams[j])
				__extractTrapCuspResultsGPU[blockspergrid, threadsperblock](gpuBatchWaveformsStreams[j], maxlocsStreams[j], rise, top, percentage, shift, mean, blockSize, gpuResultsStreams[j])
			#now synchronize the streams once all this has been queued up
		for j in range(len(blocks)):
			cudaStreams[j].synchronize()
			results[currLoc:currLoc+blocks[j].shape[0]] = gpuResultsStreams[j].get()[:blocks[j].shape[0]]
			currLoc += blocks[j].shape[0]
	del paddedFilt #
	del gpuFiltFFTBatchedStreams
	del gpuBatchWaveformsStreams
	del fftPlanStreams
	del gpuBatchWaveformsFFTStreams
	del fftPlanReverseStreams
	del cudaStreams
	del pinnedBatches
	del meansStreams
	del gpuResultsStreams
	del maxlocsStreams
	return results


@cuda.jit("(float64[:,:], float32[:,:], int32[:], int32, int32, int32)")
def __findRelevantWaveformPieces(waveformOut, waveformIn, maxlocs, fitLength, searchRange, fullRange):
	#this function will be called with as many threads as 
	#waveforms * fitLength
	tid = cuda.grid(1) #figure out the thread we are on
	if tid < fullRange:
		wave = int(tid/fitLength) #which waveform we are on
		loc = tid - wave * fitLength #where in that waveform we are
		startloc = int(maxlocs[wave] - fitLength - searchRange + 1)
		searchLen = int(searchRange * 2 + 1)
		for i in range(searchLen):
			loadedVal = waveformIn[int(wave), int(startloc + loc + i)]
			waveformOut[wave * searchLen + i, loc] = loadedVal

@cuda.jit("(float64[:], float64[:,:], int32[:], int32[:], float64[:], float64[:,:], int32, int32, int32)")
def __grabBestFitParameters(minimumChiValues, bestFitParameters, minChiLocs, maxLocations, chiValues, fitParameters, searchRange, fitLength, numWaveforms):
		#this kernel should be called with as many threads total as the number of waveforms
		#basically one thread per waveform is the ideal
		wave = cuda.grid(1)
		if wave < numWaveforms:
			minLoc = minChiLocs[wave]
			shift = int(wave * (searchRange*2+1)+minLoc)
			minimumChiValues[wave] = chiValues[shift]
			bestFitParams = fitParameters[:,shift]
			for j in range(len(bestFitParams)):
				bestFitParameters[wave,j] = bestFitParams[j]
			newMinLoc = maxLocations[wave] -searchRange+1+minLoc+fitLength//2
			minChiLocs[wave] = newMinLoc

def pseudoInverseFitGPU(waves, templates, baselines, filtert0 = None, searchRange = 10, t0Weight = None, psdWeight = None, returnResiduals = False, rechunk = False, batchsize = 1000, numStreams = 2):
	'''
	This is the pseudoinverse fitting method based on an upcoming paper. Talk with David Mathews for details of it's implementation. This method fits a waveform with a series of template functions that the user provides to the code. Depending on the values provided, it returns different information to the user.
	
	This is the GPU implementation of this function.
	For the CPU implementation, see Nab.bf.pseudoInverseFit
	
	Parameters
	----------
	waves: np.ndarray or dask.array
		The waveforms to be processed. 
		If a np.ndarray, this is converted to a dask.array for bulk processing
	templates: list, np.ndarray (must share n value with baselines)
		a list of the template functions. 
		It is expected to be in the arrangement (t, n) where t is the number of template functions and n is their length
	baselines: list, np.ndarray (must share n value with templates)
		a list of the baseline functions
		Is is expected to be in the arrangement (b, n) where b is the number of baseline functions and n is their length
	filtert0: None, int
		If none, assumes the start time of the template functions provided is in the middle
		If int, that defines the start postion of the waveform
	searchRange: int (defaults to 10):
		the number of datapoints on either side of the predicted t0 location to search for the minimum chi squared value
		Larger values increase computational time
	t0Weight: None, np.ndarray
		If none, an unweighted fit is used to extract t0
		If np.ndarray.ndim = 1: a linear weight is used, no off axis elements
		If np.ndarray.ndim = 2: a full 2d weighting matrix is used
			The matrix must be hermitian if this is used otherwise the algorithm isn't properly defined
	psdWeight: None, np.ndarray
		Same as the t0Weight parameter for the determination of the psd chi squared values
		Can be used to weight different regions of the waveform more heavily for discrimination
	returnResiduals: False
		Controls if the residuals of the fit are returned or not
	Returns
	-------
	If the fitting fails, all returned values for that waveform are np.nan
	
	best fit parameters: np.ndarray
		a matrix that is [n, t+b] containing the best fit parameters that were found for each waveform
	t0s: np.ndarray
		an array that is n long containing the extracted start time of the waveform.
		This is the location of the best fit as determined by chi squared minimization
	minChis: np.ndarray
		an array that is n long containing the extracted minimum chi squared value
		The degrees of freedom have been divided out but error/uncertainty in each data point has not been
		Requires division by the variance before it can be considered reduced chi squared
	psdPrediction: None, np.ndarray
		If len(templates) == 1: returns None as there is only one template and pulse shape discrimination is irrelevant
		If len(templates) > 1: returns an array that is n long containing the index of the closest matching pulse shape
			to the waveform as determined by the minimization of chi squared algorithm
	'''
	if waves.shape[0] == 0:
		return [], []
	else:
		if filtert0 is not None:
			print('filtert0 != None not supported yet')
			return []
		if t0Weight is not None:
			print('t0Weight != None not supported yet')
			return []
		if psdWeight is not None:
			print('psdWeight != None not supported yet')
			return []
		if returnResiduals==True:
			print('returnResiduals = True not supported yet')
			return []
		searchRange = int(searchRange) #cast it to an integer
		if rechunk or type(waves)==np.ndarray:
			if rechunk and isinstance(waves, da.core.Array): #in the case it's dask
				waves = waves.compute()#load into ram
				waves = da.from_array(waves, chunks = {0: batchsize, 1:-1}) #then put back into dask for chunked operations
			elif isinstance(waves, np.ndarray):
				waves = da.from_array(waves, chunks = {0: batchsize, 1:-1})
		if batchsize == -1:
			batchsize = len(waves)
		numwaves = len(waves)
		waveformLength = waves.shape[1]
		leftover = numwaves % batchsize
		numbatches = int(numwaves / batchsize)
		#now convert the various templates and baseline functions to arrays if they aren't already
		if isinstance(templates, list):
			templates = np.asarray(templates)
		if isinstance(baselines, list):
			baselines = np.asarray(baselines)
		if templates.shape[1] != baselines.shape[1]:
			return [], []
		if filtert0 is None: #assume it's in the middle then
			filtert0 = templates.shape[1]//2
		length = waves.shape[1] #get the size of the filters and waveforms
		filterLength = templates.shape[1]
		padLength = length + filterLength - 1
		padLength = cupyx.scipy.fft.next_fast_len(padLength) #does the clever padding trick to improve performance
		while padLength % 2 != 0:
			padLength = cupyx.scipy.fft.next_fast_len(padLength+1)
		#set up all of the template function work now
		numIdeal = len(templates)
		numBaseline = len(baselines)
		fitMatrix = []
		for shape in templates:
			fitMatrix.append(shape)
		for shape in baselines:
			fitMatrix.append(shape)
		fitMatrix = np.asarray(fitMatrix)
		#now we need to calculate the psuedoinverse
		pseudoInverse = bf.calculatePseudoInverse(fitMatrix, weight = t0Weight)
		#now do the same thing for the psd filters
		psdInverses = []
		for i in range(numIdeal):
			psdInverses.append(np.transpose(bf.calculatePseudoInverse(templates[i], weight = psdWeight)))
		psdInverses = np.asarray(psdInverses)
		#first make the filter that determines the fit parameter maximum location as that is the fastest way
		maxParameterFilter = np.zeros(padLength) #full length of the waveforms for fft convolution
		maxParameterFilter[:pseudoInverse.shape[0]] = np.flip(np.mean(pseudoInverse[:, 0:numIdeal], axis=1))
		maxParameterFilter = maxParameterFilter.astype(np.float32) / float(len(maxParameterFilter))
		#okay with that filter determined now we need to get things to the GPU and handle things with streams and whatnot
		
		blockSize = waves.blocks[0].shape[0]
		outputSize = (blockSize, padLength)
		
		cudaStreams = []
		gpuFiltFFTBatchedStreams = []
		fftPlanReverseStreams = []
		searchRegionStreams = []
		pinnedBatches = []
		gpuBatchWaveformsStreams = [] 
		gpuPostFilteringWaveformsStreams = []
		fftPlanStreams = []
		gpuBatchWaveformsFFTStreams = []
		fitParametersStreams = []
		t0FuncStreams = []
		maxlocsStreams = []
		gpuResultsStreams = []
		gpuInverseStreams = []
		gpuPSDInverseStreams = []
		ytyValuesTempStreams = []
		ytyValuesStreams = []
		ATWAStreams = []
		ATWATempStreams = []
		chiSquaredValuesStreams = []
		xATWAxValuesStreams = []
		minChiLocsStreams = []
		minChiValsStreams = []
		bestFitParamsStreams = []
		for i in range(numStreams): #create the cuda streams and storage containers
			s = cupy.cuda.Stream(non_blocking=True)#first initialize the stream
			cudaStreams.append(s)
			with s: #set us to using that particular stream
				#move the max parameter filter to the GPU
				gpuFilt = cupy.array(maxParameterFilter).astype(cupy.float32)
				#define the FFT plan for the filter
				filtrFFTPlan = cupy.cuda.cufft.Plan1d(outputSize[1], cupy.cuda.cufft.CUFFT_R2C, 1)
				#create the output array from this function
				gpuFiltFFT = filtrFFTPlan.get_output_array(gpuFilt)
				#now calculate the fft of this filter
				filtrFFTPlan.fft(gpuFilt, gpuFiltFFT, cupy.cuda.cufft.CUFFT_FORWARD)
				#configure this to work for batched multiplications
				gpuFiltFFTBatched = cupy.array(gpuFiltFFT)[:,cupy.newaxis]
				gpuFiltFFTBatched = gpuFiltFFTBatched.repeat(blockSize, axis=1)
				gpuFiltFFTBatchedStreams.append(gpuFiltFFTBatched.T)
				#now configure the storage spaces on the GPU
				batch = cupyx.zeros_pinned(outputSize, dtype=np.float32)#allocate pinned host memory, size of the original waveforms with padding. Also force conversion to 32-bit at this stage
				pinnedBatches.append(batch)
				#Allocate empty space for the GPU to hold the waveforms
				gpuBatchWaveforms = cupy.empty(outputSize, dtype=cupy.float32)
				gpuBatchWaveformsStreams.append(gpuBatchWaveforms)
				gpuPostFilteringWaveforms = cupy.empty(outputSize, dtype=cupy.float32)
				gpuPostFilteringWaveformsStreams.append(gpuPostFilteringWaveforms)
				#define the FFT Plan that will be followed for the forward transform
				fftPlan = cupy.cuda.cufft.Plan1d(gpuBatchWaveforms.shape[1], cupy.cuda.cufft.CUFFT_R2C, gpuBatchWaveforms.shape[0])
				fftPlanStreams.append(fftPlan)
				#get the space for the FFT waveforms to live in
				gpuBatchWaveformsFFT = fftPlan.get_output_array(gpuBatchWaveforms)
				gpuBatchWaveformsFFTStreams.append(gpuBatchWaveformsFFT)
				#define the plan for the reverse FFT plan to be followed
				fftPlanReverse = cupy.cuda.cufft.Plan1d(gpuBatchWaveforms.shape[1], cupy.cuda.cufft.CUFFT_C2R, gpuBatchWaveforms.shape[0])
				fftPlanReverseStreams.append(fftPlanReverse)
				maxlocs = cupy.empty(blockSize, dtype=np.int32)
				maxlocsStreams.append(maxlocs)
				gpuResults = cupy.empty(blockSize, dtype=np.complex64)
				gpuResultsStreams.append(gpuResults)
				
				#move the inverse matrix over to the GPU
				gpuInverse = cupy.array(pseudoInverse).astype(cupy.float64)
				gpuPSDInverse = cupy.array(psdInverses)
				#copy for each stream
				gpuInverseStreams.append(gpuInverse)
				gpuPSDInverseStreams.append(gpuPSDInverse)
				
				#we're going to be using the yTWy - xATWAx formula for this
				#allocate space for the sections of the array that are relevant for the search range work
				
				#first the region of the waveform data that will be searched over
				#search range x waveforms x fit length
				searchRegion = cupy.empty((gpuBatchWaveforms.shape[0]*(searchRange*2+1), filterLength), dtype=cupy.float64)
				searchRegionStreams.append(searchRegion)
				#handle if there is a t0 weighting function or not
				t0Func = None
				ATWA = None
				if t0Weight is not None:
					if t0Weight.ndim == 1:
						w = np.zeros((length, length))
						for i in range(length):
							w[i,i] = t0Weight[i]
						t0Func = cupy.array(w)
						ATWA = np.matmul(w, fitMatrix.T)
						ATWA = np.matmul(fitMatrix.T, w)
						del w
					else:
						w = np.copy(t0Weight)
						t0Func = cupy.array(w)
						ATWA = np.matmul(w, fitMatrix.T)
						ATWA = np.matmul(fitMatrix, w)
						del w
					t0FuncStreams.append(t0Func)
				else:
					ATWA = np.matmul(fitMatrix, fitMatrix.T)
				ATWAStreams.append(cupy.array(ATWA))
				ATWATempStreams.append(cupy.empty((gpuBatchWaveforms.shape[0]*int(searchRange*2+1), numIdeal + numBaseline), dtype=cupy.float64))
				#now store the fit parameters from this region
				fitParameters = cupy.empty((int(searchRange*2+1)*gpuBatchWaveforms.shape[0], numIdeal + numBaseline), dtype=cupy.float64)
				fitParametersStreams.append(fitParameters.T)
				#now set up the squared waveform values
				ytyValues = cupy.empty(gpuBatchWaveforms.shape[0]*int(searchRange*2+1), dtype=cupy.float64)
				ytyValuesTemp = cupy.empty((gpuBatchWaveforms.shape[0]*int(searchRange*2+1), filterLength), dtype=cupy.float64)
				ytyValuesStreams.append(ytyValues)
				ytyValuesTempStreams.append(ytyValuesTemp)
				xATWAxValuesStreams.append(cupy.empty(gpuBatchWaveforms.shape[0]*int(searchRange*2+1), dtype=cupy.float64))
				chiSquaredValues = cupy.empty((int(searchRange*2+1)*gpuBatchWaveforms.shape[0]), dtype=cupy.float64)
				chiSquaredValuesStreams.append(chiSquaredValues)
				minChiLocs = cupy.empty(gpuBatchWaveforms.shape[0], dtype=cupy.int32)
				minChiLocsStreams.append(minChiLocs)
				minChiVals = cupy.empty(gpuBatchWaveforms.shape[0], dtype=cupy.float64)
				minChiValsStreams.append(minChiVals)
				bestFitParams = cupy.empty((gpuBatchWaveforms.shape[0], numIdeal + numBaseline), dtype=cupy.float64)
				bestFitParamsStreams.append(bestFitParams)
				del gpuFilt
				del filtrFFTPlan
				del gpuFiltFFT
		
		#with all of this set up now, let's run the code
		threadsperblock = 512 #set up the blocks
		blockspergrid = int(np.ceil(blockSize/threadsperblock))
		#store the current location in the process
		currLoc = 0
		#store the overall results
		results = np.zeros((numwaves, 2 + numIdeal + numBaseline), np.float64)
		
		threadsForWaveformSearching = 512
		fullSearchRange = blockSize*filterLength
		blocksForWaveformSearching = int(np.ceil(fullSearchRange/threadsForWaveformSearching))
		for i in range(0, waves.numblocks[0], numStreams):
			#grab each block of memory
			blocks = []
			for j in range(numStreams):
				if i + j < waves.numblocks[0]:
					blocks.append(waves.blocks[i+j])
			#start up the first set of operations, then queue up the second set
			#should be able to do dumb streams here
			for j in range(len(blocks)):
				with cudaStreams[j]:
					pinnedBatches[j][:blocks[j].shape[0],:waveformLength] = blocks[j].compute() #move to the storage in pinned memory
					gpuBatchWaveformsStreams[j].set(pinnedBatches[j]) #move to the GPU
					#reset the padding region to 0
					gpuBatchWaveformsStreams[j][:,waveformLength:] = 0
					#calculate the FFT
					fftPlanStreams[j].fft(gpuBatchWaveformsStreams[j], gpuBatchWaveformsFFTStreams[j], cupy.cuda.cufft.CUFFT_FORWARD)
					#now multiply the FFT waveform data with the FFT filter
					cupy.multiply(gpuBatchWaveformsFFTStreams[j], gpuFiltFFTBatchedStreams[j], out=gpuBatchWaveformsFFTStreams[j])
					#do the inverse FFT operation
					fftPlanReverseStreams[j].fft(gpuBatchWaveformsFFTStreams[j], gpuPostFilteringWaveformsStreams[j], cupy.cuda.cufft.CUFFT_INVERSE)
					#now to do the extraction
					cupy.argmax(gpuPostFilteringWaveformsStreams[j], axis=1, out = maxlocsStreams[j])
					#now with the maximum value found, need to search around this region for the best fit parameters and whatnot
					#first grab the relevant windows for every waveform in the process at this stage
					__findRelevantWaveformPieces[blocksForWaveformSearching, threadsForWaveformSearching](searchRegionStreams[j], gpuBatchWaveformsStreams[j], maxlocsStreams[j], filterLength, searchRange, fullSearchRange)
					#okay now we have the region around the maximum location, now to find the parameters for that
					if t0Weight is None:
						#first calculate the squares and the yTy values
						cupy.square(searchRegionStreams[j], out=ytyValuesTempStreams[j])
						cupy.sum(ytyValuesTempStreams[j], axis=1, out=ytyValuesStreams[j])
						#now calculate the fit parameters
						cupy.matmul(gpuInverseStreams[j].T, searchRegionStreams[j].T, out = fitParametersStreams[j])
						#with these parameters calculate ATWAx
						cupy.matmul(fitParametersStreams[j].T, ATWAStreams[j], out = ATWATempStreams[j])
						#now calculate xATWAx
						cupy.multiply(fitParametersStreams[j].T, ATWATempStreams[j], out = ATWATempStreams[j])
						cupy.sum(ATWATempStreams[j], axis=1, out=xATWAxValuesStreams[j])
						#now the chi squared values
						cupy.subtract(ytyValuesStreams[j], xATWAxValuesStreams[j], out = chiSquaredValuesStreams[j])
						#now the chi squared values have been found, find the minimum and locations
						cupy.argmin(chiSquaredValuesStreams[j].reshape(blockSize, -1), axis=1, out=minChiLocsStreams[j])
						#now extract the best fit parameters and other information
						__grabBestFitParameters[blockspergrid, threadsperblock](minChiValsStreams[j], bestFitParamsStreams[j], minChiLocsStreams[j], maxlocsStreams[j], chiSquaredValuesStreams[j], fitParametersStreams[j], searchRange, filterLength, blockSize)
			for j in range(len(blocks)):
				cudaStreams[j].synchronize()
				results[currLoc:currLoc+blocks[j].shape[0],:numIdeal+numBaseline] = bestFitParamsStreams[j].get()[:blocks[j].shape[0],:]
				results[currLoc:currLoc+blocks[j].shape[0],numIdeal+numBaseline]=minChiLocsStreams[j].get()[:blocks[j].shape[0]]
				results[currLoc:currLoc+blocks[j].shape[0],numIdeal+numBaseline+1]=minChiValsStreams[j].get()[:blocks[j].shape[0]]
				currLoc += blocks[j].shape[0]
		
		del cudaStreams
		del gpuFiltFFTBatchedStreams
		del fftPlanReverseStreams
		del searchRegionStreams
		del pinnedBatches
		del gpuBatchWaveformsStreams
		del gpuPostFilteringWaveformsStreams
		del fftPlanStreams
		del gpuBatchWaveformsFFTStreams
		del fitParametersStreams
		del t0FuncStreams
		del maxlocsStreams
		del gpuResultsStreams
		del gpuInverseStreams
		del gpuPSDInverseStreams
		del ytyValuesTempStreams
		del ytyValuesStreams
		del ATWAStreams
		del ATWATempStreams
		del chiSquaredValuesStreams
		del xATWAxValuesStreams
		del minChiLocsStreams
		del minChiValsStreams
		del bestFitParamsStreams
		
		return results