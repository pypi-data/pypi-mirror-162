#this script contains the definition of the dataFile class
import os
import numpy as np
import pandas as pd
import struct
from . import fileFormats as ff
import matplotlib.pyplot as plt
from datetime import datetime
import gc 

__nabCompressionAvail = False

try:
	import nabCompression.h5
	__nabCompressionAvail = True
except:
	try:
		import deltaRice.h5
		__nabCompressionAvail = True
	except:
		__nabCompressionAvail = False

import h5py
import dask
import dask.array as da
import dask.dataframe as dd
from . import basicFunctions as bf
from . import resultFileClass as rf

class waveformFile:
	#constructor
	def __init__(self, filenames, fileFormat = 'Nab', pixelMapping = None, pretrigger = None, overwriteFileFormat = None, startTime = None, bulkRead = False):
		"""
		Initializes the waveformFile class.
		
		Parameters
		----------
		filenames: string, h5py.dataset, list[string or h5py.dataset]
			The names of the input files or datasets to use for this
			In the case of a file, assume it's a binary file and use the fileFormat parameter to parse it
			In the case of a h5py group/dataset, load that in through the h5py library
		
		fileFormat = 'Nab':
			The format of the file. This is used for non-HDF5 files/datasets
		
		pixelMapping = None:
			The mapping between board channel and pixel used to create the dataset
		
		"""
		self.__pixelMap = pixelMapping
		self.pretrigger = pretrigger
		self.filenames = filenames
		self.__overwriteFileFormat = overwriteFileFormat
		self.__hdf5 = False
		if self.__overwriteFileFormat is not None:
			if type(self.__overwriteFileFormat) is not list:
				print('invalid format for overwriteFileFormat')
				print('expects list, got ', type(overwriteFileFormat))
				return None
			else:
				if len(self.__overwriteFileFormat) != 3:
					print('invalid length to overwriteFileFormat')
					print('expects 3 entries')
					return None
		self.__startTime = None
		if startTime is not None:
			self.__startTime = startTime
		if not isinstance(self.filenames, list):
			self.filenames = [self.filenames]
		self.fileFormat = fileFormat
		self.__openFiles(bulkRead = bulkRead)
		#now create the mapping so we know where to look for each waveform number
		self.__findBoardChannels()
		#now if the pixel map exists apply that
		self.__processPixelMap()
		#now initialize all of the cutting stuff
		self.__cutDefinitions = [] #defines the operations
		 #the map of the current cut on the data, updated by each
		if self.__files is not None:
			if self.__hdf5:
				self.names = [*self.__files['header'].dtype.names, 'wave']
				self.headerNames = [*self.__files['header']]
			else:
				self.names = [*self.__files['header'].dtype.names, 'wave']
				self.headerNames = [*self.__files['header'].dtype.names]
		else:
			self.names = [None]
	def __openFiles(self, bulkRead = False): #open all the files
		self.__files = []
		self.__tempHeaders = []
		self.__fileHeaders = []
		self.__seekAmount = 0
		self.__empty = []
		self.numWaves = 0
		self.__numWaves = []
		self.wavelength = 0
		self.headWaveType = None
		self.pretrigger = None
		self.hdf5ChunkSize = None
		for name in self.filenames:
			#check the type
			if isinstance(name, h5py._hl.dataset.Dataset) or isinstance(name, h5py._hl.files.File) or isinstance(name, h5py._hl.group.Group):
				self.__hdf5 = True
			elif os.path.splitext(name)[1] == '.h5':
				self.__hdf5 = True
				name = h5py.File(name, 'r')
			if self.__hdf5:
				self.fileFormatNumber = 3 #signifying HDF5
				if self.pretrigger is None:
					self.pretrigger = 800
				keys = name.keys() #handle the naming discrepancy
				headname = 'header'
				wavename = 'waveform'
				if 'headers' in keys:
					headname = 'headers'
				if 'waveforms' in keys:
					wavename = 'waveforms'
				self.headerType = name[headname].dtype
				empty = False
				if name[headname].shape is None or name[wavename].shape is None:
					empty = True
					self.__empty.append(empty)
				if not empty:
					self.wavelength = len(name[wavename][0])
					t = name[wavename].chunks
					if t is not None:
						self.hdf5ChunkSize = name[wavename].chunks[0]
					else:
						self.hdf5ChunkSize = None
					self.__files.append([name[headname], name[wavename]])
					self.__numWaves.append(len(name[wavename]))
					self.numWaves += len(name[wavename])
			else:
				tempfile = open(name, "rb")
				tempseek, temphead = ff.readFileHeader(tempfile, self.fileFormat, waveformfile = True)
				self.fileFormatNumber = temphead['file format']
				if self.pretrigger is None:
					self.pretrigger = temphead['pretrigger']
				else:
					if self.pretrigger != temphead['pretrigger']:
						print('discrepancy in waveform file pretrigger length detected')
						print('recommend separation of files with different pretriggers for analysis')
				self.headerType = None
				if self.__overwriteFileFormat is None:
					self.headerType = np.dtype(ff.headerType(self.fileFormat, self.fileFormatNumber))
				else:
					self.headerType = self.__overwriteFileFormat[1][0][1]
				self.__seekAmount = tempseek
				self.__fileHeaders.append(temphead)
				#determine if the file is empty
				size = os.path.getsize(name)
				empty = size == tempseek
				self.__empty.append(empty)
				if not empty:
					tempfile.seek(tempseek)
					header = np.fromfile(tempfile, dtype=self.headerType, count=1)[0]
					self.wavelength=header['length']
					if self.__overwriteFileFormat is None:
						self.headWaveType = np.dtype(ff.headWaveType(self.wavelength, self.fileFormat, self.fileFormatNumber))
					else:
						self.headWaveType = np.dtype(self.__overwriteFileFormat[1])
					tempfile.close()
					if bulkRead:
						#actually read in the headers and waveforms at once cause it's faster
						t = np.fromfile(name, offset = tempseek, dtype=self.headWaveType)
						temphead = np.copy(t['header'])
						del t
					else:
						#otherwise just do the memory map and individually parse this later on
						temphead = da.from_array(np.memmap(name, offset = tempseek, mode='r', dtype=self.headWaveType), chunks = {0: 1024, 1: -1})['header']
					tempfile = da.from_array(np.memmap(name, offset = tempseek, mode='r', dtype=self.headWaveType), chunks = {0: 1024, 1: -1})
					self.__files.append(tempfile)
					self.__tempHeaders.append(temphead)
					self.__numWaves.append(len(tempfile))
					self.numWaves += len(tempfile)
		#make the value of .__files either a list with each element being [headers, waveforms] or None
		if self.__files == []:
			self.__files = None
		elif len(self.__files) == 1:
			if self.__hdf5:
				#in this case we do have to be careful with the chunking because of compression
				self.__files = {'header': np.array(self.__files[0][0]), 'wave': da.from_array(self.__files[0][1], chunks = {0: 'auto', 1: -1})}
			else:
				self.__files = {'header': np.concatenate(self.__tempHeaders), 'wave': da.concatenate(self.__files, axis=0)['wave']}
		else:
			if self.__hdf5:
				self.__files = list(zip(*self.__files)) #transpose the list so it's 2 elements [headers, waveforms]
				self.__files = {'header': np.concatenate(self.__files[0], axis=0), 'wave': da.concatenate(self.__files[1], axis=0).rechunk(chunks = {0: 'auto', 1: -1})}
			else:
				self.__files = da.concatenate(self.__files, axis=0)
				self.__tempHeaders = np.concatenate(self.__tempHeaders)
		#with the whole file array determined
		#parse it into a dataframe for the header information and a numpy structured array for the rest
		self.__currentCut = np.arange(self.numWaves)
		#at this point we want to read all of the headers in from the files
		#and save it as a pandas dataframe
		#but only if it actually has data in it
		if self.__files is not None: #if there is data that was read in
			if isinstance(self.__files['header'], np.ndarray): #if this is a numpy array, then do this with it
				self.__headers = pd.DataFrame(self.__files['header'])
				del self.__tempHeaders
			elif isinstance(self.__files['header'], da.core.Array): #if they haven't been loaded in, do so now
				self.__headers = pd.DataFrame(self.__files['header'].compute()) #load the headers into memory
			else: #otherwise it's probably an HDF5 file type and we should be good to go this way
				self.__headers = pd.DataFrame(self.__files['header'])
			self.__waves = self.__files['wave']
			if self.pretrigger is None and self.__hdf5:
				self.pretrigger = 800 #the default, due to Ca45
			elif self.pretrigger is None and not self.__hdf5:
				self.pretrigger = self.__fileHeaders[0]['pretrigger']
			#now if the data type is missing the bc parameter, add that in
			if 'bc' not in self.headers().dtypes.index.values:
				self.__headers['bc'] = self.__headers['board']*8+self.__headers['channel']
			else:
				if 'board' not in self.headers().dtypes.index.values:
					self.__headers['board'] = np.floor(self.__headers['bc']/8).astype(np.int32)
					self.__headers['channel'] = self.__headers['bc'] - self.__headers['board']*8
			#now add in the unix timestamp column if it's available
			if self.getFileStartTime() is not None:
				startTime = self.getFileStartTime()
				#now shift all of the FPGA times by this
				self.__headers['unix timestamp'] = self.__headers['timestamp'] + startTime / (4E-9)
		else:
			self.__headers = None
			self.__waves = None
			self.pretrigger = None
	def __processPixelMap(self):
		if self.__pixelMap is not None and self.__files is not None:
				#first figure out how many channels there are
				#expects a 1d array where the location of the element is the bc value and the integer stored
				#is the pixel number
				#check the length of the pixel map and handle it if it's off by a little bit or anything like that
				try:
					if len(self.__pixelMap) == self.numChannels:
						#the easiest case to process
						self.__headers['pixel'] = self.__pixelMap[self.headers()['bc']].astype(int)
					elif len(self.__pixelMap) > self.numChannels:
						#should be fine to do the normal method
						self.__headers['pixel'] = self.__pixelMap[self.headers()['bc']].astype(int)
					else: #the hardest method to handle
						#in this case we want to pad the pixel map
						self.__temp = np.zeros(self.numChannels)
						self.__temp[:len(self.__pixelMap)] = self.__pixelMap[:]
						self.__temp[len(self.__pixelMap):] = np.arange(-1, -1-(self.numChannels - len(self.__pixelMap)), -1)
						self.__headers['pixel'] = self.__temp[self.headers()['bc']].astype(int)
				except:
					print('pixel mapping failed, check pixel map for inconsistencies')
				#now pixel should be available in the dataframe
	def __findBoardChannels(self):
		if self.__files is None:
			self.bcs = None
		else:
			self.bcs = list(np.unique(self.__headers['bc'], axis=0, return_counts = True, return_inverse = True))
			temp = self.bcs[0][:]
			self.bcs[0] = []
			for a in temp:
				self.bcs[0].append(a.tolist())
			self.numChannels = len(self.bcs[0])
	def head(self, i, pandas = False):
		"""
		Returns the ith header in the dataset after cutting
		
		Parameters
		----------
		i: int
			The header to return
		pandas: bool (default's to False)
			If you want it to be in the dataframe format or a simple numpy array
		
		Returns:
			either pandas dataframe object or a np.ndarray
		"""
		if pandas:
			index = self.headers().index.values[i]
			return self.headers().loc[index,:]
		else:
			return self.__files[self.__currentCut][i]['header'].compute()
	def wave(self, i, orig=False, prep = False):
		"""
		Returns the ith waveform in the dataset after cutting
		
		Parameters
		----------
		orig: bool (defaults to False)
			If orig is true, return the ith waveform pre-cuts
		prep: bool (defaults to True)
			If prep is true, return the prepared waveform after shifts
		"""
		return self.waves(orig, prep)[i].compute()
	def files(self):
		"""
		Returns the raw dataset (before processing of waveforms)
			before any cuts are applied
		Dataset is returned as a np.ndarray
		"""
		return self.__files
	def headers(self, orig=False):
		"""
		Returns the waveform headers as a Pandas DataFrame.
		
		Parameters
		----------
		orig: bool
			If orig is true, return the whole original DataFrame without cuts
			If orig is false, return the DataFrame with cuts
		
		Returns
		-------
		headers: Pandas DataFrame
		"""
		if self.__headers is not None:
			if orig:
				return self.__headers
			else:
				return self.__headers.loc[self.returnCut(),:]
		else:
			return None
	def waves(self, orig=False, prep = True):
		"""
		Returns the raw waveforms (before processing of waveforms)
		Dataset is returned as a dask array (np.npdarray effectively)
		
		Parameters
		----------
		orig: bool (defuaults to False)
			If orig is True, return the whole np.ndarray without cuts
			If orig is False, return the np.ndarray after cuts
		prep: bool (defaults to True)
			If prep is True, returns the np.ndarray after being converted to 32bit values
			If prep is False, returns the raw original 14bit numbers in 16bit containers
		Returns
		-------
		waveforms: np.ndarray
		"""
		if self.__waves is not None:
			if orig and prep: #if both
				return bf.wavePrep(self.__waves)
			elif orig and not prep:
				return self.__waves
			elif not orig and prep:
				return bf.wavePrep(self.__waves[self.__currentCut])
			elif not orig and not prep:
				return self.__waves[self.__currentCut]
			else:
				print('How did you get here')
				print('.waves() function error')
				return None
		else: 
			return None
	def addColumn(self, name, data, overwrite = False):
		"""
		WARNING: Not completed yet. Do NOT use
		This function is used to add a column to the header information so that it can be used for cuts.
		Parameters
		----------
		name: str
			the name of the column to be added. It must not already be present in the dataset
		data: np.ndarray or list
			This must be the same length as either the full dataset or as the current cut. 
			If the same length as the current cut, all values not included in the cut in the column are set
				to np.nan
		overwrite: defaults to False
		"""
		#check if the column exists already
		if name in self.headers().columns and not overwrite:
			return
		else:
			if len(data) == self.numWaves:
				#in this case we were passed something that is the full length so use the standard method
				self.__headers[name] = data
			elif len(data) == len(self.headers()):
				#need to basically make an array with the full length of the dataset and put this data into it
				temp = np.zeros(len(self.headers(orig=True)), dtype=data.dtype)
				temp[:] = np.nan
				temp[self.headers().index] = data[:]
				self.__headers[name] = temp[:]
	def getFileStartTime(self):
		"""
		This function returns the start time of the file as a unix timestamp in UTC
		If multiple files, it returns the first start time from the various files.
		"""
		if self.__startTime is not None and self.__hdf5:
			return self.__startTime[0]
		else:
			headers = self.fileHeaders()
			if len(headers) != 0:
				if 'unix timestamp' in headers[0]: #check to make sure that value is in the header
					return headers[0]['unix timestamp'] #this just returns the first element
				else:
					return None
	def fileHeaders(self, fileNumber = None):
		"""
		This function returns the file headers to the user.
		
		Parameters
		----------
		fileNumber: int (optional)
			If provided, this specifies which file header to return
			If not provided, returns all of the file headers
		
		Returns
		-------
		fileHeaders: list[list]
			returns a nested list of the file headers.
			If fileNumber is used, then this returns a 2d list still with only one element in the outer list
			The elements in the list are determined by the file format being used
		"""
		if fileNumber is None:
			return self.__fileHeaders
		else:
			if isinstance(fileNumber, int):
				return [self.__fileHeaders[fileNumber]]
				print('unknown fileNumber input: must be int')
				return [[]]
	#returns both headers and waveforms
	#this function grabs all the waveforms from a particular event
	def getEvent(self, event):
		out = self.__files[self.__files['header']['eventid']==event].compute()
		if out is []:
			return None
		else:
			return out
	def defineCut(self, category, operator=None, optionA=None, optionB = None):
		"""
		This function defines a cut to apply to the dataset. 
		You can only cut on data available in the headers
		
		Parameters
		----------
		category : str
			the category to cut on. Must be a category in the waveform header
			To check available categories, call yourWaveformFile.headerType
			Also available categories:
				'pixel': requires a pixel map to be defined in the class
				'custom': unique operation that allows the user to pass a custom map of 
					the data to request instead of determining the map within the class
					This changes the behavior of operator
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
		This doesn't return anything to the user but modifies the cut mask within the class.
		No data is deleted by defining a cut, it just defines a mask to access only particular indices
		"""
		self.__currentCut = bf.defineCut(self.headers(), category, operator=operator, optionA=optionA, optionB=optionB)
		self.__cutDefinitions.append([category, operator, optionA, optionB])
		return
	#this function expects the user to pass a list of cuts in the format of self.__cutDefinitions
	#it does NOT check for proper formatting or anything like that, just trusts that they are safe
	def defineCuts(self, cuts):
		for cut in cuts:
			self.defineCut(*cut)
	def cutsApplied(self):
		return self.__cutDefinitions[:]
	#this resets the cuts applied, called after the removeCut.
	def reapplyCuts(self):
		self.__currentCut = np.arange(self.numWaves) #erase the old 
		self.defineCuts(self.__cutDefinitions)
		return
	def resetCuts(self):
		self.__currentCut = np.arange(self.numWaves)
		self.__cutDefinitions = []
	#remove a cut from the list, this automatically re-applies all of the cuts as well
	def removeCut(self, index):
		del self.__cutDefinitions[index]
		self.resetCuts()
		return
	#remove all of the cuts and completely reset the data
	def removeCuts(self):
		self.__cutDefinitions = [] #erase all cuts
		self.resetCuts()
	#returns the current version of the cut map
	def returnCut(self):
		return self.__currentCut[:]
	#analysis functions that are built in
	def generatePowerSpectra(self):
		return bf.generatePowerSpectra(self.files()['wave'][self.__currentCut])
	def averageWaveforms(self, correctBaseline = False, t0s = None):
		"""
		Returns the average waveform shape of the waveforms included after any cuts are applied
		
		Parameters
		----------
		correctBaseline=False: bool, int
			If correctBaseline==False, the code doesn't correct the baseline at all and averages everything as they come
			If correctBaseline==True, the code shifts the baseline such that the region defined as 
				the 80% of the pretrigger in the class is at 0 for each waveform before averaging
					80% was chosen to avoid rising edge effects
			If correctBaseline is type int, the code shifts the baseline such that the region from 0
				to correctBaseline is at 0 for each waveform before averaging
		t0s: None, np.ndarray
			If None, the code doesn't align the waveforms
			If np.ndarray, code shifts the waveforms to share the same t0 value
				This shift is applied such that the extracted t0 value is aligned to the pretrigger offset value
				stored in the waveform file
		Returns
		-------
		np.ndarray with the averaged waveform shape
		"""
		shifts = None
		if t0s is not None:
			if len(t0s) != len(self.waves()):
				print('Error: Mismatch in provided t0 length and number of waveforms')
				return None
			else:
				shifts = np.ones(len(t0s))*self.pretrigger - t0s
		if type(correctBaseline)==bool:
			if correctBaseline:
				return bf.averageWaveforms(self.waves(), pretrigger = int(0.8*self.pretrigger), shifts=shifts)
			else:
				return bf.averageWaveforms(self.waves(), shifts = shifts)
		elif type(correctBaseline)==int:
			return bf.averageWaveforms(self.waves(), pretrigger = correctBaseline, shifts=shifts)
		else:
			print('Error: unknown correctBaseline parameter: ', correctBaseline)
			return None
	def determineEnergyTiming(self, method=None, params = None, batchsize = 1000, pretrig=None, useGPU = False, rechunk = False, useFFTW = True):
		"""
		This function either runs the trapezoidal filter or the cusp filter depending on the inputs. 
		It only applies these operations on the subset of waveform data remaining after cuts have been applied.
		It then returns the results of this operation as a resultFileClass object.
		
		Parameters
		----------
		method: 'trap', 'cusp'
			The method of extracting energies and timings from the waveforms.
			For more information about each of these functions run these commands
				'trap': "Nab.bf.applyTrapFilter?"
				'cusp': "Nab.bf.applyCuspFilter?"
				'pseudoFit': "Nab.bf.pseudoInverseFit"
				'pseudoTrap': "Nab.bf.pseudoInverseTrapFilter?"
		params: list with varying elements depending on the method passed
			(optional parameters shown in parenthesis)
			'trap': [risetime , flat top length, decay rate, (threshold percent, mean, shift)]
			'cusp': [risetime, flat top length, decay rate, (threshold percent, mean, shift)]
			'pseudoInverse': [templates, baselines, (filtert0=None, searchRange=10, t0weight=None, psdWeight=None, returnResiduals=False)]
			'pseudoTrap': [templates, baselines, rise, top, tau, (percentage=0.8, filtert0=None, searchRange=10, t0weight=None, shift=0)]
		batchsize: int, defaults to 1000
			the number of waveforms to process at a time. Can be adjusted to optimize performance
		pretrig: int
			the length of the waveform before the DAQ trigger time. Used for adjusting the
				baseline offset to be 0. With no value passed it defaults to using the pretrigger
				read in from the waveform file
		useGPU: bool, defaults to False
			Experimental feature that isn't fully enabled yet. Leave on False for stable code execution.
		rechunk: bool, defaults to False
			Experimental feature to possibly aid performance with compressed data that has cuts applied
		
		Returns
		-------
		resultFile: class or None
			Returns a resultFile class object with the energy and timing results in a new column.
			If the code fails for some reason, such as no waveforms being present, this returns None
		"""
		#first check to see if there is actually data
		if self.waves() is None:
			print('no waveforms to operate on')
			return None
		if method is None or params is None:
			print('you must specify both a method and parameters')
			return None
		else:
			if method=='trap': #handle the trap filter method
				if pretrig is None:
					if self.pretrigger is not None:
						pretrig = self.pretrigger - 100
					else:
						pretrig = 800 #in this case just assume 800
				#first verify the input parameters make sense
				if not (len(params) >=3 and len(params) <= 6):
					print('trap method takes 3-6 inputs: rise time, top length, decay rate, (threshold percent, mean, shift)')
					return None
				else:
					eners, times = bf.applyTrapFilter(self.waves(prep=False), *params, pretrigger=pretrig, batchsize=batchsize, useGPU = useGPU, hdf5ChunkSize = self.hdf5ChunkSize, rechunk=rechunk, useFFTW = useFFTW)
					headers = None
					if self.headers() is not None:
						headers = self.headers().copy()
					headers['energy'] = eners
					headers['t0'] = times
					return rf.resultFile(data=headers.copy(), mapping = self.__pixelMap, fileFormatNumber = self.fileFormatNumber)
			elif method=='cusp': #handle the cusp filter method
				if pretrig is None:
					if self.pretrigger is not None:
						pretrig = self.pretrigger - 100
					else:
						pretrig = 800
				if not (len(params) >= 3 and len(params) <= 6):
					print('cusp method takes 3-6 inputs: rise time, top length, decay rate, (threshold percent, mean, shift)')
					return None
				else:
					#actually do the filtering
					eners, times = bf.applyCuspFilter(self.waves(prep=False), *params, pretrigger=pretrig, batchsize=batchsize, useGPU = useGPU, rechunk = rechunk)
					headers = None
					if self.headers() is not None:
						headers = self.headers().copy()
					headers['energy'] = eners
					headers['t0'] = times
					return rf.resultFile(data=headers.copy(), mapping = self.__pixelMap, fileFormatNumber = self.fileFormatNumber)
				return None
			elif method == 'pseudoFit': #for the psuedoinverse fitting method
				if useGPU:
					print('no GPU functionality available for this yet, using CPU instead')
				if (len(params) >= 2 and len(params) <= 7):
					fitParameters, t0s, minChis, psdGuess = bf.pseudoInverseFit(self.waves(prep=False), *params, rechunk = rechunk, batchsize=batchsize)
					if fitParameters is not None: #then results were actually found
						headers = None
						if self.headers() is not None:
							headers = self.headers().copy()
						for i in range(fitParameters.shape[1]):
							name='param'+str(i)
							headers[name] = fitParameters[:,i]
						headers['t0'] = t0s[:]
						headers['chi'] = minChis[:]
						if psdGuess is not None:
							headers['psdGuess'] = psdGuess[:]
						return rf.resultFile(data=headers.copy(), mapping = self__pixelMap, fileFormatNumber = self.fileFormatNumber)
				else:
					print('pseudoFit method takes between 2 and 7 inputs')
					print('templates, baselines, filtert0=None, searchRange=10, t0weight=None')
					print('psdWeight=None, returnResiduals=False')
					return None
			elif method == 'pseudoTrap': #for the pseudoinverse trap filter method
				if useGPU:
					print('no GPU functionality available for this yet, using CPU instead')
				if (len(params) >= 5 and len(params) <= 10):
					results = bf.pseudoInverseTrapFilter(self.waves(), *params, batchsize=batchsize)
					if results is None:
						return None
					else:
						headers = None
						if self.headers() is not None:
							headers = self.headers().copy()
						headers['energy'] = results[:,0]
						headers['t0'] = results[:,1]
						headers['chi'] = results[:,2]
						#now iterate over what's left
						for i in range(3, results.shape[1]):
							outname = 'param'+str(int(i-3))
							headers[outname] = results[:,i]
						return rf.resultFile(data=headers.copy(), mapping = self.__pixelMap, fileFormatNumber = self.fileFormatNumber)
				else:
					print('pseudotrap method takes between 5 and 10 inputs')
					print('templates, baselines, rise, top, tau, percentage=0.8')
					print('filtert0=None, searchRange = 10, t0Weight = None, shift=0')
					return None
			else:
				print('unrecognized method: ', method)
				print('accepts trap, cusp, pseudoFit, psuedoTrap')
				return None
	def extractRiseTimes(self, low = None, high = None, smooth = None, pretrigger = None):
		"""
		This function extracts rise times from waveforms passed to it using a threshold cross method. 
		This defaults to a standard 10% -> 90% threshold cross implementation
		You can add smoothing parameters or adjust the thresholds if desired
		
		IMPORTANT NOTE: Risetimes from different parameters are NOT necessarily equivalent. Do not assume they are.
		Parameters:
			low: None, float
				The lower threshold. Defined as being between 0 and 1. Defaults to 0.1
			high: None, float
				The upper threshold. Defined as being between 0 and 1. Defaults to 0.9
			smoothing: None, np.ndarray
				The smoothing functiont to be applied to the waveform. Defaults to None for no smoothing
			pretrigger: None
				The length of the pretrigger region to be averaged to 0
				Wants the actual pretrigger length set in the file
				Will average up to the 80% point of this region
				If None this defaults to using the information from the class
				If not not, overwrites the class value
		Returns:
			A np.ndarray of the risetimes as determined with the given parameters
		"""
		if pretrigger is None:
			return bf.extractRiseTimes(self.waves(), low=low, high=high, smooth=smooth, pretrigger=self.pretrigger)
		else:
			return bf.extractRiseTimes(self.waves(), low=low, high=high, smooth=smooth, pretrigger=pretrigger) 
	def extractDecayRate(self, start=None, stop=None):
		"""
		This function is used to extract the decay rate of the waveforms.
		This parameter is primarily used for optimizing the trapezoidal and cusp filters.
		
		Parameters
		----------
		start: int, default None
			optional parameter for the start location of the fit
			defaults to classes stored pretrigger value + 100 if None is passed
		stop: int, default None
			the last point in the waveform to fit
			If none this defaults to the end of the waveform
		
		Returns
		-------
		decayRates: np.ndarray
			returns the decay rates in a np.ndarray
		"""
		if self.pretrigger is None and start is None: #in the case the user didn't pass proper parameters
			print('self.pretrigger is None')
			print('must pass in start parameter')
			return None
		else:
			if start is None:
				start = int(self.pretrigger*0.8)
			elif start > self.wavelength:
				print('Weird start request: '+str(start))
				print('start location should be less than the length of the waveform')
				return None
			if stop is None:
				stop = self.wavelength
			elif stop > self.wavelength or stop < start:
				print('Weird stop request: '+str(stop))
				print('stop location should be start < stop < wavelength')
				return None
			return bf.extractDecayRate(self.waves(), start, stop)
			
		if start is None:
			start = pretrigger + 100
			if start > len(self.wavelength):
				print('Weird start request: '+str(start))
				print('start location should be less than the length of the waveform')
				return None
		if stop is None:
			stop = self.wavelength
		return bf.extractDecayRate(self.waves(), pretrigger=pretrigger, start=start, stop=stop)

