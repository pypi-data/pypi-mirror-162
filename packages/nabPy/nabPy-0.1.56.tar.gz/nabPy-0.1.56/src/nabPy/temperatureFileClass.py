import os
import numpy as np
import struct
import pandas as pd
import h5py

from . import fileFormats as ff
from . import basicFunctions as bf

class temperatureFile:
	def __init__(self, filenames, startTime = None):
		self.filenames = filenames
		self.__startTime = None
		if startTime is not None:
			self.__startTime = startTime
		if not isinstance(self.filenames, list):
			self.filenames = [self.filenames]
		self.__hdf5 = False
		self.fileFormat = 'Nab'
		self.__openFiles()
		self.__currentCut = self.__files.index.values #the map of the current cut on the data, updated by each function call, initilized to all included
		return
	def __openFiles(self): #open all the files
		self.__files = []
		self.__fileHeaders = []
		self.__seekAmount = 0
		self.__empty = []
		self.numTemps = 0
		self.__numTemps = []
		self.__fileHeaders = []
		for name in self.filenames:
			if isinstance(name, h5py._hl.dataset.Dataset):
				self.__hdf5 = True
				self.__files.append(np.array(name))
				self.__numTemps.append(len(name))
				self.numTemps += len(name)
			else:
				tempfile = open(name, "rb")
				tempseek, temphead = ff.readFileHeader(tempfile, self.fileFormat)
				self.__seekAmount = tempseek
				self.__fileHeaders.append(temphead)
				#determine if the file is empty
				size = os.path.getsize(name)
				empty = size == tempseek
				self.__empty.append(empty)
				if not empty:
					tempfile.seek(tempseek)
					tempfile = np.memmap(name, offset = tempseek, mode='r', dtype=ff.temperatureType())
					self.__files.append(tempfile)
					self.__numTemps.append(len(tempfile))
					self.numTemps += len(tempfile)
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
				if 'Timestamp' in list(self.__files.dtypes.keys()):
					self.__files['unix timestamp'] = self.__files['Timestamp']*4E-9 + startTime
				elif 'timestamp' in list(self.__files.dtypes.keys()):
					self.__files['unix timestamp'] = self.__files['timestamp']*4E-9 + startTime
	def data(self, orig = False):
		if orig == True:
			return self.__files
		else:
			return self.__files.loc[self.returnCut(),:]
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
					print('unknown fileNumber input: must be int')
					return [[]]
	def getFileStartTime(self):
		"""
		This function returns the start time of the file as a unix timestamp in UTC
		If multiple files, it returns all of them in a list
		Some file formats don't have this information available. Those return a None in the list
		"""
		if self.__startTime is not None and self.__hdf5:
			return self.__startTime
		else:
			headers = self.fileHeaders()
			startTimes = []
			if len(headers) != 0:
				if 'unix timestamp' in headers[0]:
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
			the category to cut on. Must be a category in the waveform header
			To check available categories, call yourWaveformFile.headerType
			Also available categories:
				'pixel': requires a pixel map to be defined in the class
				'custom': unique operation that allows the user to pass a custom map of 
					the data to request instead of determining the map within the class
					This changes the behavior of operator
		operator: str, np.ndarray
			The operation to be applied to that category
			Supported options: >, >=, <, <=, =, ==, !=, between, outside, coincidence
			If category='custom', then this expects a np.ndarray to be used as the mask
			
		optionA: int,float
			This is the first option being passed for the cut.
			For cuts with a single point of comparison, this is that value
			For cuts with two points of comparison such as between, this is the lower value
		optionB: int,float
			This is the second option passed for the cut. It is expected to be the upper value
			for cuts such as between
		
		Returns
		--------
		This doesn't return anything to the user but modifies the cut mask within the class.
		No data is deleted by defining a cut, it just defines a mask
		"""
		self.__currentCut = bf.defineCut(self.data(), category, operator=operator, optionA=optionA, optionB=optionB)
		self.__cutDefinitions.append([category, operator, optionA, optionB])
		return
	#this function expects the user to pass a list of cuts in the format of self.__cutDefinitions
	#it does NOT check for proper formatting or anything like that, just trusts that they are safe
	def defineCuts(self, cuts):
		"""
		Applies multiple cuts to the code. 
		Expects a list with multiple cut definitions as defined by the defineCut function.
		"""
		for cut in cuts:
			self.defineCut(*cut)
	def cutsApplied(self):
		"""
		Returns the list of currently applied cuts in the same format that
		defineCuts expects.
		"""
		return self.__cutDefinitions[:]
	#this resets the cuts applied, called after the removeCut.
	def reapplyCuts(self):
		"""
		This goes back and re-applies all of the cuts that have been defined so far.
		Just a way to reset the dataset
		"""
		self.__currentCut = np.arange(self.numWaves) #erase the old 
		self.defineCuts(self.__cutDefinitions)
		return
	def resetCuts(self):
		"""
		This erases all cuts that have been applied so far.
		"""
		self.__currentCut = self.__files.index.values
		self.__cutDefinitions = []
	#remove a cut from the list, this automatically re-applies all of the cuts as well
	def removeCut(self, index):
		"""
		This removes a cut from the current cut definition. 
		It then calls the resetCuts function to reapply all of the cuts and reset the system
		"""
		del self.__cutDefinitions[index]
		self.resetCuts()
		return
	#remove all of the cuts and completely reset the data
	def removeCuts(self):
		"""
		Same as resetCuts
		"""
		self.resetCuts()
	#returns the current version of the cut map
	def returnCut(self):
		"""
		Returns the current cut definition as a np.ndarray
		"""
		return self.__currentCut[:]
