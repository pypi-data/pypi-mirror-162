import os
import numpy as np
import struct
from . import fileFormats as ff
from . import basicFunctions as bf
import pandas as pd
import h5py

class triggerFile:
	def __init__(self, filenames, fileFormat ='Nab', pixelMapping = None, startTime = None):
		self.filenames = filenames
		self.__startTime = None
		if startTime is not None:
			self.__startTime = startTime
		self.__pixelMap = None
		if pixelMapping is not None:
			self.__pixelMap = np.copy(pixelMapping)
		self.__hdf5 = False
		if not isinstance(self.filenames, list):
			self.filenames = [self.filenames]
		self.fileFormat = fileFormat
		self.__openFiles()
		self.__findBoardChannels()
		self.__processPixelMap()
		self.__currentCut = np.arange(self.numtrigs)
		self.__cutDefinitions = []
		return
	def __openFiles(self):
		self.__files = []
		self.__fileHeaders = []
		self.__seekAmount = 0
		self.__empty = []
		self.numtrigs = 0
		self.__numtrigs = []
		for name in self.filenames: #iterate over each element in the list of values passed
			if isinstance(name, h5py._hl.dataset.Dataset): #in this case we were passed an HDF5 dataset
				self.__hdf5 = True
				self.__files.append(np.array(name))
				self.__numtrigs.append(len(name))
				self.numtrigs += len(name)
			else:
				self.__hdf5 = False
				tempfile = open(name, "rb")
				tempseek, temphead = ff.readFileHeader(tempfile, self.fileFormat)
				self.__seekAmount = tempseek
				self.__fileHeaders.append(temphead)
				size = os.path.getsize(name)
				empty = size == tempseek
				self.__empty.append(empty)
				if not empty:
					tempfile.seek(tempseek)
					tempfile = np.array(np.memmap(name, offset=tempseek, mode='r', dtype=ff.triggerType()))
					self.__files.append(tempfile)
					self.__numtrigs.append(len(tempfile))
					self.numtrigs += len(tempfile)
		if self.__files == []:
			self.__files = None
		elif len(self.__files) == 1:
			self.__files = self.__files[0]
			self.__files = pd.DataFrame(self.__files)
		else:
			self.__files = np.concatenate(self.__files, axis=0)
			self.__files = pd.DataFrame(self.__files)
		if self.__files is not None:
			if self.getFileStartTime() is not None:
				startTime = self.getFileStartTime()
				#now shift all of the FPGA times by this
				self.__files['unix timestamp'] = self.__files['timestamp'] + startTime / (4E-9)
	def __findBoardChannels(self):
		if self.__files is None:
			self.bcs = None
		else:
			self.bcs = list(np.unique(self.__files['bc'], axis=0, return_counts = True, return_inverse = True))
			temp = self.bcs[0][:]
			self.bcs[0] = []
			for a in temp:
				self.bcs[0].append(a.tolist())
			self.numChannels = len(self.bcs[0])
	def __processPixelMap(self):
		if self.__pixelMap is not None and self.__files is not None:
			#first figure out how many channels there are
			#expects a 1d array where the location of the element is the bc value and the integer stored
			#is the pixel number
			#check the length of the pixel map and handle it if it's off by a little bit or anything like that
			try:
				if len(self.__pixelMap) == self.numChannels:
					#the easiest case to process
					self.__files['pixel'] = self.__pixelMap[self.__files['bc']]['pixel'].astype(int)
				elif len(self.__pixelMap) > self.numChannels:
					#should be fine to do the normal method
					self.__files['pixel'] = self.__pixelMap[self.__files['bc']]['pixel'].astype(int)
				else: #the hardest method to handle
					#in this case we want to pad the pixel map
					self.__temp = np.zeros(self.numChannels)
					self.__temp[:len(self.__pixelMap)] = self.__pixelMap[:]['pixel']
					self.__temp[len(self.__pixelMap):] = np.arange(-1, -1-(self.numChannels - len(self.__pixelMap)), -1)
					self.__files['pixel'] = self.__temp[self.__files['bc']].astype(int)
					#now pixel should be available in the dataframe
			except:
				print('pixel mapping failed, check pixel map for inconsistencies')
	def triggers(self, orig = False):
		"""
		Return the triggers to the user after all cuts have been applied.
		
		Parameters
		----------
		orig: bool, defaults to False
			if True, ignore cuts and return raw triggers
		
		Returns
		-------
		triggers: Pandas DataFrame
			returns the original trigger file with any additional columns added as a Pandas DataFrame"""
		if orig: 
			return self.__files
		else:
			return self.__files.loc[self.returnCut(), :]
	def files(self):
		return self.__files
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
		if self.__hdf5:
			return [[]]
		else:
			if fileNumber is None:
				return self.__fileHeaders
			else:
				if isinstance(fileNumber, int):
					return [self.__fileHeaders[fileNumber]]
				else:
					print('unknown fileNumber input: must be int')
					return [[]]
	def addColumn(self, name, data, overwite = True):
		"""
		This function is used to add a column to the header information so that it can be used for cuts.
		This is effectively a wrapper about the Pandas functionality that adds columns to dataframes
		There are additional protections in the case of accidentally overwriting data. 
		
		Parameters
		----------
		name: str
			the name of the column to be added. It must not already be present in the dataset
		data: np.ndarray or list
			This must be the same length as either the full dataset or as the current cut. 
			If the same length as the current cut, all values not included in the cut in the column are set
				to np.nan
		"""
		#check if the column exists already
		if name in self.__files.columns:
			print('Column under that name already exists')
			return
		else:
			if len(data) == self.numWaves:
				#in this case we were passed something that is the full length so use the standard method
				self.__files[name] = data
			elif len(data) == len(self.headers()):
				#need to basically make an array with the full length of the dataset and put this data into it
				temp = np.zeros(len(self.triggers(orig=True)), dtype=data.dtype)
				temp[:] = np.nan
				temp[self.triggers().index] = data[:]
				self.__files[name] = temp[:]
	def getFileStartTime(self):
		"""
		This function returns the start time of the file as a unix timestamp in UTC
		If multiple files, it only returns the first one (previous versions returned a list)
		Some file formats don't have this information available. Those return a None in the list
		
		For HDF5 file formats, this information is passed to the class on creation. Each file is assumed to start at 
		the same time.
		"""
		if self.__startTime is not None and self.__hdf5:
			return self.__startTime
		else:
			headers = self.fileHeaders()
			if len(headers) != 0:
				if 'unit timestamp' in headers[0]:
					return headers[0]['unix timestamp']
				else:
					return None
	def defineCut(self, category, operator=None, optionA=None, optionB = None):
		"""
		This function defines a cut to apply to the dataset. 
		You can only cut on data available in the headers
		
		Parameters
		----------
		category : str
			the category to cut on. Must be a category in the trigger header
				'energy', 'bc', 'timestamp', 'pixel': if pixel map is provided
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
		self.__currentCut = bf.defineCut(self.files(), category, operator=operator, optionA=optionA, optionB=optionB)
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
		self.__currentCut = np.arange(self.numtrigs)
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
	def plotTriggerLocations(self, bcmap = None, numDet=1, cmap='cividis'):
		if bcmap is None and self.__pixelMap is None:
			print('need a pixel map')
			return None
		else:
			if bcmap is None: #assume the earlier provided mapping
				#need to do my own histogram
				hist = np.zeros(127)
				pixel, counts = np.unique(self.triggers()['pixel'].to_numpy(), return_counts = True)
				hist[pixel] = counts[:]
				return bf.plotOneDetector(hist, numDet = numDet, cmap = cmap)
