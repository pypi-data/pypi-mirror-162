'''
This file contains the various functions defined for the explicit purposes of replaying the data from the DAQ.

The idea is that these are called directly after the data is written from the Windows Fast-DAQ.
Then the output from these scripts is actually what pyNab expects to handle. 
'''
#standard python imports
import numpy as np
import h5py #used for file reading/writing
import os #used for directory and file functions
import time #used for sleep function
import gc
import shutil
from numba import jit
import glob

#custom code imports
from . import basicFunctions as bf
from . import fileFormats as ff

__compressionAvailable = False
try:
	import nabCompression.h5
	__compressionAvailable = True
except Exception as e:
    __compressionAvailable = False

def getHeaderType(dataIn):
	output = None
	if len(dataIn) != 0:
		dtype = dataIn.dtype
		if dtype == 'uint16':
			header = [('bc', 'u1')]
			header.append(('result', 'u1'))
			header.append(('timestamp', 'u8'))
			header.append(('req', 'u8'))
			header.append(('hit type', 'u1'))
			header.append(('event type', 'u1'))
			header.append(('blank', 'u2'))
			header.append(('eventid', 'u4'))
			shape = dataIn.shape
			if len(shape) == 1:
				waveformLength = int(shape[0]-13)
			else:
				waveformLength = int(shape[1]-13)
			waveform = str(waveformLength)+'u2'
			return np.dtype(header), waveform, True
		else:
			headerType = []
			for name in dtype.names[:-1]:
				headerType.append((name, dtype[name]))
			return np.dtype(headerType), None, False
	else:
		return None

def convertWaveformType(dataIn):
	output = None
	if len(dataIn) != 0:
		headerType, waveformType, flat = getHeaderType(dataIn)
		if flat == True: #in this case we are dealing with the flattened structure so use numpy.view to parse it all
			outType = np.dtype([('header', headerType), ('waveform', waveformType)])
			return dataIn.view(outType)
		else:
			headerType = getHeaderType(dataIn)
			outType = [('header', headerType)]
			outType.append(('waveform', str(len(dataIn[0]['waveform']))+'h'))
			output = np.zeros(len(dataIn), dtype=outType)
			for name in headerType.names:
				output['header'][name][:] = dataIn[name]
			temp = np.vstack(dataIn['waveform']) #stack all the waveform data together, this loads it in nicely
			del dataIn
			gc.collect()
			temp[:] = bf.doAnd(temp) #do the 16 bit conversion process
			gc.collect()
			output['waveform'][:] = temp.astype(np.int16)
			del temp
			gc.collect()
	return output

@jit
def separateWaveformTypes(file, headertype):
	#this function is passed an array of unsigned short values
	curloc = 0
	headerlength = 13
	stoploc = len(file)
	#setup the output containers
	singles = []
	singlesChecksums = []
	coincidences = []
	coincidencesChecksums = []
	pulsers = []
	pulsersChecksums = []
	baselines = []
	baselinesChecksums = []
	cosmics = []
	cosmicsChecksums = []
	while curloc < stoploc:
		#first grab the length of the waveform
		length = file[curloc] - 13
		#step past that
		curloc += 1
		#now this is the header itself
		header = file[curloc:curloc+headerlength].view(headertype)[0]
		#check what type of waveform it is and depending on that send it somewhere else
		#at this stage the headers and waveforms have not been modified, just sent somewhere
		eventType = header['event type']
		tempWaveform = bf.doAnd(file[curloc+headerlength:curloc+length+headerlength])
		checksum = bf.Fletcher32(tempWaveform.view(np.uint16))
		if eventType == 0:
			singles.append(file[curloc:curloc+length+headerlength])
			singlesChecksums.append(checksum)
		elif header['event type'] == 1:
			coincidences.append(file[curloc:curloc+length+headerlength])
			coincidencesChecksums.append(checksum)
		elif header['event type'] == 2:
			pulsers.append(file[curloc:curloc+length+headerlength])
			pulsersChecksums.append(checksum)
		elif header['event type'] == 3:
			baselines.append(file[curloc:curloc+length+headerlength])
			baselinesChecksums.append(checksum)
		elif header['event type'] == 4:
			cosmics.append(file[curloc:curloc+length+headerlength])
			cosmicsChecksums.append(checksum)
		curloc += length + headerlength
	return singles, singlesChecksums, coincidences, coincidencesChecksums, pulsers, pulsersChecksums, baselines, baselinesChecksums, cosmics, cosmicsChecksums

def parseFile(filename, headertype):
	file = np.fromfile(filename, dtype=np.uint16)
	singles, singlesChecksums, coincidences, coincidencesChecksums, pulsers, pulsersChecksums, baselines, baselinesChecksums, cosmics, cosmcsChecksums = separateWaveformTypes(file, headertype)
	if len(singles) > 0:
		singles = np.asarray(singles)
		singlesChecksums = np.asarray(singlesChecksums).astype(np.uint32)
	else:
		singles = None
		singlesChecksums = None
	if len(coincidences) > 0:
		coincidences = np.asarray(coincidences)
		coincidencesChecksums = np.asarray(coincidencesChecksums).astype(np.uint32)
	else:
		coincidences = None
		coincidencesChecksums = None
	if len(pulsers) > 0:
		pulsers = np.asarray(pulsers)
		pulsersChecksums = np.asarray(pulsersChecksums).astype(np.uint32)
	else:
		pulsers = None
		pulsersChecksums = None
	if len(baselines) > 0:
		baselines = np.asarray(baselines)
		baselinesChecksums = np.asarray(baselinesChecksums).astype(np.uint32)
	else:
		baselines = None
		baselinesChecksums = None
	if len(cosmics) > 0:
		cosmics = np.asarray(cosmics)
		cosmicsChecksums = np.asarray(cosmicsChecksums).astype(np.uint32)
	else:
		cosmics = None
		cosmicsChecksums = None
	del file
	return singles, singlesChecksums, coincidences, coincidencesChecksums, pulsers, pulsersChecksums, baselines, baselinesChecksums, cosmics, cosmicsChecksums

def prepareDataset(init, checksums):
	'''
	This function needs to prepare the dataset for writing to HDF5
	Need to sort by the event id information first
	Then calculate the fletcher32 checksums for each value
	Then do the bitshift operation on the waveform data
	'''
	#first do the sorting of the dataset
	indices = np.argsort(init['header']['eventid'])
	newHeaderType = []
	for element in init['header'].dtype.descr:
		newHeaderType.append(element)
	newHeaderType.append(('checksum', 'u4'))
	newHeaders = np.zeros(len(indices), dtype=np.dtype(newHeaderType))
	for name in init['header'].dtype.names:
		newHeaders[name] = np.copy(init['header'][name][indices])
	newHeaders['checksum'] = np.copy(checksums[indices])
	waveforms = np.copy(bf.doAnd(init['wave'][indices]))
	del init
	del checksums
	del indices
	return newHeaders, waveforms

def parseWaveformFiles(directory, run, subrun, headertype):
	'''
	This function parses the input waveform files and creates arrays for each waveform type. 
	It does this in a way that allows for differing waveform lengths per event type
	'''
	files = glob.glob(directory+'Run'+str(run)+'_'+str(subrun)+'RIO*.wave')
	singles = []
	singlesChecksums = []
	coincidences = []
	coincidencesChecksums = []
	pulsers = []
	pulsersChecksums = []
	baselines = []
	baselinesChecksums = []
	cosmics = []
	cosmicsChecksums = []
	for file in files:
		s, sChecks, c, cChecks, p, pChecks, b, bChecks, cos, cosChecks = parseFile(file, headertype)
		if s is not None:
			singles.append(s)
			singlesChecksums.append(sChecks)
		if c is not None:
			coincidences.append(c)
			coincidencesChecksums.append(cChecks)
		if p is not None:
			pulsers.append(p)
			pulsersChecksums.append(pChecks)
		if b is not None:
			baselines.append(b)
			baselinesChecksums.append(bChecks)
		if cos is not None:
			cosmics.append(cos)
			cosmicsChecksums.append(cosChecks)
	#make singular arrays for each of these
	if len(singles) > 0:
		singles = np.concatenate(singles)
		singlesChecksums = np.concatenate(singlesChecksums)
		if singles.ndim == 2:
			wavelength = singles.shape[1] - 13
			dtype = ff.headWaveType(wavelength, 'Nab', 4)
			singles = singles.view(dtype)[:,0]
			singles = prepareDataset(singles, singlesChecksums)
		else:
			singles = None
	else:
		singles = None
	if len(coincidences) > 0:
		coincidences = np.concatenate(coincidences)
		coincidencesChecksums = np.concatenate(coincidencesChecksums)
		if coincidences.ndim == 2:
			wavelength = coincidences.shape[1] - 13
			dtype = ff.headWaveType(wavelength, 'Nab', 4)
			coincidences = coincidences.view(dtype)[:,0]
			coincidences = prepareDataset(coincidences, coincidencesChecksums)
		else:
			coincidences = None
	else:
		coincidences = None
	if len(pulsers) > 0:
		pulsers = np.concatenate(pulsers)
		pulsersChecksums = np.concatenate(pulsersChecksums)
		if pulsers.ndim == 2:
			wavelength = pulsers.shape[1] - 13
			dtype = ff.headWaveType(wavelength, 'Nab', 4)
			pulsers = pulsers.view(dtype)[:,0]
			pulsers = prepareDataset(pulsers, pulsersChecksums)
		else:
			pulsers = None
	else:
		pulsers = None
	if len(baselines) > 0:
		baselines = np.concatenate(baselines)
		baselinesChecksums = np.concatenate(baselinesChecksums)
		if baselines.ndim == 2:
			wavelength = baselines.shape[1] - 13
			dtype = ff.headWaveType(wavelength, 'Nab', 4)
			baselines = baselines.view(dtype)[:,0]
			baselines = prepareDataset(baselines, baselinesChecksums)
		else:
			baselines = None
	else:
		baselines = None
	if len(cosmics) > 0:
		cosmics = np.concatenate(cosmics)
		cosmicsChecksums = np.concatenate(cosmicsChecksums)
		if cosmics.ndim == 2:
			wavelength = cosmics.shape[1] - 13
			dtype = ff.headWaveType(wavelength, 'Nab', 4)
			cosmics = cosmics.view(dtype)[:,0]
			cosmics = prepareDataset(cosmics, cosmicsChecksums)
		else:
			cosmics = None
	else:
		cosmics = None
	return singles, coincidences, pulsers, baselines, cosmics

def replayWaveformsIntoHDF5(file, directory, run, subrun, compression = False):
	formatNumber = 4
	#open the HDF5 file first
	headertype = np.dtype(ff.headerType(fileFormat = 'Nab', formatNumber = formatNumber))
	#okay with the file opened, need to add in the waveform information
	waveforms = parseWaveformFiles(directory, run, subrun, headertype)
	names = ['singles', 'coincidences', 'pulsers', 'baselines', 'cosmics']
	for name, waves in zip(names, waveforms):
		if waves is None:
			file.create_dataset('waveforms/'+name+'/headers', data = h5py.Empty(headertype))
			file.create_dataset('waveforms/'+name+'/waveforms', data = h5py.Empty('int16'))
		else:
			if not compression:
				file.create_dataset('waveforms/'+name+'/headers', data = waves[0], fletcher32=True)
				file.create_dataset('waveforms/'+name+'/waveforms', data = waves[1], fletcher32=True)
	return

def handleDamagedEvents(testfile):
	"""
	This function is designed to parse the broken event structure that has since been fixed. 
	There was a bug in the DAQ that caused the long baseline trace event type and the
	temperature recording event type to have errors when accessed through HDF5. This function
	returns an array that if saved in the place of the original event data would solve the problem
	by patching the damaged events with fake trigger information.
	
	Parameters
	----------
	testfile: HDF5 file object
		The opened input file
		Assumes the events are in the 'events' dataset
	
	Returns
	-------
	events: np.ndarray
		A numpy.ndarray object containing all of the events after any "bad" events were fixed.
		"bad" events have fake trigger information put in them now to fix the file reading issues
	"""
	outEvents = []
	for i in range(len(testfile['events'])):
		try:
			outEvents.append(testfile['events'][i])
		except:
			print(i)
			#if that fails, the issue is that the triggers messed it up
			tempEvent = np.zeros(1, dtype=dtype)
			for field in list(dtype.fields)[:-2]:
				tempEvent[field] = testfile['events'][field][i]
			#now for the trigger
			tempEvent['number of triggers'] = 1
			fakeTrigger = np.zeros(1, dtype=triggertype)
			fakeTrigger['timestamp'] = testfile['events']['baseline timestamp'][i]
			tempEvent['triggers'] = fakeTrigger
			outEvents.append(tempEvent[0])
	outEvents = np.array(outEvents, dtype=dtype)
	return outEvents

def convertFileFormatFullDAQ(inputFileLocation, outputFileLocation, run, subrun, compression = False):
	"""
	This function is effectively the first step in the replay process. 
	It reads in the initial DAQ output file and makes some simple modifications to how the data is stored before outputting a new version of the file.
	
	These modifications are focused around how the waveforms are stored but some changes are done to the parameter information to make it easier to handle.
	
	Parameters
	------
	inputFileName: string
		the name and location of the input file
	
	outputFileName: string
		the name and location of the output file
	
	compression: bool (defaults to False)
		If this is set to True, and if the nabCompression.h5 libraries are available, then compression will be enabled for waveform data.
		Otherwise if either of those conditions aren't met, the waveform data will not be compressed.
	
	Returns
	-------
	None
	"""
	inputFileName = inputFileLocation + 'Run'+str(run)+'_'+str(subrun)+'.h5'
	outputFileName = outputFileLocation + 'Run'+str(run)+'_'+str(subrun)+'.h5'
	testIn = h5py.File(inputFileName, 'r')
	testOut = h5py.File(outputFileName, 'w')
	try:
		#first copy the FPGA temperature data over
		print('\t Starting FPGA Temperatures')
		if testIn['FPGATemperatures'].shape != 0: #if it's not empty, make this
			testOut.create_dataset('FPGATemperatures', data = testIn['FPGATemperatures'], fletcher32=True)
		gc.collect()
		#now copy the parameter information over
		print('\t Starting Parameters')
		for key in testIn['Parameters'].keys():
			gc.collect()
			datasetName = 'Parameters/'+key
			if key == 'RunSettings': #unpack these into an easier to parse form
				data = testIn[datasetName]
				for f in data.dtype.names:
					subname = datasetName + '/'+f
					testOut[subname] = testIn[datasetName][()][f]
				del data
			elif key == 'HardwareConfiguration': #unpack these into an easier to parse form
				group = testIn[datasetName]
				for k in group.keys():
					subname = datasetName + '/'+k
					testOut[subname] = group[k][()]
				del group
			else: #other ones are just fine how they are
				testOut[datasetName] = testIn[datasetName][()]
		print('\t Starting Triggers')
		#copy over the trigger information
		testOut.create_dataset('triggers', data = testIn['triggers'], fletcher32=True)
		gc.collect()
		#copy the event information over
		print('\t Starting Events')
		testOut.create_dataset('events', data = testIn['events'])
		gc.collect()
		testIn.close()
		print('\t Starting to parse the waveform data')
		replayWaveformsIntoHDF5(testOut, inputFileLocation, run, subrun, compression = compression)
		testOut.close()
		gc.collect()
		return 0
	except Exception as e:
		print('error during execution')
		print(e)
		testIn.close()
		testOut.close()
		return -1
	return 0

def verifyDataIntegrity(initialFile, finalFile):
	"""
	This function verifies that all the data was preserved during the replay process.
	It opens up the original file and the new file and confirms that all data matches
	
	Parameters
	------
	initialFile: string
		the name and location of the input file
	
	finalFile: string
		the name and location of the output file
	
	Returns
	-------
	result: int
		If result = 0: file matches and data is okay
		If result < 0: file doesn't match
			-1: FPGA temperature data doesn't match
			-2: Run Settings mismatch
			-3: Hardware Configuration Mismatch
			-4: Generical configuration parameter mismatch
			-5: Trigger data mismatch
			-6: Event data mismatch
			-7: Waveform data headers mismatch
			-8: Waveform data waveforms mismatch
			-9: Error during data quality check, assume problem
	"""
	testIn = h5py.File(initialFile, 'r')
	testOut = h5py.File(finalFile, 'r')
	try:
		#first copy the FPGA temperature data over
		if testIn['FPGATemperatures'].shape != 0: #if it's not empty, check this
			inp = testIn['FPGATemperatures'][()]
			out = testOut['FPGATemperatures'][()]
			if not np.array_equal(inp, out):
				return -1
			del inp
			del out
			gc.collect()
		#now copy the parameter information over
		for key in testIn['Parameters'].keys():
			datasetName = 'Parameters/'+key
			if key == 'RunSettings': #unpack these into an easier to parse form
				data = testIn[datasetName]
				for f in data.dtype.names:
					subname = datasetName + '/'+f
					if not np.array_equal(testOut[subname][()], testIn[datasetName][()][f]):
						return -2
			elif key == 'HardwareConfiguration': #unpack these into an easier to parse form
				group = testIn[datasetName]
				for k in group.keys():
					subname = datasetName + '/'+k
					if not np.array_equal(testOut[subname][()], group[k][()]):
						return -3
			else: #other ones are just fine how they are
				if not np.array_equal(testOut[datasetName][()], testIn[datasetName][()]):
					return -4
		gc.collect()
		#copy over the trigger information
		inp = testOut['triggers'][()]
		out = testIn['triggers'][()]
		if not np.array_equal(inp, out):
			return -5
		del inp
		del out
		gc.collect()
		#copy the event information over
		inp = testOut['events'][()]
		out = testIn['events'][()]
		if not np.array_equal(inp, out):
			return -6
		del inp
		del out
		gc.collect()
		#now read in the waveform data and verify the checksums all match what they should
		for key in testOut['waveforms']:
			headers = testOut['waveforms/'+str(key)+'/headers'][()]
			waveforms = testOut['waveforms/'+str(key)+'/waveforms'][()]
			#check if these datasets are empty or not
			if headers.shape is not None:
				#if they have stuff, calculate the checksums and verify it all matches
				checksumsInit = headers['checksum']
				calculated = np.apply_along_axis(bf.Fletcher32, 1, waveforms.view(np.uint16))
				equal = np.array_equal(calculated, checksumsInit)
				if not equal:
					return -7
		testIn.close()
		testOut.close()
		del testIn
		del testOut
		gc.collect()
		return 0
	except Exception as e:
		print('Error occured during Data Integrity Check')
		print(e)
		testIn.close()
		testOut.close()
		del testIn
		del testOut
		gc.collect()
		return -9
	gc.collect()
	return 0

def findHDF5FilesToOperateOn(filedir):
	"""
	This script looks for a .fin file
	These are indicators from the DAQ that a new file should be analyzed
	Once one is found, a hdf5 file with the appropriate name is identified
	and it's existence is verified.
	
	Those that pass all these checks are ready for analysis.
	"""
	files = os.listdir(filedir)
	if len(files) == 0: #no files found
		return None
	else:
		hdf5Files = []
		for file in files:
			name, ext = os.path.splitext(file)
			if ext == '.end':
				hdf5name = os.path.join(filedir, name) +'.h5'
				if os.path.exists(hdf5name):
					hdf5Files.append(hdf5name)
				else:
					print('HDF5 File not found!!!')
					print('How did that happen??')
					return -1
		return hdf5Files

def deleteFinFile(file):
	"""
	This function looks for the .fin file that indicated that we should do analysis
	and deletes it. This is only called after the analysis is done.
	The expected name passed to this is the HDF5 file name
	"""
	finName = os.path.splitext(file)[0]
	finName+='.end'
	os.remove(finName)
	return

def checkForStopSignal(directory):
	"""
	Checks for a file signal to stop the replay code
	
	Parameters
	----------
	directory: string
		The location to search for the stop signal in
	
	Returns
	-------
	result: boolean
		If true, then the code should continue running
		If false, then the replay code should stop because stop.stop has been found
	"""
	files = os.listdir(directory)
	if 'stop.stop' in files:
		return False
	else:
		return True


def replayScript(inputDir = '/mnt/CacheSSD/', outputDir = '/mnt/raid/Nab/ORNL', badFolder = '/mnt/raid/Nab/ORNL/problematicFiles', queryTime = 5, compression = False):
	"""
	This is the actual replay script. It's job is to identify files that have recently arrived from the DAQ system and process them.
	
	It will replay the files into a format that is easily handled by pyNab and offline analysis in general.
	Eventually this will have additional post-processing functionality.
	For now, it's just converting file formats.
	
	Parameters
	----------
	inputDir: string
		Defaults to : /mnt/CacheSSD/
		The location to look for incoming files
	
	outputDir: string
		Defaults to /mnt/raid/Nab/ORNL
		The location to output the files to
	
	badFolder: string
		The location where problematic files that broke the replay script should be moved to
		Any files that fail to replay, or replayed files that fail to verify, are moved here
	
	queryTime: int
		Defaults to 5
		The time to wait to look for new files if no files were found
	
	compression: bool
		Defaults to False
		Enables compression. Do not use until official HDF5 support goes through
	
	Returns
	-------
	None
	"""
	print('Replay Code Running')
	print('Looking for Files in Directory: ' + inputDir)
	go = True
	while go:
		go = checkForStopSignal(inputDir)
		if not go:
			print('Stop Signal Received')
			print('Stopping execution after this batch of files')
		toOperateOn = findHDF5FilesToOperateOn(inputDir)
		if toOperateOn is not None:
			if isinstance(toOperateOn, int): #in this case it's an error code
				print('error found during findHDF5FilesToOperateOn')
				print('System stopping')
				go = False
			elif isinstance(toOperateOn, list):
				#in this case we found some files and want to analyze them
				for file in toOperateOn:
					#get the original file name without directory
					print('starting replay script on file: ', file)
					basename = os.path.basename(file)
					outputName = os.path.join(outputDir, basename)
					replayRes = convertFileFormatFullDAQ(file, outputName, compression = False)
					gc.collect()
					if replayRes == -1:
						print('\t Replay failed, moving file to badFolder: ', badFolder)
						origFileNewLocation = os.path.join(badFolder, basename)
						#this file failed, move it to the bad folder
						shutil.move(file, origFileNewLocation)
						deleteFinFile(file)
						if os.path.exists(outputName): #if it had made the new file, delete it
							os.remove(outputName)
					elif replayRes == 0: #only do this if the previous code exited properly
						print('\t replay finished')
						print('\t verifying data integrity')
						deleteFinFile(file)
						'''
						result = verifyDataIntegrity(file, outputName)
						gc.collect()
						if result == 0:
							print('\t \t Success!')
							#if this succeeds then we delete the original file
							deleteFinFile(file)
							os.remove(file)
							gc.collect()
						else:
							print('\t \t Data Integrity check failed with error: ', result)
							print('\t \t Moving file to the badfolder: ', badFolder)
							origFileNewLocation = os.path.join(badFolder, basename)
							#this file failed, move it to the bad folder
							shutil.move(file, origFileNewLocation)
							#now delete the replayed file cause it didn't work properly
							os.remove(outputName)
							deleteFinFile(file)
							break
						'''
					else:
						print('how did you get here??')
						break
		else:
			time.sleep(queryTime)
	if not checkForStopSignal(inputDir): 
		#if the code stopped due to a stop.stop file appearing, delete it
		os.remove(os.path.join(inputDir, 'stop.stop'))
	return
