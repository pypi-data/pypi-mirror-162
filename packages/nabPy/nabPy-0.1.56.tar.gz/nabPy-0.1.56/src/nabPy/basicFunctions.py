import numpy as np #the usual
import matplotlib.pyplot as plt #import for plotting
import matplotlib.patches as patches #import for pixel maps
import matplotlib.colors as colors #coloration
import matplotlib.cm as cmx #not sure
import os #for file functions
from . import fileFormats as ff #file formats
import struct #useful for reading binary values
import re #sorting files
import tempfile #used when making the animation
import scipy.signal as signal #used for power spectra
import ntpath #used as this is os independent and should work on both windows and linux
from scipy.optimize import curve_fit #used for fitting curves, as it says
from PIL import Image #used for making the gifs
import glob #used to find all files in directory and whatnot
import inspect #this is used to determine the number of parameters passed to a fit function
import gc
import warnings
warnings.filterwarnings('ignore')


#various Dask includes for parallelization of the code
import dask.array as da
from dask import delayed
from dask import compute

#imports for numba to accelerate code and compilation
import numba
from numba.experimental import jitclass #used for the VarDelay class
from numba import float32, float64, int16, int32 #used for the VarDelay class
from numba import vectorize

from tqdm import tqdm

#try to configure the GPU to see if that can be used or not
__gpuAvailable = False
__gpuErrorMessage = None
try:
	from . import gpuFunctions as gpu
	__gpuAvailable = True
except Exception as e:
	__gpuAvailable = False
	__gpuErrorMessage = e

__fxpAvailable = False
try:
	from fxpmath import Fxp #used to handle the fixed point precision calculations in the DAQ emulation
	__fxpAvailable = True
except Exception as e:
	__fxpAvailable = False

__fftwAvailable = False
useFFTW = False
try:
	import pyfftw
	__fftwAvailable = True
	useFFTW = True
except Exception as e:
	__fftwAvailable = False
	useFFTW = False

'''
This script just contains a lot of the standard functionality that is used a lot across the board. 
It's just for convenience really.

At some point this should probably be broken up into different sections but at least for now this is fine.
'''

'''
-----------------------------------------------------------------------------
File handling functions
-----------------------------------------------------------------------------
'''
def natural_sort(l):
	"""
	Sorts in the same way that most OS do

	Parameters
	----------
	l: list
		pass a list of file names

	Returns
	-------
	a sorted list matching how most OS sort files
	"""
	convert = lambda text: int(text) if text.isdigit() else text.lower()
	alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)',key)]
	return sorted(l, key = alphanum_key)

def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)

def convertBinaryString(string):
	"""
	Parses a set of binary data and returns a single string assuming the encoding was utf-8
	Parameters
	----------
	string: list of character values
		A list of character values that were output from a binary file reading functions

	Returns
	-------
	a concatenated string of values interpreted from the utf-8 encoded data
	"""
	string = string.view(np.chararray).decode('utf-8')
	temp = ''
	for a in string:
		temp += a
	return temp

@numba.jit("uint32(uint16[:])")
def Fletcher32(data):
	"""
	Returns the checksum of a particular array of values as determined by the Fletcher32 algorithm.
	Source: https://en.wikipedia.org/wiki/Fletcher%27s_checksum
	This implementation was verified to match the check values in the table. 
	No overflow protection is built in to the addition as in the Nab dataset cannot overflow when using 64-bit containers for the addition.
	Returned value is a 32-bit checksum
		Python may cast this to a 64-bit number but it's really 32-bit
	"""
	sum1 = 0
	sum2 = 0
	for d in data:
		sum1 = sum1+d
		sum2 = sum2+sum1
	sum1 = sum1%65535
	sum2 = sum2%65535
	return (sum2<<16)|sum1


#waveform preparation functions
@vectorize(['int16(uint16)', 'int16(int16)'])
def doAnd(x):
	"""
	This function converts the provided array from 14 bit unsigned numbers stored in 16 bit containers to 16 bit signed values. This is a necessary step when parsing waveform data from the Nab experiment.

	Parameters
	----------
	wave: np.ndarray of dtype np.int16
		The input waveform in a 1d np.ndarray or a series of input waveforms in a 2d np.ndarray
		Technically this can support an arbitrarily sized package of waveform data so long as it is in a np.ndarray

	Returns
	-------
	wave: 
		the modified waveform still stored as a np.int16
	"""
	x = x & 16383
	if x > 8192:
		return x - 16384
	else:
		return x
	return x

def wavePrep(waveform, forcePrep = False):
	"""
	This function prepares the waveforms for analysis and plotting. It converts the 14 bit unsigned waveform data read from a file to 32 bit signed floating point values for processing and analysis. It calls doAnd for the initial conversion to 16 bit.

	Parameters
	----------
	waveform: np.ndarray
		The input waveform or series of input waveforms stored as a np.ndarray
		If the waveform is passed in as np.uint16, then it does the bit shift
		If the waveform is passed in as np.int16, then it doesn't do the bit shift
	forcePrep: bool (defaults to False)
		If true, forces the prep operation to be called
	Returns
	-------
	waveform: np.ndarray
		The waveform stored as 32 bit signed floating point numbers
	"""
	if waveform.dtype == np.dtype(np.uint16):
		waveform = waveform.astype(np.int16)
		waveform = doAnd(waveform)
	elif waveform.dtype == np.dtype(np.int16) and forcePrep:
		waveform = doAnd(waveform)
	return waveform.astype(np.float32)


'''
-----------------------------------------------------------------------------
Compression Functions
-----------------------------------------------------------------------------
'''
@numba.jit
def encodeWaveform(waveform, filt):
	'''
	This function uses a passed filter to encode the waveform. This is a general form of 
	the delta encoding for arbitrary filters. 
	In the special case of the delta filter, this does an optimized algorithm.
	'''
	encoded = np.zeros_like(waveform)
	if np.array_equal(filt.astype(np.int16), np.array([1, -1], dtype=np.int16)):
		#the special case of the delta filter
		lastVal = waveform[0]
		encoded[0] = lastVal
		thisVal = 0
		temp = 0
		for i in range(1, len(encoded)):
			thisVal = waveform[i]
			temp = thisVal - lastVal
			encoded[i] = temp
			lastVal = thisVal
		return encoded
	else:
		for i in range(len(waveform)):
			out = waveform[i] * filt[0]
			for j in range(1, len(filt)):
				if i - j >= 0:
					out += waveform[i-j]*filt[j]
			encoded[i] = out
	return encoded

@numba.jit
def decodeWaveform(encoded, filt):
	output = np.zeros_like(encoded)
	if np.array_equal(filt.astype(np.int16), np.array([1, -1], dtype=np.int16)):
		#the special case of the delta filter
		lastVal = encoded[0]
		output[0] = lastVal
		thisVal = 0
		temp = 0
		for i in range(1, len(output)):
			thisVal = encoded[i]
			temp = thisVal + lastVal
			output[i] = temp
			lastVal = temp
		return output
	for i in range(len(encoded)):
		temp = encoded[i]
		for j in range(1, len(filt)):
			if i - j >= 0:
				temp -= output[i-j]*filt[j]
		temp = temp / filt[0]
		output[i] = temp
	return output

@numba.jit(inline='always')
def getBit(cont, bitnum, end):
	return (cont >> (end - bitnum))&1

@numba.jit(inline='always')
def getBit64(cont, bitnum):
	return ((cont>>(63-bitnum))&1)

@numba.jit
def __determinePowerOf2(M):
	if M <= 0: #invalid
		return -1
	elif int(M) != M:
		return -1
	elif (M & (M - 1)) != 0:
		return -1
	else:
		i = 0
		while i < 64:
			if M == 1:
				return i
			else:
				M = (M>>1)
				i += 1
		return -1

@numba.jit
def compressWithRiceCoding(waveIn, M=8):
	'''
	This function encodes the given array using Rice coding to compress the data. 
	It does this using the given M value for the Golomb parameter. 
	https://en.wikipedia.org/wiki/Golomb_coding
	
	Parameters
	----------
	waveIn:
		The input array. This is expected to be of type np.ndarray with dtype np.int16
			Any other input type will cause undermined behavior
	
	M:
		The tunable Golomb parameter M. This should be a power of 2. Ex: 1, 2, 4, 8, 16
		The optimal parameter for Nab and Ca45 datasets is 8.
	
	Returns
	-------
	out: np.ndaray with type np.uint32
		The compressed array using Golomb coding. 
	'''
	out = []
	temp = np.uint64(0)
	loc = 0
	end = 32
	rShift = __determinePowerOf2(M) #figure out what the number of bits to shift for the remainder is
	if rShift == -1:
		print('M value passed was improper: M>0, power of 2, and integer')
		return np.empty(1, dtype=np.uint32)
	rShift = np.uint16(rShift)
	rShiftVal = np.uint16((np.uint64(1)<<rShift)-1)
	giveup = 8
	for i in range(0, len(waveIn)):
		sign = int(waveIn[i] >=0)
		orig = np.int16(abs(waveIn[i]))
		q = np.uint16(orig>>rShift)
		r = np.uint16(orig&rShiftVal)
		locshift = 0
		if q < giveup: #in the case the system can do the compression just fine
			temp = np.uint64((temp<<np.uint64(q+1))|np.uint64(1)) #shift to the left that many values + 1
			locshift = q+1 #keep track of the current location
			if sign == 1:
				temp=temp<<np.uint64(1)
			else:
				temp = (temp<<np.uint64(1))|np.uint64(1)
			#now handle the remainder
			temp = (temp<<np.uint64(rShift))|np.uint64(r)
			loc+= 1 + rShift + locshift
		else: #if the quotient is too large, do the giveup signal
			temp = (temp << np.uint64(giveup + 1))|np.uint64(1);
			temp = temp << np.uint64(16);
			if waveIn[i] >= 0:
				temp = temp|np.uint64(waveIn[i])
			else:
				temp = temp|np.uint64(waveIn[i]+32768) #this is 2**15, our values must be smaller than 2**15 so this lets the decoder know it was negative
			loc += giveup + 1 + 16 #the length of the giveup signal, 1 for the end code, and then 16 for the length of the datapoint
		if loc>=end: # we have filled 32 bits worth of stuff up, write that
			outVal=temp >> np.uint64(loc - end)
			temp = temp&np.uint64(np.uint64(1<<(loc-end))-1)
			out.append(outVal)
			loc = loc - end
	if loc!=0: #if at the end we haven't freed the 32 bit buffer yet
		outVal = temp<<np.uint64(end - loc)
		out.append(outVal)
	out = np.array(out, dtype=np.uint32)
	return out

@numba.jit
def decompressWithRiceCoding(compressedIn, length, M=8):
	'''
	This function decodes the given array using Rice coding to decompress the data. 
	It does this using the given M value for the Golomb parameter. 
	https://en.wikipedia.org/wiki/Golomb_coding
	
	Parameters
	----------
	waveIn:
		The input array. This is expected to be of type np.ndarray with dtype np.int16
			Any other input type will cause undermined behavior
	length:
		The length of the output array. This is used to tell the code when to terminate in the case that there are bits
		remaining in the final container of the compressed input.
	M:
		The tunable Golomb parameter M that was using during compression. If a different value
		than the one used during compression is used, the results will be meaningless. 
	
	Returns
	-------
	out: np.ndaray with type np.int16
		The de-compressed array
	'''
	compressedLength = len(compressedIn)
	bit = 0
	readval = 0
	bitloc = 0
	#load in the first buffer
	read = compressedIn[0]
	read = read << np.uint64(32)
	read = read|np.uint64(compressedIn[1])
	#set up the remainder shift values, assuming that m = 8
	rShift = __determinePowerOf2(M) #figure out what the number of bits to shift for the remainder is
	if rShift == -1:
		print('M value passed was improper: M>0, power of 2, and integer')
		return np.empty(length, dtype=np.int16)
	rShift = np.uint16(rShift)
	rShiftVal = np.uint16((np.uint16(1)<<rShift)-1)
	val = 0
	waveOut = np.zeros(length, dtype=np.int16)
	firstVal = 0
	bit = 0
	#reverse the bits on this
	for i in range(0, length): #iterate over each expected output datapoint
		q = np.uint64(0)
		while not getBit64(read,bit):
			q+=1
			bit+=1
		bit+=1
		if q == 8: #this is the case when the quotient was too large
			val = (read >> np.uint64((48-bit))&np.uint64(32767)) #48 because of 64 - 16, 32767 = 2**15 - 1
			if val > 16383:
				val = val - 32768
			bit += 16
		else:
			#get the sign of the value now
			sign = ((np.uint16(getBit64(read, bit))^1)<<1)-1
			bit+=1
			#now get the remainder
			r = (read>>np.uint64(64 - rShift - bit))&np.uint64(rShiftVal) #(read>>(64-rshift-bit))&rshifthigh;
			bit += rShift #//rShift
			val = (np.uint64(q)<<np.uint64(rShift))+r 
			val = sign*val
		waveOut[i] = val
		if bit >= 32: #read in more to the buffer
			bit = bit - 32
			bitloc+=1
			read = compressedIn[bitloc]
			read = read << np.uint64(32)
			if bitloc != compressedLength - 1:
				read = read|compressedIn[bitloc + 1]
	return waveOut

'''
Define all of the functions relevant to the trapezoidal filter
'''
def defineSingleTrap(rise, top, tau, length=None):
	"""
	This function defines the standard trapezoidal filter as discussed in the Jordanov paper in such a way as to be used in a convolution based filtering approach. That paper defines it for recursive implementations, this is a convolution based implementation more suited for Python and use with convolution functions such as numpy's np.convolve or np.fftconvlve.

	Nuclear Instruments and Methods in Physics Research A353 (1994) 261-264
	https://deepblue.lib.umich.edu/bitstream/handle/2027.42/31113/0000009.pdf?sequence=1

	Parameters
	----------
	rise: int
		this parameter controls the length of the rising edge of the trapezoid. This should be tuned and optimized based on the noise in the system. A good initial guess is the same value as tau.
	top: int
		the length of the flat top of the trapezoid. This should be longer than the expected rising edge of the pulse shape to properly integrate accumulated charge.
	tau: int, float
		the decay constant of the electronics. This should be a fixed value determined by the electronics chain. This can be determined by fitting the decaying region of multiple waveforms to an exponentially decaying function and extracting the decay rate
	length: int (defaults to None)
		the desired length of the filter. This needs to be at least 2 * rise + top and can be longer if padding is desired for the filtering process (some convolution based filtering methods need the filter and waveform to be the same size)
		If no input is provided, this defaults to None and the filter is not padded
	Returns
	-------
	filter: np.ndarray
		This returns the filter defined in a numpy array ready to be convolved with the waveform. It is pre-scaled such that the output from using this filter with a normalized convolution methodology will not artificially scale the waveform amplitude. With some FFT-based convolution techniques, additional scaling may be necessary if the method isn't already normalized.
	"""
	filt = None
	if length is None:
		filt = np.zeros(rise * 2 + top)
	else:
		if length < rise * 2 + top:
			print('invalid length parameter')
			print('should be longer than rise * 2 + top')
			return None
		else:
			filt = np.zeros(length)
	for i in range(rise):
		filt[i]=i+tau
		filt[i+rise+top]=rise-tau-i
	for i in range(rise,rise+top):
		filt[i]=rise
	for i in range(rise+rise+top,len(filt)):
		filt[i]=0
	scale=1.0/(rise*tau)
	filt*=scale
	return filt

def defineDoubleTrap(rise, top, tau, length=None):
	'''
	Returns the double trapezoidal filter as used in the DAQ. 
	See the defineSingleTrap for more information about the single trapezoid. 
	Parameters
	----------
	rise: int
		this parameter controls the length of the rising edge of the trapezoid. This should be tuned and optimized based on the noise in the system. A good initial guess is the same value as tau.
	top: int
		the length of the flat top of the trapezoid. This should be longer than the expected rising edge of the pulse shape to properly integrate accumulated charge.
	tau: int, float
		the decay constant of the electronics. This should be a fixed value determined by the electronics chain. This can be determined by fitting the decaying region of multiple waveforms to an exponentially decaying function and extracting the decay rate
	length: int, defaults to None
		the desired length of the filter. This needs to be at least 4 * rise + 2 * top and can be longer if padding is desired for the filtering process (some convolution based filtering methods need the filter and waveform to be the same size)
		If no input is provided, this defaults to None and will mean the output is not padded with 0's
	Returns
	-------
	filter: np.ndarray
		This returns the filter defined in a numpy array ready to be convolved with the waveform. It is pre-scaled such that the output from using this filter with a normalized convolution methodology will not artificially scale the waveform amplitude. With some FFT-based convolution techniques, additional scaling may be necessary if the method isn't already normalized.
	'''
	if length is None:
		length = rise * 4 + top * 2
	else:
		if length < rise * 4 + top * 2:
			print('invalid length parameter')
			print('should be longer than rise * 2 + top')
			return None
	singleTrap = defineSingleTrap(rise, top, tau)
	boxcar = np.zeros(len(singleTrap)+1)
	boxcar[0] = -1
	boxcar[rise+top] = 1
	doubleTrap = np.convolve(singleTrap, boxcar)
	if len(doubleTrap) < length:
		out = np.zeros(length)
		out[:len(doubleTrap)] = doubleTrap[:]
		return out
	else:
		return doubleTrap[:length]

'''
Define some classes to be used in the DAQ Filter Emulation.
These are used to replicate the delay functions in the DAQ.
'''
spec = [('data', int32[:])]
@jitclass(spec)
class VarDelay:
	def __init__(self,size):
		self.data = np.zeros(size, dtype=int32)
	def Stuff(self,value):
		first_out = self.data[-1]
		self.data = np.roll(self.data,1)
		self.data[0] = value
		return first_out

spec = [('data', float32[:])]
@jitclass(spec)
class VarDelayFloat:
	def __init__(self,size):
		self.data = np.zeros(size, dtype=float32)
	def Stuff(self,value):
		first_out = self.data[-1]
		self.data = np.roll(self.data,1)
		self.data[0] = value
		return first_out

@numba.jit
def daqFilterEmulator(waveform, rise, top, tau, scaleFactor):
	'''
	This function emulates the DAQ filtering for the given input waveform and parameters.
	
	Parameters
	----------
	waveform: np.ndarray
		a 1d array with a single waveform
	rise: int
		the risetime parameter for the trapezoidal filter
	top: int
		the flat top length of the trapezoidal filter
	tau: int
		the decay rate parameter for the trapezoidal filter
	scaleFactor: float
		The scale factor for the division operation. This should be calculated via:
		scaleFactor = int(1.0/Fxp(1.0/(float(tau) * float(rise)), signed=False, n_word=24, n_frac=23))
		This method ensures the proper precision is used
	
	Returns
	-------
	filtered waveform: list
		The input waveform post down-sampling and filtering
	'''
	rise = int(rise)
	top = int(top)
	tau = int(tau)
	mult_tau = float(tau)
	#first we need to downsample the DAQ timebins
	downSampled = []
	for i in range(0, len(waveform), 2):
		t = waveform[i] + waveform[i+1]
		if t > 16382:
			t = 16382
		elif t < -16384:
			t = -16384
		downSampled.append(np.floor_divide(t, 2))
	delay_b = VarDelayFloat(rise)
	delay_c = VarDelayFloat(top)
	delay_d = VarDelayFloat(rise)
	delay_f = VarDelayFloat(1)
	delay_k = VarDelayFloat(1)
	delay_l = VarDelayFloat(2)
	delay_n = VarDelay(1)
	delay_q = VarDelay(1)
	delay_s = VarDelay(rise+top)
	delay_u = VarDelay(1)
	delay_y = VarDelay(1)
	delay_z = VarDelay(1)
	acc1 = 0
	acc2 = 0
	acc3 = 0
	output = []
	for val in downSampled:
		B = delay_b.Stuff(val)
		C = delay_c.Stuff(B)
		D = delay_d.Stuff(C)
		F = delay_f.Stuff(val-B-C+D)
		acc1 += F
		K = delay_k.Stuff(acc1)
		L = delay_l.Stuff(int(F*mult_tau))
		N = delay_n.Stuff(int(K+L))
		acc2 += N
		Q = delay_q.Stuff(acc2)
		S = delay_s.Stuff(acc2)
		U = delay_u.Stuff(S)
		acc3 += Q-acc2+S-U
		Y = delay_y.Stuff(acc3)
		output.append(delay_z.Stuff(np.rint(Y / scaleFactor)))
	return output

def emulateDAQFilter(waves, rise, top, tau, triggerThreshold):
	"""
	This function emulates the DAQ filtering of the incoming waveforms. 
	
	It is not designed for high throughput but instead designed to emulate the DAQ behavior as accurately as possible.
	This uses a modified form of the double trapezoidal filter.
	
	Parameters
	----------
	waves: np.ndarray
		a 2d numpy array with waveforms in it
	rise: int
		the risetime parameter for the trapezoidal filter
	top: int
		the flat top length of the trapezoidal filter
	tau: int
		the decay rate parameter for the trapezoidal filter
	
	Returns
	-------
	filteredWaveforms: np.ndarray
		a 2d numpy array with the filtered waveforms in it
	"""
	if waves.shape[0] == 0:
		return [], []
	else:
		if __fxpAvailable:
			if type(waves) == np.ndarray: #convert to dask array to do things in parallel
				waves = da.asarray(waves)
			#figure out the scale factor
			scaleFactor = int(1.0/Fxp(1.0/(float(tau) * float(rise)), signed=False, n_word=24, n_frac=23))
			filteredWaves = da.apply_along_axis(daqFilterEmulator, 1, waves, rise, top, tau, scaleFactor).compute()
			return filteredWaves
		else:
			print('fxpmath library not available. This is required for this function.')
			print('Install from: https://github.com/francof2a/fxpmath ')
			return [], []

@numba.jit
def extractTrapResults(filtered, rise, top, percentage, shift = 0, mean = 0):
	"""
	This function extracts the results from the trapezoidal filter. It does so with a percent threshold cross algorithm so it looks for a maximum, identifies the filter output information, and extracts timing and energy information from this.
	
	Parameters
	----------
	filtered: np.ndarray
		The output of the convolution of the waveform and the filter
	rise: int
		the rise time parameter for the trapezoidal filter
	top: int
		the flat top length for the trapezoidal filter
	percentage: float(0 through 1)
		the percent threshold used 
	
	Returns
	-------
	energy: float
		the energy extracted from the waveform
	timing: float
		the start time of the waveform
	"""
	maxloc = np.argmax(filtered)
	maxval = filtered[maxloc]
	threshold = maxval * percentage
	#find upwards cross point
	#iterate from the max location back towards beginning
	i = maxloc
	found = False
	leftCross = None
	while i >= maxloc - rise - top and found == False:
		if filtered[i] >= threshold and filtered[i-1] <= threshold:
			found = True 
			leftCross = i-1
		i-= 1
	rightCross = None
	found = False
	i = maxloc
	while i <= maxloc + rise + top and found == False:
		if filtered[i] >= threshold and filtered[i+1] <= threshold:
			found = True
			rightCross = i + 1
		i+=1
	#now use these to extract the results
	if rightCross is None or leftCross is None:
		return np.nan, np.nan
	else:
		midpoint = (leftCross + rightCross)/2
		if mean == 0:
			return filtered[int(midpoint)+shift], midpoint - top/2 - rise
		else:
			if mean < 0:
				return filtered[int(midpoint+shift-mean):int(midpoint+shift+1)].mean(), midpoint - top/2 - rise
			else:
				return filtered[int(midpoint+shift):int(midpoint+shift+mean)].mean(), midpoint - top/2 - rise

def pyFFTWExtraction(waveforms, pretrigger, fftFilt, padLen, extractionFunc, args, batchsize = -1, block_info = None):
	"""
	This is a more efficient form of convolution using the FFTW library. 
	It's more efficient than the standard numpy/scipy/dask implementations
	"""
	numWaves, waveformLength = waveforms.shape
	if batchsize <= 0 or batchsize >= numWaves:
		batchsize = numWaves
	numBatches = numWaves//batchsize
	if numWaves % batchsize != 0:
		numBatches += 1
	#prep the work environment for the stuff
	#create the buffers that'll be used for the FFTs
	padded = np.zeros(shape=(batchsize, padLen), dtype=np.float32)
	fftArray = np.zeros(shape=[batchsize, padLen//2+1], dtype=np.complex64)
	#create the FFT plans
	fftForward = pyfftw.FFTW(padded, fftArray, direction='FFTW_FORWARD', axes=[1])
	fftReverse = pyfftw.FFTW(fftArray, padded, direction='FFTW_BACKWARD', axes=[1])
	#create the results array 
	results = np.zeros(shape=(numWaves, 2))
	for i in range(numBatches):
		startLoc = batchsize * i
		stopLoc = batchsize * (i+1)
		if stopLoc > numWaves:
			stopLoc = numWaves
		padded[:stopLoc-startLoc,:waveformLength] = waveforms[startLoc:stopLoc,:] 
		means = padded[:stopLoc-startLoc,0:pretrigger].mean(axis=1)
		padded[:stopLoc-startLoc,:waveformLength] = np.subtract(padded[:stopLoc-startLoc,:waveformLength], means[:,None])
		fftForward() #do their FFT, now the FFT results are stored in the fftArray array
		#fftArray *= fftFilt #do the multiplication in place or as in place as python allows
		np.multiply(fftArray, fftFilt, out=fftArray)
		fftReverse() #now undo the FFT back
		#fft has now been applied, apply the extraction function
		res = np.apply_along_axis(extractionFunc, 1, padded, *args)
		results[startLoc:stopLoc,0] = np.copy(res[:stopLoc-startLoc,0])
		results[startLoc:stopLoc,1] = np.copy(res[:stopLoc-startLoc,1])
		padded[:,:] = 0 #reset it to 0
	del padded
	del fftArray
	del fftFilt
	del means
	del res
	del fftForward
	del fftReverse
	del waveforms
	return results

def defineCuspFilter(rise_time, flat_top, tau, length = None):
	"""
	Defines the standard cusp filter. Check this paper for possibly useful information.
	https://arxiv.org/abs/1504.02039
	Definition taken from Aaron Jezghani's DSP gitlab
	https://gitlab.com/apjezghani/DigitalSignalProcessing
	
	Parameters
	----------
	rise_time: int
		the shaping time of the filter. Similar to the rise time parameter in the trapezoidal filter
	flat_top: int
		length of the charge integration time. Similar to the flat top parameter for the trapezoidal filter
	tau: int, float
		the decay rate parameter. Should be tuned to match the decay rate of the waveforms
	Returns
	-------
	filter: np.ndarray
		The filter defined for convolution based implementations
	"""
	filter_length = 2*rise_time+flat_top
	if length is None:
		length = filter_length
	out = np.zeros(length+filter_length)
	p0_1 = np.zeros(length+filter_length) #0th-order polynomial, segment 1
	p1_1 = np.zeros(length+filter_length) #1st-order polynomial, segment 1
	p2_1 = np.zeros(length+filter_length) #2nd-order polynomial, segment 1
	p0_2 = np.zeros(length+filter_length) #0th-order polynomial, segment 2
	p0_3 = np.zeros(length+filter_length) #0th-order polynomial, segment 3
	p1_3 = np.zeros(length+filter_length) #1st-order polynomial, segment 3
	p2_3 = np.zeros(length+filter_length) #2nd-order polynomial, segment 3
	c0_1 = 0.5*(tau-0.5) # coefficient for p0_1
	c1_1 = (tau-0.5) # coefficient for p1_1
	c2_1 = 1.0 #coefficient for p2_1
	c0_2 = 0.5*rise_time*(rise_time+1.) #coefficient for p0_2
	c0_3 = .5*(rise_time+rise_time*rise_time-(tau-0.5)-2.*rise_time*(tau-0.5)) #coefficient for p0_3
	c1_3 = -1.-rise_time+(tau-0.5) #coefficient for p1_3
	c2_3 = 1.0 #coefficient for p2_3
	inp = np.zeros(filter_length+length)
	inp[1] = 1
	for i in range(length):
		p0_1[i+filter_length] = p0_1[i+filter_length-1] + inp[i] - (inp[i-rise_time] if i>=rise_time else 0)
		p1_1[i+filter_length] = p1_1[i+filter_length-1] + p0_1[i+filter_length] - (rise_time*inp[i-rise_time] if i>=rise_time else 0)
		p2_1[i+filter_length] = p2_1[i+filter_length-1] + p1_1[i+filter_length] - (.5*rise_time*(rise_time+1)*inp[i-rise_time] if i>=rise_time else 0)

		p0_2[i+filter_length] = p0_2[i+filter_length-1] + (inp[i-rise_time] if i>=rise_time else 0.) - (inp[i-rise_time-flat_top] if i>=(rise_time+flat_top) else 0.)

		p0_3[i+filter_length] = p0_3[i+filter_length-1] + (inp[i-rise_time-flat_top] if i>=(rise_time+flat_top) else 0) - (inp[i-filter_length] if i>=filter_length else 0.0)
		p1_3[i+filter_length] = p1_3[i+filter_length-1] + p0_3[i+filter_length] - (rise_time*inp[i-filter_length] if i>=filter_length else 0.)
		p2_3[i+filter_length] = p2_3[i+filter_length-1] + p1_3[i+filter_length] - (.5*rise_time*(rise_time+1)*inp[i-filter_length] if i>=filter_length else 0.)

		out[i] = (c0_1*p0_1[i+filter_length]+c1_1*p1_1[i+filter_length]+c2_1*p2_1[i+filter_length]+c0_2*p0_2[i+filter_length]+c0_3*p0_3[i+filter_length]+c1_3*p1_3[i+filter_length]+c2_3*p2_3[i+filter_length])/(.5*rise_time*(rise_time+1.)*(tau-0.5));
	del p0_1
	del p1_1
	del p2_1
	del p0_2
	del p0_3
	del p1_3
	del p2_3
	return out[:length]

def extractCuspResults(filtered, rise, top, percentage, shift = 0, mean = 0):
	"""
	This function extracts the energy and timing information from the cusp filter output
	It wraps around the Trapezoidal Filter Energy Extraction as they are the same algorithm
	Parameters
	----------
	filtered: np.ndarray
		the filtered output of the waveform with the cusp filter
	rise: int
		the rise time provided to the cusp filter. This is used to correct for the timing
	
	Returns
	-------
	energy: float
		the peak amplitude of the waveform
	timing: int
		the start time of the waveform
	"""
	return extractTrapResults(filtered, rise, top, percentage, shift = shift, mean = mean)

def applyTrapFilter(waves, rise, top, tau, percentage = 0.8, mean = 0, shift = 0, pretrigger=800, batchsize = 1000, useGPU = False, hdf5ChunkSize = None, rechunk = False, useFFTW = True):
	"""
	This function applies the trapezoidal filter to a batch of waveforms and extracts energy and timing information with it. This version of the filter is defined via convolutions instead of the standard recursive method to improve performance in Python.
	For a description of the trapezoidal filter defined here, check this resource.
	Nuclear Instruments and Methods in Physics Research A353 (1994) 261-264
	https://deepblue.lib.umich.edu/bitstream/handle/2027.42/31113/0000009.pdf?sequence=1
	
	Parameters
	----------
	waves: np.ndarray
		a 2d numpy array with waveforms in it
	rise: int
		the risetime parameter for the trapezoidal filter
	top: int
		the flat top length of the trapezoidal filter
	tau: int,float
		the decay rate parameter for the trapezoidal filter
	pretrigger: int
		the length of the waveform to be used to average the baseline to 0
	batchsize: int
		how many waveforms to process at a time. Defaults to 1,000 but should be optimized on a per-computer basis. -1 means do all at once (warning this uses a lot of RAM)
	useGPU: bool
		Experimental feature allowing for the usage of a GPU through cupy. This isn't working yet.
	shift: int (defaults to 0)
		applies a shift to the extraction location for the energy from the trap filter
	hdf5ChunkSize: None
		don't use
	rechunk: bool (defaults to False)
		Use if you have applied multiple cuts to data and have enough RAM to load the whole dataset
		This will rechunk the data and make operations dramatically faster
	
	Returns
	-------
	energy: list
		list of floating point numbers that define the energies of the waveforms
	timing: list
		list of extracted start time of waveforms
	"""
	if waves.shape[0] == 0:
		return [], []
	else:
		if rechunk or type(waves)==np.ndarray:
			if rechunk and isinstance(waves, da.core.Array): #in the case it's dask
				waves = waves.compute()#load into ram
				waves = da.from_array(waves, chunks = {0: batchsize, 1:-1}) #then put back into dask for chunked operations
			elif isinstance(waves, np.ndarray):
				waves = da.from_array(waves, chunks = {0: batchsize, 1:-1})
		pretrigger = int(pretrigger)
		#this applies the trapezoidal filter to the waveforms and grabs the energy and timing results
		eners = []
		times = []
		#do the bulk wave preparation
		if batchsize == -1:
			batchsize = len(waves)
		numwaves = len(waves)
		leftover = numwaves % batchsize
		numbatches = int(numwaves / batchsize)
		#set up the main computations
		if useGPU == True and __gpuAvailable == True: #only try it when it's available and requested
			results = gpu.gpuTrapCuspFilterImplementation(waves, method='trap', rise=rise, top=top, tau=tau, percentage=percentage, pretrigger = pretrigger, shift = shift, mean = mean, batchsize = batchsize)
			return np.array(results.real), np.array(results.imag)
		else: #in this case just use the CPU
			#first define the filter itself
			filtLen = rise * 2 + top
			padLen = filtLen + waves.shape[1] - 1
			padLen = int(pow(2, np.ceil(np.log2(padLen)))) #pad to be the next power of 2, cause it's faster
			filt = defineSingleTrap(rise, top, tau, padLen)
			if waves.dtype != np.float32:
				waves = wavePrep(waves)
			if __fftwAvailable and useFFTW: #if both it's available and the user requests to use it
				#now pad the array to be the right length
				fftFilt = np.transpose(np.fft.rfft(filt),None)
				results = da.map_blocks(pyFFTWExtraction, waves, pretrigger, fftFilt, padLen, extractTrapResults, [rise, top, percentage, shift, mean], batchsize = batchsize, dtype=np.float32).compute()
				return results[:,0], results[:,1]
			else:
				if type(waves) == np.ndarray: #if it's a numpy array, convert it to dask so we can do this in parallel nicely
					waves = da.asarray(waves)
				means = waves[:,0:pretrigger].mean(axis=1)
				shifted = da.subtract(waves, means[:,None])
				padded = da.zeros(shape=(waves.shape[0], padLen), dtype=np.float32, chunks= {0: waves.chunks[0], 1: -1})
				padded[:,:waves.shape[1]] = shifted[:,:]
				fftFilt = da.asarray(np.transpose(np.fft.rfft(filt),None))
				fftWaves = da.fft.rfft(padded, axis=1)
				multiplication = da.multiply(fftWaves, fftFilt)
				filtered = da.fft.irfft(multiplication, axis=1).real
				res = da.apply_along_axis(extractTrapResults, 1, filtered, rise, top, percentage, shift, mean).compute()
				eners = res[:,0]
				times = res[:,1]
		return np.array(eners), np.array(times)

def applyCuspFilter(waves, rise, top, tau, percentage = 0.8, mean = 0, shift = 0, pretrigger=800, batchsize = 1000, useGPU = False, hdf5ChunkSize = None, rechunk = False, useFFTW = True):
	"""
	This function applies the trapezoidal filter to a batch of waveforms and extracts energy and timing information with it. This version of the filter is defined via convolutions instead of the standard recursive method to improve performance in Python.
	For a description of the trapezoidal filter defined here, check this resource.
	Nuclear Instruments and Methods in Physics Research A353 (1994) 261-264
	https://deepblue.lib.umich.edu/bitstream/handle/2027.42/31113/0000009.pdf?sequence=1
	
	Parameters
	----------
	waves: np.ndarray
		a 2d numpy array with waveforms in it
	rise: int
		the risetime parameter for the trapezoidal filter
	top: int
		the flat top length of the trapezoidal filter
	tau: int,float
		the decay rate parameter for the trapezoidal filter
	pretrigger: int
		the length of the waveform to be used to average the baseline to 0
	batchsize: int
		how many waveforms to process at a time. Defaults to 1,000 but should be optimized on a per-computer basis. -1 means do all at once (warning this uses a lot of RAM)
	useGPU: bool
		Experimental feature allowing for the usage of a GPU through cupy. This isn't working yet.
	shift: int (defaults to 0)
		applies a shift to the extraction location for the energy from the trap filter
	hdf5ChunkSize: None
		don't use
	rechunk: bool (defaults to False)
		Use if you have applied multiple cuts to data and have enough RAM to load the whole dataset
		This will rechunk the data and make operations dramatically faster
	
	Returns
	-------
	energy: list
		list of floating point numbers that define the energies of the waveforms
	timing: list
		list of extracted start time of waveforms
	"""
	if waves.shape[0] == 0:
		return [], []
	else:
		if rechunk or type(waves)==np.ndarray:
			if rechunk and isinstance(waves, da.core.Array): #in the case it's dask
				waves = waves.compute()#load into ram
				waves = da.from_array(waves, chunks = {0: batchsize, 1:-1}) #then put back into dask for chunked operations
			elif isinstance(waves, np.ndarray):
				waves = da.from_array(waves, chunks = {0: batchsize, 1:-1})
		pretrigger = int(pretrigger)
		#this applies the trapezoidal filter to the waveforms and grabs the energy and timing results
		eners = []
		times = []
		#do the bulk wave preparation
		if batchsize == -1:
			batchsize = len(waves)
		numwaves = len(waves)
		leftover = numwaves % batchsize
		numbatches = int(numwaves / batchsize)
		#set up the main computations
		if useGPU == True and __gpuAvailable == True: #only try it when it's available and requested
			results = gpu.gpuTrapCuspFilterImplementation(waves, method='cusp', rise=rise, top=top, tau=tau, percentage=percentage, pretrigger = pretrigger, shift = shift, mean = mean, batchsize = batchsize)
			return np.array(results.real), np.array(results.imag)
		else: #in this case just use the CPU
			#first define the filter itself
			filtLen = rise * 2 + top
			padLen = filtLen + waves.shape[1] - 1
			padLen = int(pow(2, np.ceil(np.log2(padLen)))) #pad to be the next power of 2, cause it's faster
			filt = defineCuspFilter(rise, top, tau, padLen)
			if waves.dtype != np.float32:
				waves = wavePrep(waves)
			if __fftwAvailable and useFFTW: #if both it's available and the user requests to use it
				#now pad the array to be the right length
				fftFilt = np.transpose(np.fft.rfft(filt),None)
				results = da.map_blocks(pyFFTWExtraction, waves, pretrigger, fftFilt, padLen, extractCuspResults, [rise, top, percentage, shift, mean], batchsize = batchsize, dtype=np.float32).compute()
				return results[:,0], results[:,1]
			else:
				if type(waves) == np.ndarray: #if it's a numpy array, convert it to dask so we can do this in parallel nicely
					waves = da.asarray(waves)
				means = waves[:,0:pretrigger].mean(axis=1)
				shifted = da.subtract(waves, means[:,None])
				padded = da.zeros(shape=(waves.shape[0], padLen), dtype=np.float32, chunks= {0: waves.chunks[0], 1: -1})
				padded[:,:waves.shape[1]] = shifted[:,:]
				fftFilt = da.asarray(np.transpose(np.fft.rfft(filt),None))
				fftWaves = da.fft.rfft(padded, axis=1)
				multiplication = da.multiply(fftWaves, fftFilt)
				filtered = da.fft.irfft(multiplication, axis=1).real
				res = da.apply_along_axis(extractCuspResults, 1, filtered, rise, top, percentage, shift, mean).compute()
				eners = res[:,0]
				times = res[:,1]
		return np.array(eners), np.array(times)

def calculatePseudoInverse(a, weight = None):
	if a.ndim == 1: #in the case the input is just a vector
		length = len(a)
		if weight is None:
			scale = np.dot(a, a)
			out = np.zeros(len(a))
			for i in range(len(a)):
				if abs(a[i]) < 0.00000001:
					out[i] = 0
				else:
					out[i] = a[i]/scale
			return out
		else:
			w = None
			if weight.ndim == 1:
				w = np.zeros((length, length))
				for i in range(length):
					w[i,i] = weight[i]
			else:
				w = np.copy(weight)
			ATW = np.matmul(np.transpose(a), w)
			ATWA = np.matmul(ATW, a)
			ATWAInv = np.inverse(ATWA)
			inverse = np.matmul(ATWAInv, ATW)
			return inverse
	elif a.ndim == 2: #in this case it's a matrix
		if weight is None:
			return np.linalg.pinv(a)
		else:
			w = None
			if weight.ndim == 1:
				w = np.zeros((a, a))
				for i in range(length):
					w[i,i] = weight[i]
			else:
				w = np.copy(weight)
			ATW = np.matmul(np.transpose(a), w)
			ATWA = np.matmul(ATW, a)
			ATWAInv = np.inverse(ATWA)
			inverse = np.matmul(ATWAInv, ATW)
			return inverse
	else:
		print('Error: invalid input dimension, needs to be 1d or 2d')
		return None

def calcATWA(matrix, weight = None):
	if weight is None:
		return np.matmul(np.transpose(matrix), matrix)
	w = None
	if weight.ndim == 1:
		w = np.zeros((length, length))
		for i in range(length):
			w[i,i] = weight[i]
	else:
		w = np.copy(weight)
	return np.matmul(matrix, np.matmul(weight, matrix))

@numba.jit
def __pseudoFitPSDAlongAxis(waves, maxLocs, fitMatrix, pseudoInverse, filtert0, filterLength, searchRange, t0Weight, numIdeal, psdInverses, psdWeight, returnResiduals):
	shape = None
	if numIdeal > 1: #if there are multiple
		if returnResiduals:
			shape = (len(waves), pseudoInverse.shape[1]+3+pseudoInverse.shape[0])
		else:
			shape = (len(waves), pseudoInverse.shape[1]+3)
	else:
		if returnResiduals:
			shape = (len(waves), pseudoInverse.shape[1]+2+pseudoInverse.shape[0])
		else:
			shape = (len(waves), pseudoInverse.shape[1]+2)
	results = np.zeros(shape, dtype=np.float64)
	results[:] = np.nan #set all values to failure
	for w in range(len(waves)):
		res = results[w,:]
		wave = waves[w]
		maxLoc = maxLocs[w]
		fitRegionLeft = int(maxLoc - filterLength - searchRange)
		fitRegionRight = maxLoc + searchRange
		res = np.zeros(shape[1])
		if fitRegionLeft < 0 or fitRegionRight >= len(wave): #if the fitting failed to return something in the valid window, return np.nan for all values
			continue
		fitRegion = wave[maxLoc-filterLength - searchRange: maxLoc + searchRange]
		fitParameters = np.zeros((searchRange*2+1, pseudoInverse.shape[1]))
		minChi = np.inf
		minChiLoc = -1
		for i in range(searchRange * 2 + 1):#determine fit parameters, fitted wave, and chi squared in one loop
			for j in range(pseudoInverse.shape[1]): #fit parameters first
				fitParameters[i,j] = np.dot(pseudoInverse[:,j], fitRegion[i:filterLength+i])
			fittedWave = np.dot(fitMatrix, fitParameters[i,:])
			waveDiff = fitRegion[i:filterLength+i]-fittedWave
			chi = None
			if t0Weight is None:
				chi = np.sum(np.square(waveDiff))
			else:
				if t0Weight.ndim == 1:
					chi = np.dot(waveDiff, np.multiply(t0Weight, waveDiff))
				else:
					chi = np.dot(waveDiff, np.dot(t0Weight, waveDiff))
			if chi < minChi:
				minChi = chi
				minChiLoc = i
		t0 = maxLoc - filterLength + filtert0 - searchRange + minChiLoc
		#now with the best time figured out, grab the best fit parameters as well
		bestFitParameters = fitParameters[minChiLoc, :]
		#okay now we need to go through and do the psd on this if there is more than one template function
		if numIdeal > 1:
			#need to subtract the baseline functions from the best fit region
			bestFitRegion = fitRegion[minChiLoc:minChiLoc+filterLength]
			withoutBaseline = bestFitRegion - np.dot(fitMatrix[:,numIdeal:], bestFitParameters[numIdeal:])
			#with that removed, now go through and do the fitting just like we did before
			minPSDChi = np.inf
			minPSDChiLoc = -1
			for i in range(numIdeal):
				params = np.dot(psdInverses[i], withoutBaseline)
				waveDiff = withoutBaseline - np.multiply(fitMatrix[:,i], params)
				chi = None
				if psdWeight is None:
					chi = np.sum(np.square(waveDiff))
				else:
					if psdWeight.ndim == 1:
						chi = np.dot(waveDiff, np.multiply(psdWeight, waveDiff))
					else:
						chi = np.dot(waveDiff, np.dot(psdWeight, waveDiff))
				if chi < minPSDChi:
					minPSDChi = chi
					minPSDChiLoc = i
			res[:len(bestFitParameters)] = bestFitParameters
			res[-3]= t0
			res[-2] =  minChi/(filterLength - len(bestFitParameters))
			res[-1] = minPSDChiLoc
			results[w,:] = res[:]
		else:
			res[:len(bestFitParameters)] = bestFitParameters
			res[-2]= t0
			res[-1] = minChi/(filterLength - len(bestFitParameters))
			results[w,:] = res[:]
	return results

def __pseudoFitBlockFunction(waveforms, padLen, maxParameterFilterFFT, fitMatrix, pseudoInverse, filtert0, 
							 filterLength, searchRange, t0Weight, numIdeal, psdInverses, 
							 psdWeight, batchsize, returnResiduals = False):
	"""
	This is a more efficient form of the process using FFTW
	"""
	numWaves, waveformLength = waveforms.shape
	badRegionStart = fitMatrix.shape[0]
	badRegionStop = waveformLength - fitMatrix.shape[0]
	if batchsize <= 0 or batchsize >= numWaves:
		batchsize = numWaves
	numBatches = numWaves//batchsize
	if numWaves % batchsize != 0:
		numBatches += 1
	#prep the work environment for the stuff
	#create the buffers that'll be used for the FFTs
	filterLength = pseudoInverse.shape[0]
	padded = np.zeros(shape=(batchsize, padLen), dtype=np.float32)
	fftArray = np.zeros(shape=(batchsize, padLen//2+1), dtype=np.complex64)
	#create the FFT plans
	fftForward = pyfftw.FFTW(padded, fftArray, direction='FFTW_FORWARD', axes=[1])
	fftReverse = pyfftw.FFTW(fftArray, padded, direction='FFTW_BACKWARD', axes=[1])
	#create the results array 
	shape = np.zeros(2, dtype=int)
	shape[0] = len(waveforms)
	if numIdeal > 1: #if there are multiple
		if returnResiduals:
			shape[1] =  pseudoInverse.shape[1]+3+pseudoInverse.shape[0]
		else:
			shape[1] = pseudoInverse.shape[1]+3
	else:
		if returnResiduals:
			shape[1] = pseudoInverse.shape[1]+2+pseudoInverse.shape[0]
		else:
			shape[1] = pseudoInverse.shape[1]+2
	results = np.zeros(shape)
	for i in range(numBatches):
		padded[:,:] = 0
		startLoc = batchsize * i
		stopLoc = batchsize * (i+1)
		if stopLoc > numWaves:
			stopLoc = numWaves
		padded[:stopLoc-startLoc,:waveformLength] = waveforms[startLoc:stopLoc,:]
		#this time we don't have to subtract the baseline or anything like that
		#we can just do the normal thing and it'll work nicely
		fftForward() #do their FFT, now the FFT results are stored in the fftArray array
		fftArray *= maxParameterFilterFFT #do the multiplication in place or as in place as python allows
		fftReverse() #now undo the FFT back
		maxLocs = np.argmax(padded[:,badRegionStart:badRegionStop], axis=1)+badRegionStart
		results[startLoc:stopLoc] = __pseudoFitPSDAlongAxis(waveforms[startLoc:stopLoc,:].astype(np.float64, copy=False), maxLocs, fitMatrix, pseudoInverse, filtert0, filterLength, searchRange, t0Weight, numIdeal, psdInverses, psdWeight, returnResiduals)
	return results

def pseudoInverseFit(waves, templates, baselines, filtert0 = None, searchRange = 10, t0Weight = None, psdWeight = None, returnResiduals = False, rechunk = False, batchsize = 1000):
	'''
	This is the pseudoinverse fitting method based on an upcoming paper. Talk with David Mathews for
	details of it's implementation. This method fits a waveform with a series of template functions that the
	user provides to the code. Depending on the values provided, it returns different information to the user.
	
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
	#check the inputs to see if they make sense
	if waves.shape[0] == 0:
		return [], []
	else:
		if rechunk or type(waves)==np.ndarray:
			if rechunk and isinstance(waves, da.core.Array): #in the case it's dask
				waves = waves.compute()#load into ram
				waves = da.from_array(waves, chunks = {0: batchsize, 1:-1}) #then put back into dask for chunked operations
			elif isinstance(waves, np.ndarray):
				waves = da.from_array(waves, chunks = {0: batchsize, 1:-1})
		#do the bulk wave preparation
		if batchsize == -1:
			batchsize = len(waves)
		numwaves = len(waves)
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
		length = waves.shape[1]
		filterLength = templates.shape[1]
		filterLength = templates.shape[1]
		padLen = length + filterLength - 1
		padLen = int(pow(2, np.ceil(np.log2(padLen))))
		#first we need to figure out the fit matrix
		numIdeal = len(templates)
		numBaseline = len(baselines)
		fitMatrix = []
		for shape in templates:
			fitMatrix.append(shape)
		for shape in baselines:
			fitMatrix.append(shape)
		fitMatrix = np.asarray(fitMatrix)
		#now we need to calculate the psuedoinverse
		pseudoInverse = calculatePseudoInverse(fitMatrix, weight = t0Weight)
		#now do the same thing for the psd filters
		psdInverses = []
		for i in range(numIdeal):
			psdInverses.append(np.transpose(calculatePseudoInverse(templates[i], weight = psdWeight)))
		psdInverses = np.asarray(psdInverses)
		#first make the filter that determines the fit parameter maximum location as that is the fastest way
		maxParameterFilter = np.zeros(padLen) #full length of the waveforms for fft convolution
		maxParameterFilter[:pseudoInverse.shape[0]] = np.flip(np.mean(pseudoInverse[:, 0:numIdeal], axis=1)) #grab the mean of the inverse filters for each ideal template
		maxParameterFilterFFT = np.fft.rfft(maxParameterFilter) #do the fft of it to reduce computations later
		#now we know the region where the chi square minimum should approximately be, do the full process of finding fit parameters in this region now
		results = da.map_blocks(__pseudoFitBlockFunction, waves, padLen, maxParameterFilterFFT, fitMatrix.T, pseudoInverse, filtert0, filterLength, searchRange, t0Weight, numIdeal, psdInverses, psdWeight, batchsize, returnResiduals, dtype=np.float64).compute()
		gc.collect()
		if numIdeal > 1:
			bestParameters = results[:,:pseudoInverse.shape[1]]
			t0s = results[:,pseudoInverse.shape[1]]
			minChis = results[:,pseudoInverse.shape[1]+1]
			psdGuess = results[:,-1]
			return [bestParameters, t0s, minChis, psdGuess]
		else:
			bestParameters = results[:,:pseudoInverse.shape[1]]
			t0s = results[:,pseudoInverse.shape[1]]
			minChis = results[:,pseudoInverse.shape[1]+1]
			return [bestParameters, t0s, minChis, None]
		return [None, None, None, None]

@numba.jit
def __pseudoFitSubLoopTrapFilter(waves, maxLocs, fitMatrix, pseudoInverse, filtert0, filterLength, 
					 searchRange, t0Weight, numIdeal, trapFilter, rise, top, shift=0):
	results = []
	for i in range(len(waves)):
		wave = waves[i]
		maxLoc = maxLocs[i]
		#with this location in the output known, we can now search for the minimum chi squared
		fitRegionLeft = maxLoc - filterLength - searchRange
		fitRegionRight = maxLoc + searchRange
		res = None 
		#now figure out the shape of the output returned from this
		res = np.zeros(pseudoInverse.shape[1] + 3, dtype=np.float64) #energy, timing, chi, fit parameters
		res[:] = np.nan #set all of them to nan just in case the code fails
		if fitRegionLeft < 0 or fitRegionRight >= len(wave): #if the fitting failed to return something in the valid window, return np.nan
			results.append(res)
		else:
			fitRegion = wave[maxLoc-filterLength - searchRange: maxLoc + searchRange].astype(np.float64)
			fitParameters = np.zeros((searchRange*2+1, pseudoInverse.shape[1]), dtype=np.float64)
			minChi = np.inf
			minChiLoc = -1
			for i in range(searchRange * 2 + 1):#determine fit parameters, fitted wave, and chi squared in one loop
				for j in range(pseudoInverse.shape[1]): #fit parameters first
					fitParameters[i,j] = np.dot(pseudoInverse[:,j], fitRegion[i:filterLength+i])
				fittedWave = np.dot(fitMatrix, fitParameters[i,:])
				waveDiff = fitRegion[i:filterLength+i]-fittedWave
				chi = None
				if t0Weight is None:
					chi = np.sum(np.square(waveDiff))
				else:
					if t0Weight.ndim == 1:
						chi = np.dot(waveDiff, np.multiply(t0Weight, waveDiff))
					else:
						chi = np.dot(waveDiff, np.dot(t0Weight, waveDiff))
				if chi < minChi:
					minChi = chi
					minChiLoc = i
			t0 = maxLoc - filterLength + filtert0 - searchRange + minChiLoc
			#now with the best time figured out, grab the best fit parameters as well
			trapLen = len(trapFilter)
			startPos = int(t0 - trapLen + rise + top//2+shift) #take the halfway point on the trapezoid and then shift if desired
			if startPos < 0 or startPos + trapLen > len(wave): #make sure that this position actually makes sense
				results.append(res)
			else:
				bestFitParameters = fitParameters[minChiLoc, :]
				bestFitRegion = wave[startPos:startPos+trapLen].astype(np.float64)
				for i in range(numIdeal, fitMatrix.shape[1]):
					bestFitRegion -= fitMatrix[:trapLen,i] * bestFitParameters[i] #subtract off the baseline functions
				#using this, subtract off the baseline
				trapLen = len(trapFilter)
				startPos = int(t0 - trapLen + rise + top//2+shift) #take the halfway point on the trapezoid
				#now subtract the baselines and apply the trap filter
				energy = np.dot(bestFitRegion, trapFilter)
				out = [energy, t0, minChi]
				for param in bestFitParameters:
					out.append(param)
				results.append(np.array(out))
	return results

def __pyFFTWExtractionFitTrap(waveforms, fitFunctions, inverseMatrix, 
							maxParameterFilterFFT, padLen, numIdeal, trapFilter, rise, top,
							filtert0 = None, searchRange = 10, t0Weight = None,
							batchsize = -1, shift = 0, block_info = None):
	"""
	This is a more efficient form of convolution using the FFTW library. 
	It's more efficient than the standard numpy/scipy/dask implementations
	"""
	numWaves, waveformLength = waveforms.shape
	badRegionStart = fitFunctions.shape[1]
	badRegionStop = waveformLength - fitFunctions.shape[1]
	if batchsize <= 0 or batchsize >= numWaves:
		batchsize = numWaves
	numBatches = numWaves//batchsize
	if numWaves % batchsize != 0:
		numBatches += 1
	#prep the work environment for the stuff
	#create the buffers that'll be used for the FFTs
	filterLength = inverseMatrix.shape[0]
	padded = np.zeros(shape=(batchsize, padLen), dtype=np.float32)
	fftArray = np.zeros(shape=(batchsize, padLen//2+1), dtype=np.complex64)
	#create the FFT plans
	fftForward = pyfftw.FFTW(padded, fftArray, direction='FFTW_FORWARD', axes=[1])
	fftReverse = pyfftw.FFTW(fftArray, padded, direction='FFTW_BACKWARD', axes=[1])
	#create the results array 
	results = np.zeros(shape=(numWaves, 3 + len(fitFunctions)))
	fitFunctions = np.transpose(fitFunctions)
	for i in range(numBatches):
		padded[:,:] = 0
		startLoc = batchsize * i
		stopLoc = batchsize * (i+1)
		if stopLoc > numWaves:
			stopLoc = numWaves
		padded[:stopLoc-startLoc,:waveformLength] = waveforms[startLoc:stopLoc,:]
		#this time we don't have to subtract the baseline or anything like that
		#we can just do the normal thing and it'll work nicely
		fftForward() #do their FFT, now the FFT results are stored in the fftArray array
		fftArray *= maxParameterFilterFFT #do the multiplication in place or as in place as python allows
		fftReverse() #now undo the FFT back
		maxLocs = np.argmax(padded[:,badRegionStart:badRegionStop], axis=1)+badRegionStart
		results[startLoc:stopLoc] = __pseudoFitSubLoopTrapFilter(waveforms[startLoc:stopLoc,:], maxLocs, fitFunctions, inverseMatrix, filtert0, filterLength, searchRange, t0Weight, numIdeal, trapFilter, rise, top, shift=shift)
	return results

def pseudoInverseTrapFilter(waves, templates, baselines, rise, top, tau,
							percentage = 0.8, filtert0 = None, searchRange = 10, 
							t0Weight = None, shift = 0, batchsize = 1000):
	"""
	This is the pseudoinverse fitting method based on an upcoming paper similar to pseudoInverseFit barring
	
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
	rise: int
		the risetime parameter for the trapezoidal filter
	top: int
		the flat top length of the trapezoidal filter
	tau: int,float
		the decay rate parameter for the trapezoidal filter
	percentage: float (defaults to 0.8)
		The threshold cross percentage to search for in the trap filter
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
	batchsize: int (defaults to -1):
		The number of waveforms to be handled by each process at a time
	Returns
	-------
	If the fitting fails, all returned values for that waveform are np.nan
	results: np.ndarray (2d array, each column has different meaning)
		First column: energy
		Second column: timestamp
		Third column: chi squared value
		4th+: best fit parameters
	"""
	#check the inputs to see if they make sense
	if len(waves) == 0:
		return None
	else:
		if type(waves) == np.ndarray:
			waves = da.from_array(waves, chunks = {0: 'auto', 1: -1})
		if isinstance(templates, list):
			templates = np.asarray(templates)
		if isinstance(baselines, list):
			baselines = np.asarray(baselines)
		if filtert0 is None: #assume it's in the middle then
			filtert0 = templates.shape[1]/2
		length = waves.shape[1]
		filterLength = templates.shape[1]
		padLen = length + filterLength - 1
		padLen = int(pow(2, np.ceil(np.log2(padLen))))
		if filterLength-filtert0 < rise * 2 + top:
			print('invalid input parameters')
			print('trap filter must be shorter than the fit function length - t0 position')
			print(filterLength - filtert0, '!>', rise * 2 + top, rise, top, filtert0)
			return None
		#first we need to figure out the fit matrix
		numIdeal = len(templates)
		numBaseline = len(baselines)
		fitMatrix = []
		for shape in templates:
			fitMatrix.append(shape)
		for shape in baselines:
			fitMatrix.append(shape)
		fitMatrix = np.asarray(fitMatrix)
		#now we need to calculate the psuedoinverse
		pseudoInverse = calculatePseudoInverse(fitMatrix, weight = t0Weight)
		#first make the filter that determines the fit parameter maximum location as that is the fastest way
		maxParameterFilter = np.zeros(padLen) #full length of the waveforms for fft convolution
		maxParameterFilter[:pseudoInverse.shape[0]] = np.flip(np.mean(pseudoInverse[:, 0:numIdeal], axis=1)) #grab the mean of the inverse filters for each ideal template
		maxParameterFilterFFT = np.fft.rfft(maxParameterFilter) #do the fft of it to reduce computations later
		trapFilter = defineSingleTrap(rise, top, tau, rise * 2 + top)
		#flip this array around because that's how we'll be using it anyways
		trapFilter = np.flip(trapFilter)
		#okay now each of these things are defined, should be "easy" to split the workload up
		#for now assume the FFTW method, we can work on that later
		results = da.map_blocks(__pyFFTWExtractionFitTrap, waves, fitMatrix, pseudoInverse, 
								maxParameterFilterFFT, padLen, len(templates), trapFilter, 
								rise, top, filtert0=filtert0, searchRange = searchRange, 
								t0Weight = t0Weight, batchsize = batchsize, dtype=np.float64, shift = shift)
		return results.compute()


@numba.jit
def doubleExpP0Est(x):
	offset = x[0:800].mean()
	amp = np.max(x)-offset
	t0 = np.argmax(x)
	decay1 = 1250.0
	decay2 = 10
	return [amp, t0, decay1, decay2, offset]

@numba.jit
def doubleExp(x, amp, t0, decay1, decay2, offset):
	"""
	This function defines a double exponential function that is often used for fitting waveforms
	
	Parameters
	----------
	x: np.ndarray
		the x coordinates of the dataset
	amp: int, float
		the amplitude of the function
	t0: int, float (if float it's rounded to nearest int)
		the start time of the signal, any values before are 0
	decay1: int, float
		the main decay constant of the waveform
	decay2: int, float
		the secondary decay constant of the waveform used to define the rising edge normally
	offset: int, float
		the baseline offset of the waveform
	
	Returns
	-------
	waveform: np.ndarray
		The waveform with those parameters
	"""
	out = np.zeros(len(x))
	out[:int(t0)] = offset
	decayRegion = x[int(t0):]-int(t0)
	out[int(t0):] = offset + amp * (np.exp(-decayRegion/decay1)-np.exp(-decayRegion/decay2))
	return out

@numba.jit
def waveSigmoidFunc(x, amp, t0, decay1, decay2, offset, linear):
	"""
	This function defines a double exponential function that is often used for fitting waveforms
	
	Parameters
	----------
	x: np.ndarray
		the x coordinates of the dataset
	amp: int, float
		the amplitude of the function
	t0: int, float (if float it's rounded to nearest int)
		the start time of the signal, any values before are 0
	decay1: int, float
		the main decay constant of the waveform
	decay2: int, float
		the secondary decay constant of the waveform used to define the rising edge normally
	offset: int, float
		the baseline offset of the waveform
	
	Returns
	-------
	waveform: np.ndarray
		The waveform with those parameters
	"""
	out = np.zeros(len(x))
	out[:int(t0)] = offset
	decayRegion = x[int(t0):]-int(t0)
	out[int(t0):] = offset + amp * (np.exp(-decayRegion/decay1)-np.exp(-decayRegion/decay2))
	return out

def extractRiseTimes(waveforms, low=0.1, high=0.1, smooth=None, pretrigger=800):
	"""
	This function extracts rise times from waveforms passed to it. his function does so by using threshold cross
	methods. If a fit method is desired, see the fitWaveforms function instead. 
	
	IMPORTANT NOTE: Risetimes from different methods are NOT necessarily equivalent. Do not assume they are.
	
	Parameters:
		waves: np.ndarray
			the waveforms to be processed. Expects 2d array of waveforms
		pretrigger: int
			the length of the pretrigger region to be averaged to 0
			Wants the actual pretrigger length set in the file
			Will average up to the 80% point of this region to subtract the baseline
		params: list or None (defaults to None)
			If the method is 'default', this represents the threshold cross points
				Expects: if params[0] is provided, params[1] is provided 
					params[0] = lower threshold
					params[1] = upper threshold
			If the method is 'fit', these are fit parameters
				params[0]: length of the fit centered on pretrigger value
		smooth: np.ndarray, None (defaults to None)
			This defines a convolutional smoothing function to be applied to the waveforms
				before they are fit or passed through the default method
			Any arrays shorter than the waveform length will be padded with zeros
	Returns:
		A np.ndarray of the risetimes as calculated by the method chosen
	"""
	if waveforms is not None:
		if waves.shape[0] == 0:
			return None
		elif type(waveforms) == np.ndarray: #if it's a numpy array, convert it to dask so we can do this in parallel
			waveforms = da.asarray(waveforms)
		if smooth is not None:
			if len(smooth) < len(waveforms[0]):
				smooth.resize(len(waveforms[0]))
			elif len(smooth) > len(waveforms[0]):
				print('Error: smoothing function should be less than the length of the waveforms')
				return None
			else:
				smooth = da.transpose(da.fft.rfft(smooth),None)
		if low < 0 or low > high:
			print('invalid low parameter:', low, 'stopping execution')
			return None
		if high < low or high >=1:
			print('invalid high parameter:', high, 'stopping execution')
			return None
		numwaves = waves.shape[0]
		leftover = numwaves % batchsize
		numbatches = int(numwaves / batchsize)
		means = waveforms[:,0:pretrigger].mean(axis=1)
		shifted = da.subtract(waveforms, means[:,None])
		if smooth is not None:
			temp = da.fft.rfft(shifted, axis=1)
			temp = da.multiply(temp, smooth)
			shifted = da.fft.irfft(temp)
		@numba.jit
		def findCrossPoints(wave):
			maxval = np.max(wave)
			maxloc = np.argmax(wave)
			upperCross = maxval * upper
			lowerCross = maxval * lower
			upCrossPoint = None
			lowCrossPoint = None
			i = maxloc
			while upCrossPoint is None or lowCrossPoint is None:
				if wave[i] >= upperCross and wave[i-1] <= upperCross:
					upCrossPoint = i
				if wave[i] >= lowerCross and wave[i-1] <= lowerCross:
					lowCrossPoint = i
				i-=1
				if i <= 0:
					break
			if upCrossPoint is not None and lowCrossPoint is not None:
				return upCrossPoint - lowCrossPoint
			else:
				return np.nan
		res = da.apply_along_axis(findCrossPoints, 1, shifted).compute()
		return np.array(res)
	else: #no waveforms case
		return None

def gaussian(x, amp, mean, sigma, offset):
	"""
	This defines a gaussian function for fitting purposes
	
	Parameters
	----------
	x: np.ndarray
		the x coordinates of the array
	amp: int, float
		the amplitude of the function
	mean: int, float
		the mean value of the fit
	sigma: int, float
		the standard deviation of the function
	offset: int, float
		the baseline offset of the function
	
	Returns
	-------
	function: np.ndarray
		the gaussian function defined with those parameters
	"""
	return amp * np.exp(-1.0 * ((x-mean)/sigma)**2.0) + offset

#functions for fitting to a gaussian
def fitFunction(xdata, ydata, function = None, bounds = None, p0 = None):
	popt = None
	pcov = None
	if function is None:
		function = gaussian
	try:
		if bounds is None and p0 is None:
			popt, pcov = curve_fit(function, xdata, ydata)
		elif bounds is not None and p0 is None:
			popt, pcov = curve_fit(function, xdata, ydata, bounds = bounds)
		elif bounds is None and p0 is not None:
			popt, pcov = curve_fit(function, xdata, ydata, p0=p0)
		elif bounds is not None and p0 is not None:
			popt, pcov = curve_fit(function, xdata, ydata, p0=p0)
	except Exception as e: 
		print('Fitting Failed:', e)
		return None, None
	return popt, pcov


@numba.jit
def expFit(x, amp, decay1, offset):
	"""
	This function defines a simple exponentially decaying function that is used for fitting the decay rate of waveforms
	
	Parameters
	----------
	x: np.ndarray
		the x coordinates of the dataset
	amp: int, float
		the amplitude of the function
	decay1: int, float
		the main decay constant of the waveform
	offset: int, float
		the baseline offset of the waveform
	
	Returns
	-------
	waveform: np.ndarray
		The waveform with those parameters
	"""
	out = amp * np.exp(-x/decay1) + offset
	return out

def extractDecayRateDaskBlocks(waves, start, stop, guessDecay):
	if waves.shape[0] == 0: #in the case of no waveforms
		return np.array([0], dtype=np.float32)
	else:
		results = []
		xdata = np.arange(stop-start)
		for i in range(waves.shape[0]):
			wave = waves[i][start:stop]
			res = None
			offset = np.min(wave)
			amp = np.max(wave)
			try:
				popt, pcov = curve_fit(expFit, xdata, wave, p0=[amp, guessDecay, offset], bounds = ((-16384, 0, -16383), (16384, 2000, 16383)))
				res = popt[1]
			except:
				res = np.nan
			results.append(res)
		return np.array(results, dtype=np.float32)

def extractDecayRate(waves, pretrigger = None, start=0, stop=-1, guess = 1250):
	"""
	This function is used to extract the decay rate of the waveforms.
	This parameter is primarily used for optimizing the trapezoidal and cusp filters.
	
	Parameters
	----------
	waves: np.ndarray
		the waveforms in a 2d array
	start: int (defaults to 0)
		the first location in the array to start the fit
	stop: int (defaults to -1)
		the last point in the waveform to fit
	guess: int/float (defaults to 1250)
		An initial guess at what the decay rate should be
	Returns
	-------
	decayRates: np.ndarray
		returns the decay rates in a np.ndarray
	"""
	if waves is not None:
		if type(waves) == np.ndarray:
			waves = da.from_array(waves, chunks = {0: 'auto', 1: -1})
		if stop == -1:
			stop = len(waves[0]) #get the length of the first waveform and use that
		results = da.map_blocks(extractDecayRateDaskBlocks, waves, start, stop, guess, dtype=np.float32, drop_axis=1).compute()
		return results
	else:
		return None

def fitWaveforms(waves, pretrigger, function = 'doubleExp', p0func = None, region = None, residuals = False, showErrs = True, **kwargs):
	"""
	This function fits the waveforms to a variety of functions and returns the fit parameters and covariance matrix.
	Parameters
	----------
	waves: np.ndarray or dask.array
		2d array of waveforms
	pretrigger: int
		The pretrigger offset defined in the waveform file
	function: str, function
		if str: 'doubleExp' for a difference of exponentials, see function Nab.bf.doubleExp
			'sigmoid': not defined yet
		if function:
			an arbitrarily defined function
	p0func: None, function
		If None, defaults to the standard behavior for the 'doubleExp' function
		If function, this function is called to find estimates for the initial fit parameters
	region: None, int, or np.ndarray
		The region to be fit
		If None: the whole waveform
		If int, a particular window around the pretrigger
		If np.ndarray: those particular x values
	residuals: bool, defaults to False
		Returns the residuals of the fit to the user as well
	showErrs: bool, defauls to True
		prints out the error messages from scipy curve_fit to the user if True
	
	Returns
	-------
	best fit parameters: np.ndarray
		The best fit parameters as find by scipy curve_fit for the given function
		These are in the order they are passed to the function
	covariance matrix: np.ndarray
		This is the covariance matrix for the fit parameters. Each row is the number of fit parameters
		squared in length due to them being flattened with np.ndarray.flatten() before being returned
	residuals: None or np.ndarray
		If residuals is True: returns the residuals of the best fit in a np.ndarray
		If residuals is False: returns None
	"""
	if waves is not None:
		if type(waves) == np.ndarray:
			waves = da.asarray(waves)
		fitFunc = None
		if callable(function):
			fitFunc = function
		else:
			if function == 'doubleExp':
				fitFunc = doubleExp
			else:
				print('unrecognized function input: expects either a function definition or "doubleExp"')
				return None
		xvals = None
		if region is None:
			xvals = np.arange(len(waves[0]))
		elif isinstance(region, int): #in this case we want a particular window around the pretrigger
			xvals = np.arange(region)
			xvals = pretrigger - int(region/2) + xvals[:]
		elif isinstance(region, np.ndarray):
			xvals = region.copy()
		else:
			print('unrecognized region input, expects None, int, or np.ndarray')
			return None
		numArgs = len(inspect.signature(fitFunc).parameters)-1
		if p0func is None:
			p0func = doubleExpP0Est
		def fitWave(wave, residuals = False, **kwargs):
			res = None
			if residuals == False:
				res = np.zeros(numArgs*(numArgs + 1))
			else:
				res = np.zeros(numArgs*(numArgs + 1) + len(wave))
			res[:] = np.nan
			p0 = p0func(wave)
			try:
				popt, pcov = curve_fit(fitFunc, xvals, wave, p0=p0, **kwargs)
				res[:numArgs] = popt[:]
				res[numArgs:numArgs*(numArgs + 1)] = pcov.flatten()
				if residuals:
					res[numArgs*(numArgs+1):] = wave - fitFunc(xvals, *popt)
			except Exception as e:
				if showErrs:
					print(e)
			return res
		results = da.apply_along_axis(fitWave, 1, waves[:,xvals], residuals=residuals, **kwargs).compute()
		if residuals:
			return results[:,:numArgs], results[:,numArgs:numArgs*(numArgs+1)], results[:,numArgs*(numArgs+1):]
		else:
			return results[:,:numArgs], results[:,numArgs:numArgs*(numArgs+1)], None

def generatePowerSpectra(waves):
	"""
	This function goes through and calculates the power spectra of a series of waveforms.
	It does this using the scipy signal periodogram function with scaling='specrum'
	
	Parameters
	----------
	waves: np.ndarray
		just a big 2d array of waveforms
	
	Returns
	-------
	frequencies: np.ndarray
		the frequency bins of the output
	amplitude: np.ndarray
		the amplitude of the power spectrum in each bin
	"""
	res = signal.periodogram(waves, 250E6, axis=1, scaling='spectrum')
	return res[0], np.mean(res[1], axis=0)

def averageWaveforms(waves, pretrigger = None, shifts = None):
	"""
	This function averages the waveforms that are passed to it
	
	Parameters
	----------
	waves: np.ndarray
		a 2d array of waveforms
	pretrigger: int, defaults to None
		the length of the waveform to average the baseline out
	shifts: np.ndarray
		the value to shift each waveform by to align them
	Returns
	-------
	average: np.ndarray
		the averaged waveform shape
	"""
	if waves is None:
		return None
	else:
		#check to make sure the waveforms are the right data type
		if type(waves) == np.ndarray:
			waves = da.asarray(waves)
		if shifts is not None:
			if len(waves) != len(shifts):
				print('Error: len(shifts) must equal len(waves)')
				return None
		if pretrigger is None and shifts is None: #both are none, just do a straight average
			return np.mean(waves, axis=0).compute()
		elif pretrigger is not None and shifts is None: #in this case we want to zero the baseline, but still no alignment
			means = np.mean(waves[:,:pretrigger], axis=1)
			return np.mean((waves.T-means).T, axis=0).compute()
		elif pretrigger is None and shifts is not None: #don't zero the baseline, but align the t0s
			#queue up the tasks using dask delayed, then actually do them
			out = []
			for i in range(len(waves)):
				out.append(delayed(np.roll(waves[i], int(shifts[i]))))
			#this line applies the shifts, converts results to matrix, and calculates the mean ignoring nans
			return da.nanmean(da.asarray(compute(*out)), axis=0).compute()
		else: #both zero the baseline and then align the t0s
			#again queue up using dask delayed, then actually do them
			means = np.mean(waves[:,:pretrigger], axis=1)
			zeroed = (waves.T-means).T
			#now align these waveforms
			out = []
			for i in range(len(zeroed)):
				if shifts[i] is None:
					temp = np.zeros(len(zeroed[i]))
					temp[:] = np.nan
					out.append(delayed(temp))
				elif np.isnan(shifts[i]):
					temp = np.zeros(len(zeroed[i]))
					temp[:] = np.nan
					out.append(delayed(temp))
				else:
					out.append(delayed(np.roll(zeroed[i], int(shifts[i]))))
			#this line applies the shifts, converts results to matrix, and calculates the mean ignoring nans
			return da.nanmean(da.asarray(compute(*out)), axis=0).compute()


#cutting routines for the different classes here
def basicCuts(data, category, operator, optionA):
	"""
	Standard cutting operations. Allows the user to apply basic cuts to the dataset
	
	Parameters:
	-----------
		data: np.ndarray with named elements
			the input dataset to apply cuts to
		category: str
			the named part of the dataset to compare to the value to be cut on
		operator: str
			the cut operation: options are '>', '>=', '<', '<=', '=', '==', '!=', 'or'
		optionA: int, float, list(only in case of 'or' operation)
			the value to cut based on
	Returns:
	--------
		returns a np.ndarray boolean mask for the input dataset that applies the cut
			Does not return a modified version of the dataset to preserver original data
	"""
	cut = None
	if operator == '>':
		cut = (data[category] > optionA).values
	elif operator == '>=':
		cut = (data[category] >= optionA).values
	elif operator == '<':
		cut = (data[category] < optionA).values
	elif operator == '<=':
		cut = (data[category] <= optionA).values
	elif operator == '=' or operator == '==':
		cut = (data[category] == optionA).values
	elif operator == '!=':
		cut = (data[category] != optionA).values
	elif operator == 'or':
		#in this case we need to iterate over the options provided in the list
		cut = np.zeros(len(data), dtype=bool)
		for a in optionA: #this is a list of values
			cut = np.logical_or(cut, (data[category] == a).values)
	else:
		print('Improper operator passed to basicCuts: no cut applied')
		return np.ones(len(data), dtype=bool)
	return cut

def twoComparisonCut(data, category, operator, lower, upper):
	"""
	Cut operations that depend on having an upper and lower value being passed to them.
	
	Parameters:
	-----------
		data: np.ndarray with named elements
			the input dataset to apply cuts to
		category: str
			the named part of the dataset to compare to the value to be cut on
		operator: str
			the cut operation: options are 'between', 'outside'
		lower: int, float
			the lower value in the comparison
		upper: int, float
			the upper value of the comparison
	
	Returns:
	--------
		returns a np.ndarray boolean mask for the input dataset that applies the cut
			Does not return a modified version of the dataset to preserve original data
	"""
	if operator == 'between':
		cut = basicCuts(data, category, '>=', lower)
		cut2 = basicCuts(data, category, '<=', upper) 
		return np.logical_and(cut, cut2)
	elif operator == 'outside':
		cut = basicCuts(data, category, '<=', lower)
		cut2 = basicCuts(data, category, '>=', upper)
		return np.logical_or(cut, cut2)
	else:
		print('Improper operator passed to twoComparisonCut: no cut applied')
		return np.ones(len(data), dtype=bool)

def sortDataset(data, category):
	"""
	This function returns a mask that sorts the dataset when applied.
	Effectively this runs np.argsort on the dataset
	
	Parameters:
	-----------
		data: np.ndarray with named elements
			the input dataset to apply cuts to
		category: str
			The category to sort the data based on
	
	Returns:
	--------
		returns a np.ndarray mask that sorts the data that was passed in when applied
	"""
	return np.argsort(data[category])


def coincidenceCut(data, category, duration):
	"""
	This function cuts data that didn't occur within a certain time period of another piece of data. It's basically the inverse of the antiCoincidenceCut function.
	Technically any parameter can be expected, but it is meant to be used with the timestamp containers
	
	Note for reliable behavior, the data must be sorted along the category that is being used in this dataset first.
	
	Parameters:
	-----------
		data: np.ndarray with named elements
			the input dataset to apply cuts to
		category: str
			The category to apply this cut based on. Usually this is timestamp
		duration: int, float
			The time period, in units of whatever category (for timestamp this is 4ns timebins), that concurrent data must occur within
	
	Returns:
	--------
		returns a np.ndarray mask for the input data that applies the cut
			Does not return a modified version of the dataset to preserve original data
	"""
	cutCat = data[category].values
	#different shifts of the original data
	t1, t2, t3 = cutCat[:-2], cutCat[1:-1], cutCat[2:]
	#defines the truth array
	cut = (t2 - t1 >= duration) & (t3 - t2 >= duration)
	#now this will remove the values that we want to keep so we need to flip it
	cut = np.logical_not(cut)
	#or this with the whole false array to make it the proper length for the data set
	out = np.zeros(len(cutCat), dtype=bool) #big array of false
	out[1:-1] = out[1:-1] | cut #or with that array
	return out

def antiCoincidenceCut(data, category, duration):
	"""
	This function cuts data that did occur within a certain time period of another piece of data. It's basically the inverse of the coincidenceCut function.
	Technically any parameter can be expected, but it is meant to be used with the timestamp containers
	
	Note for reliable behavior, the data must be sorted along the category that is being used in this dataset first.
	
	Parameters:
	-----------
		data: np.ndarray with named elements
			the input dataset to apply cuts to
		category: str
			The category to apply this cut based on. Usually this is timestamp
		duration: int, float
			The time period, in units of whatever category (for timestamp this is 4ns timebins), that concurrent data must occur within
	
	Returns:
	--------
		returns a np.ndarray mask for the input data that applies the cut
			Does not return a modified version of the dataset to preserve original data
	"""
	cutCat = data[category].values
	#different shifts of the original data
	t1, t2, t3 = cutCat[:-2], cutCat[1:-1], cutCat[2:]
	#defines the truth array
	cut = (t2 - t1 >= duration) & (t3 - t2 >= duration)
	#or this with the whole false array to make it the proper length for the data set
	out = np.zeros(len(cutCat), dtype=bool) #big array of false
	out[1:-1] = out[1:-1] | cut #or with that array
	return out

@numba.jit
def optimizedCorruptionCheck(timestamps, reqs, boards):
	outputIndices = np.zeros(len(timestamps), dtype=np.bool_)
	outputIndices[:] = True
	sortTimestamps = np.argsort(timestamps) #the indices that sort the timestamps
	sortedDataset = np.zeros((3, len(timestamps)), dtype=np.uint64)
	sortedDataset[0,:] = timestamps[sortTimestamps]
	sortedDataset[1,:] = reqs[sortTimestamps]
	sortedDataset[2,:] = boards[sortTimestamps]
	length = len(timestamps)
	#this is a dataset that is sorted based on the timestamp now
	unsortTimestamps = np.argsort(sortTimestamps) #the indices that undo the sorting
	for i in range(len(timestamps)):#iterate over the timestamps in the sorted dataset
		timestamp = sortedDataset[0,i]
		board = sortedDataset[2,i]
		#now check the neighbor request times to see if they are within the range or not
		shift = 1
		found = False
		#search stuff to the right in time
		for j in range(i+1, length):
			nextReq = sortedDataset[1,j]
			nextBoard = sortedDataset[2,j]
			if nextReq >= timestamp: #if next request is after the time
				diff = nextReq - timestamp
				if diff <= 18500:
					if board == nextBoard:
						found = True
						outputIndices[i] = False #means it was corrupted
						break
				else:
					break
			else:
				diff = timestamp - nextReq
				if diff <= 15000:
					if board == nextBoard:
						found = True
						outputIndices[i] = False #means it was corrupted
						break
				else:
					break
		if not found:
			for j in range(i-1, -1, -1): #now iterate to the left
				nextReq = sortedDataset[1,j]
				nextBoard = sortedDataset[2,j]
				if nextReq >= timestamp: #if next request is after the time
					diff = nextReq - timestamp
					if diff <= 18500:
						if board == nextBoard:
							found = True
							outputIndices[i] = False #means it was corrupted
							break
					else:
						break
				else:
					diff = timestamp - nextReq
					if diff <= 15000:
						if board == nextBoard:
							found = True
							outputIndices[i] = False #means it was corrupted
							break
					else:
						break
	return outputIndices[unsortTimestamps]

def defineCut(data, category, operator=None, optionA = None, optionB = None):
		"""
		This function defines a cut to apply to the dataset. 
		You can only cut on data available in the headers
		
		Parameters
		----------
		data: dask.DataFrame
			the DataFrame that contains the dataset
		category : str
			the category to cut on. Must be a category in the waveform header
			To check available categories, call yourWaveformFile.headerType
			Also available categories:
				'pixel': requires a pixel map to be defined in the class
				'custom': unique operation that allows the user to pass a custom map of 
					the data to request instead of determining the map within the class
					This changes the behavior of operator
				'ca45Corruption': cut that is based on the conditions Noah described in his thesis.
					This removes the corruption issues from that version of the DAQ.
					Returns a dataset sorted by timestamp.
		operator: str, np.ndarray
			The operation to be applied to that category
			Supported options: >, >=, <, <=, ==, !=, between, outside, coincidence, anti-coincidence, or
			If category='custom', then this expects a np.ndarray to be used as the mask
		optionA: int,float,list[int,float]
			This is the first option being passed for the cut.
			For option(s) >, >=, <, <=, ==, !=: int,float. this is the value they are being compared to
			For option(s) between, outside, coincidence: int,float. this is the lower value
			For option(s) or: list[int,float]. this is a list of allowed values for that category
		optionB: int,float
			This is the second option passed for the cut. It is expected to be the upper value
			For option(s) between, outside: this is the upper value
		Returns
		--------
			This returns the indices in the dataset that "survive" the cut. 
			In the case of invalid input, the operation doesn't apply a cut.
		"""
		#the way this function works is that it operates on the portion of the dataset remaining
		#it looks at that portion that is left, and then checks to see if it passes the cut condition
		#it returns a numpy array with the locations that passed in terms of the positions in the index array
		#that pass the cut
		cut = None
		if category in data.dtypes.index.values:
			if operator in ['>', '>=', '<', '<=', '=', '==', '!=', 'or']:
				cut = basicCuts(data, category, operator, optionA)
			elif operator in ['between', 'outside']: #two comparison operations
				cut = twoComparisonCut(data, category, operator, optionA, optionB)
			elif operator == 'antiCoincidence' or operator == 'anti-coincidence': #the inverse coincidence operator
				cut = antiCoincidenceCut(data, category, optionA)
			elif operator == 'coincidence': #regular coincidence operator
				cut = coincidenceCut(data, category, optionA)
			elif operator == 'sort':
				cut = sortDataset(data, category)
			else:
				print('This operation is not recognized by the resultFile class')
		elif category == 'pixel': #this only goes off if the pixel name isn't in the dataframe so it's an error
			print('Need to provide a pixel map to the class. Use .definePixelMap()')
		elif category == 'custom':
			#this particular case is returned early because it's special and different
			#expects an array of the indexes that should be allowed through
			cut = data.loc[operator].index.values
			return cut
		elif category == 'ca45Corruption':
			#this cut is for the ca45 dataset, it removes corruption based on the headers
			#it needs the data to be sorted based on timestamp
			sortIndices = defineCut(data, 'timestamp', 'sort')
			timestamps = data['timestamp'].to_numpy()[sortIndices]
			reqs = data['req'].to_numpy()[sortIndices]
			boards = data['board'].to_numpy()[sortIndices]
			cut = optimizedCorruptionCheck(timestamps, reqs, boards)
			cut = np.sort(sortIndices[cut])
		else: #category is not in the list or bc
			print(category)
			print('Category not included in this data type. Check .names for eligible categories')
		if cut is not None: #these "cuts" are numpy arrays that basically operate on the current indices array
			currentIndices = data.index.values
			return currentIndices[cut]
		else: #in case of nothing being calculated so far
			return data.index.values

def plotOneDetector(values, numDet = 1, cmap = 'cividis', size = 3, showNum = True, showVal = True, alpha=1, rounding = None, title = None, norm = None, forceMin = None, forceMax = None, labels=None, filename = None, saveDontShow = False): #this is a simple function that plots values over each pixel
	fig, ax = plt.subplots(1, figsize=(size * 7 + size, size * 7), constrained_layout = True)
	ax.set_xlim(-size * 13, size * 13)
	ax.set_ylim(-size * 13, size * 13)
	cm = plt.get_cmap(cmap)
	cNorm = None
	minval = np.min(values)
	maxval = np.max(values)
	if forceMin is not None:
		minval = forceMin
	elif norm == 'log':
		if minval <= 0:
			minval = 0.01
	if forceMax is not None:
		maxval = forceMax
	if norm is None:
		cNorm = colors.Normalize(minval, maxval)
	elif norm == 'log':
		cNorm = colors.LogNorm(minval, maxval)
	else:
		print('unrecognized normalization option: needs to be log or not set')
		return
	scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
	vertOffset = size * np.sqrt(3)
	horOffset = size * 1.5
	colEnd = [7, 15, 24, 34, 45, 57, 70, 82, 93, 103, 112, 120, 127]
	colStart = [1, 8, 16, 25, 35, 46, 58, 71, 83, 94, 104, 113, 121]
	colLen = list(np.array(colEnd) - np.array(colStart) + 1)
	numCol = len(colEnd)
	for pixel in range(1, len(values)+1):
		col = 0
		for j in range(len(colEnd)):
			if pixel >= colStart[j] and pixel <= colEnd[j]:
				col = j
		numInCol = pixel - colStart[col] #number in the column from the top of the column
		horPosition = (col - numCol/2)*horOffset
		topOfCol = colLen[col]/2*vertOffset - vertOffset/2
		verPosition = topOfCol - vertOffset*numInCol
		hex = patches.RegularPolygon((horPosition, verPosition), numVertices=6, radius=size, facecolor=scalarMap.to_rgba(values[pixel-1]), orientation=np.pi/2, alpha = alpha, edgecolor='black')
		ax.add_patch(hex)
		txt = ''
		if showNum == True:
			txt += str(pixel)
		if labels is not None:
			if txt != '':
				txt += '\n'
			txt += str(labels[pixel-1])
		if showVal:
			if txt != '':
				txt += '\n'
			if rounding is not None:
				if rounding == 'int':
					txt += str(int(values[pixel-1]))
				else:
					txt += str(round(values[pixel-1], rounding))
		if txt!='':
			ax.text(horPosition-size/2, verPosition, txt, ma='center', va='center')
	#axColor = plt.axes([size*6, size*-6, size, size*])
	#plt.colorbar(scalarMap, cax = axColor, orientation="vertical")
	fig.colorbar(scalarMap, ax=ax)
	plt.axis('off')
	if title is not None:
		plt.title(title)
	if filename is not None:
		plt.savefig(filename)
		if saveDontShow == True:
			plt.clf()
			return
	else:
		if saveDontShow == True:
			print('need to pass a name if you want to save the file')
			plt.clf()
			return
		plt.show()
		return
	return

def makeHitsOverTimeGif(timestamps, hitlocations, outputname, batchsize = None, units = 'daq', cumulative = False, cmap = 'cividis', size = 3, showNum = True, showVal = True, alpha=1, rounding = None, norm = None, forceMin = None, labels=None, duration = 300):
	#this function basically does the same thing as plot one detector but it goes through and does it by saving the output of that function to .pngs and combining them into a .gif
	#it expects the hit locations to be passed as the actual pixel hit values not the board and channel
	startTime = np.min(timestamps)
	steps = None
	numSteps = None
	if batchsize is None:
		#default value of 10 batches basically
		numSteps = 10
		stopTime = np.max(timestamps)
		stepSize = (stopTime - startTime)/10.0
		steps = []
		for i in range(numSteps):
			steps.append(startTime + i * stepSize)
	else:
		if isinstance(batchsize, str): #parse the batches this way
			#if this is the case, then the last value is supposed to be the indicator of the unit
			unit = batchsize[-1]
			number = int(batchsize[:-1])
			#with this information, convert things into seconds
			if unit == 's':
				stepSize = number
			elif unit == 'm':
				stepSize = 60.0*number
			elif unit == 'h':
				stepSize = 3600.0*number
			else:
				print('unrecognized unit of time')
				print('expects s, m, or h')
				return None
			#check the units on the timestamps
			if units == 'daq':
				stepSize = stepSize / (4.0E-9)
			elif units == 's':
				stepSize = stepSize
			numSteps = int((np.max(timestamps)-startTime)/stepSize)
			steps = []
			for i in range(numSteps):
				steps.append(startTime + i * stepSize)
		elif isinstance(batchsize, int): #want this many batches
			stopTime = np.max(timestamps)
			stepSize = (stopTime - startTime)/batchsize
			steps = []
			for i in range(batchsize):
				steps.append(startTime + i * stepSize)
		elif isinstance(batchsize, (list, np.ndarray)): #provided the regions
			steps = list(batchsize)
		else:
			print('unsupported batchsize argument')
			print('expects intu (u is unit of s, m, or h), integer, list, or 1d np.ndarray')
			return None
	numSteps = len(steps)
	batches = []
	if numSteps - 1 == 0:
		batches.append(np.histogram(hitvals, np.arange(1, 128))[0])
	else:
		for i in range(numSteps-1):
			hitvals = None
			if cumulative:
				hitvals = hitlocations[np.less(timestamps, steps[i+1])]
			else:
				hitvals = hitlocations[np.logical_and(np.greater_equal(timestamps, steps[i]), np.less(timestamps, steps[i+1]))]
			batch = np.histogram(hitvals, np.arange(1, 129))[0]
			batches.append(batch)
	#now that the histograms are prepared, need to do the actual plotting
	batches = np.array(batches)
	minVal = np.min(batches)
	maxVal = np.max(batches)
	if forceMin is not None:
		minVal = forceMin
	#make a temporary directory for the animation
	tempdir = tempfile.TemporaryDirectory()
	frames = []
	for i in tqdm(range(len(batches))):
		title = 'Frame '+str(i)+' out of '+str(len(steps))
		filename = os.path.join(tempdir.name, str(i)+'.png')
		plotOneDetector(batches[i], numDet = 1, cmap = cmap, size = size, showNum = showNum, showVal = showVal, alpha=alpha, rounding = rounding, title = title, norm = norm, forceMin = minVal, forceMax = maxVal, labels=labels, filename = filename, saveDontShow = True)
		plt.close()
		frames.append(Image.open(filename))
	frames[0].save(outputname, format='GIF', append_images=frames[1:], save_all=True, duration=duration, loop=0)
	tempdir.cleanup()
