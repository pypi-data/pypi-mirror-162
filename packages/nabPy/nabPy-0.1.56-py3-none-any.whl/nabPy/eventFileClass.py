#this script handles the event files. It opens the file and parses all of the events within it
import numpy as np
from . import fileFormats as ff
import os
import copy #used for deepcopy behavior
import h5py


class event:
	def __init__(self, file): #this is passed an open file and reads from it
		self.type, self.uuid, self.wavelength, self.numtrigs = np.fromfile(file, dtype=ff.eventHeader(), count=1)[0]
		self.trigs = []
		self.neighbors = []
		for i in range(self.numtrigs):
			self.trigs.append(np.fromfile(file, dtype=ff.triggerType(version='event'), count=1)[0])
			if self.trigs[i]['numNeighbors'] != 0:
				self.neighbors.append(np.fromfile(file, dtype='u1', count=self.trigs[i]['numNeighbors']))
			else:
				self.neighbors.append(None)
		self.baselineTimestamp = np.fromfile(file, dtype='uint64', count=1)[0]

class eventFile:
	def __init__(self, filenames):
		self.filenames = filenames
		if not isinstance(self.filenames, list): #convert into list
			self.filenames = [self.filenames]
		self.__hdf5 = False
		self.__openFile() #actually open the files
	def __openFile(self):
		self.events = []
		self.__files = []
		for name in self.filenames:
			if isinstance(name, h5py._hl.dataset.Dataset): #check if it's an hdf5 dataset
				self.__hdf5 = True
				self.__files.append(np.array(name))
			else:
				self.__file = open(name, 'rb')
				self.__fileSize = os.stat(name).st_size
				self.__seekAmount, self.__fileHeader = ff.readFileHeader(self.__file)
				self.__formatVersion = self.__fileHeader['file format']
				self.__file.seek(self.__seekAmount)
				self.__currentLoc = self.__file.tell()
				while self.__currentLoc < self.__fileSize:
					self.__files.append(event(self.__file))
					self.__currentLoc = self.__file.tell()
		if self.__files == []:
			self.__files = None
		else:
			if self.__hdf5:
				self.__files = np.concatenate(self.__files, axis=0)
		return
	def events(self):
		"""
		This function returns a copy of the events stored in the given files.
		
		Parameters
		----------
		None
		
		Returns
		-------
		If filetype is HDF5:
			returns numpy.ndarray of events
		Else:
			returns deepcopied list of events
		The type of each element in the relevant containers is NOT the same.
		Do not intermingle HDF5 datasets with non-HDF5 datasets
		"""
		if self.__hdf5:
			return copy.deepcopy(self.__files)
		else:
			return self.__files[:]
	def event(self, i):
		"""
		This function returns the requested event to the user.
		
		Parameters
		----------
		i: event number
		
		Returns:
		event:
			The type of this event depends on if HDF5 is used or not. 
			If HDF5, it's the type output by the DAQ.
			If not HDF5, a custom class to handle the event type.
			These are NOT necessarily compatible so use with caution. 
		"""
		return self.__files[i]
