'''
This is the Nab Python class that can handle a lot of the standard data processing 
and plot making routines. It expects the user to have a variety of libraries that are all 
imported below.
'''
#normal python includes
import numpy as np
import matplotlib.pyplot as plt
import os
import ntpath
import dask.array as da
import dask.dataframe as dd
__hdf5Available = False
try:
	import nabCompression.h5
	__hdf5Available = True
except:
	try:
		import deltaRice.h5
		__hdf5Available = True
	except:
		__hdf5Available = False

import h5py #used for handling the hdf5 datafiles

#commonly used functions between classes
from . import basicFunctions as bf
from . import fileFormats as ff

#the classes themselves
from . import parameterFileClass as pf
from .import eventFileClass as ef
from . import resultFileClass as rf
from . import triggerFileClass as tf
from . import temperatureFileClass as tmf
from . import waveformFileClass as wf
from . import replay as re

versionNumber = '0.2.1' #version 0.2.1 added in HDF5 support

#first define the standard run class type
class DataRun:
	def __init__(self, directory, runNumber, ignoreEventFile = False, bulkRead = False):
		self.ignoreEventFile = ignoreEventFile
		self.bulkRead = bulkRead 
		self.__hdf5 = False
		self.__hdf5Files = []
		self.__hdf5Filenames = []
		#first find the associated datafiles
		self.directory = directory
		self.runNumber = runNumber
		res = self.__findRelevantFiles()
		if res == -1:
			print('no DataRun class created')
			return None
		#now instantiate the various associated classes with each file cluster
		self.__openFiles()
		#now interpolate the temperature data so the waveform files and whatnot know the FPGA temperatures for each hit and whatnot
		self.__mapTemperatures()
		return
	def __exit__(self, exc_type, exc_value, traceback): #clearing up the class
		if self.__hdf5:
			for file in self.__hdf5Files:
				file.close()
	def __findRelevantFiles(self):
		self.__paramFilenames = []
		self.__coincFilenames = []
		self.__eventFilenames = []
		self.__noiseFilenames = []
		self.__pulsrFilenames = []
		self.__singlFilenames = []
		self.__tmprtFilenames = []
		self.__triggFilenames = []
		#basically go through the directory and find all of the files that match this description and whatnot
		tmp = [f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
		tmp = bf.natural_sort(tmp)
		for file in tmp:
			#first check to see if it's run number matches what we want
			name = bf.path_leaf(file)
			ext = os.path.splitext(file)[1]
			tmpnum = name.split('_')[0][3:]
			try:
				tmpnum = int(tmpnum)
			except ValueError:
				tmpnum = None
			if tmpnum is not None:
				if tmpnum == self.runNumber: #verify that the run number is the same
					#check the extension on each file
					if ext == '.h5': #using the hdf5 file extension instead of the other file extensions
						self.__hdf5 = True
						self.__hdf5Filenames.append(self.directory + file)
						self.__hdf5Files.append(h5py.File(self.directory + file, 'r'))
					else: #not using hdf5
						self.__hdf5 = False
						if ext == '.param': #parameter file
							self.__paramFilenames.append(self.directory + file)
						elif ext == '.trigg': #trigger file
							self.__triggFilenames.append(self.directory + file)
						elif ext == '.event': #event file
							self.__eventFilenames.append(self.directory + file)
						elif ext == '.tmprt': #temperature file
							self.__tmprtFilenames.append(self.directory + file)
						elif ext == '.singl': #single file
							self.__singlFilenames.append(self.directory + file)
						elif ext == '.coinc': #coincidence file
							self.__coincFilenames.append(self.directory + file)
						elif ext == '.noise': #noise file
							self.__noiseFilenames.append(self.directory + file)
						elif ext == '.pulsr': #pulser file
							self.__pulsrFilenames.append(self.directory + file)
					#any other file extensions get ignored
		#check to make sure that at least 1 file was found, otherwise give up
		if not self.__paramFilenames and not self.__coincFilenames and not self.__eventFilenames and not self.__noiseFilenames and not self.__pulsrFilenames and not self.__singlFilenames and not self.__tmprtFilenames and not self.__triggFilenames and not self.__hdf5Filenames:
				print('no files with Run # = ', self.runNumber, ' found in ', self.directory)
				return -1
		else:
			if self.__hdf5:
				for file in self.__hdf5Files:
					#first add all the files that are always present
					if 'Parameters' in file.keys():
						self.__paramFilenames.append(file['Parameters'])
					if 'triggers' in file.keys():
						self.__triggFilenames.append(file['triggers'])
					if 'events' in file.keys():
						self.__eventFilenames.append(file['events'])
					if 'FPGATemperatures' in file.keys():
						self.__tmprtFilenames.append(file['FPGATemperatures'])
					#now add the waveform files
					if 'singles' in file['waveforms'].keys():
						self.__singlFilenames.append(file['waveforms/singles'])
					if 'coincidences' in file['waveforms'].keys():
						self.__coincFilenames.append(file['waveforms/coincidences'])
					if 'baselines' in file['waveforms'].keys():
						self.__noiseFilenames.append(file['waveforms/baselines'])
					#handle the fact I'm an idiot and misnamed this dataset
					if 'pulsers' in file['waveforms'].keys():
						self.__pulsrFilenames.append(file['waveforms/pulsers'])
					elif 'pulser' in file['waveforms'].keys():
						self.__pulsrFilenames.append(file['waveforms/pulser'])
		return 0
	#now a whole bunch of file opening scripts
	def __openFiles(self):
		self.__openParamFiles()
		self.__openTriggerFiles()
		self.__openTemperatureFiles()
		self.__openWaveformFiles()
		if not self.ignoreEventFile and not self.__hdf5: #this has no effect on HDF5 as that doesn't have the event file issues
			self.__openEventFiles()
	def __openParamFiles(self):
		if self.__hdf5:
			self.__parameterFile = pf.parameterFile(self.__hdf5Files[0]['Parameters'])
		else:
			self.__parameterFile = pf.parameterFile(self.__paramFilenames[0])
	def __openTriggerFiles(self):
		self.__triggerFiles = tf.triggerFile(self.__triggFilenames, pixelMapping = self.parameterFile().BoardChannelPixelMap)
	def __openTemperatureFiles(self): #open all of the temperature files and combine all that information
		self.__temperatures = tmf.temperatureFile(self.__tmprtFilenames)
	def __openWaveformFiles(self):
		self.__coincFiles = wf.waveformFile(self.__coincFilenames, pixelMapping = self.parameterFile().BoardChannelPixelMap['pixel'], startTime = self.parameterFile().startTime, bulkRead = self.bulkRead)
		self.__noiseFiles = wf.waveformFile(self.__noiseFilenames, pixelMapping = self.parameterFile().BoardChannelPixelMap['pixel'], startTime = self.parameterFile().startTime, bulkRead = self.bulkRead)
		self.__pulsrFiles = wf.waveformFile(self.__pulsrFilenames, pixelMapping = self.parameterFile().BoardChannelPixelMap['pixel'], startTime = self.parameterFile().startTime, bulkRead = self.bulkRead)
		self.__singlFiles = wf.waveformFile(self.__singlFilenames, pixelMapping = self.parameterFile().BoardChannelPixelMap['pixel'], startTime = self.parameterFile().startTime, bulkRead = self.bulkRead)
	def __openEventFiles(self):
		self.__eventFiles = []
		for name in self.__eventFilenames:
			self.__eventFiles.append(ef.eventFile(name))
	def __mapTemperatures(self):
		return None
	#process the various different files and return relevant information
	def filenames(self, category=None):
		"""
		This function prints the names of the various files that were loaded in.
		
		In the case the code is using HDF5 files, the category parameter does nothing
		
		Parameters
		----------
		category: defaults to None, options require string input. case doesn't matter
			'param', 'parameter', 'parameters': returns the parameter file list
			'coinc', 'coincidence', 'coincidences': returns the coincidence file list
			'noise', 'baseline': returns the long baseline trace files
			'pulser', 'pulsr', 'pulsers', 'pulsrs': pulser file names
			'singles', 'single', 'singl': singles file names
			'temps', 'temp', 'temperatures', 'temperature': temperature file names
			'trigger', 'triggers', 'triggs', 'trigg', 'trig', 'trigs': the trigger file names
		
		Returns
		-------
		filenames: list[list] or list
			If category is None:
				returns a list[list] format where each filename type is grouped in a list and output together
			else:
				returns a singular list with each filename of that type or [] for unrecognized category
		"""
		if self.__hdf5: #in the case we are using HDF5, just do it this way
			return self.__hdf5Filenames
		else:
			if category is not None:
				cat = category.lower()
				if cat in ['param', 'parameter', 'parameters']:
					return self.__paramFilenames
				elif cat in ['coinc', 'coincidence', 'coincidences']:
					return self.__coincFilenames
				elif cat in ['noise', 'baseline']:
					return self.__noiseFilenames
				elif cat in ['pulser', 'pulsr', 'pulsers', 'pulsrs']:
					return self.__pulsrFilenames
				elif cat in ['singles', 'single', 'singl']:
					return self.__singlFilenames
				elif cat in ['temps', 'temp', 'temperatures', 'temperature']:
					return self.__tmprtFilenames
				elif cat in ['trigger', 'triggers', 'triggs', 'trigg', 'trig', 'trigs']:
					return self.__triggFilenames
				else:
					print('unrecognized category')
					return []
			else:
				return [self.__paramFilenames, self.__coincFilenames, self.__eventFilenames, self.__noiseFilenames, self.__pulsrFilenames, self.__singlFilenames, self.__tmprtFilenames, self.__triggFilenames]
	def parameterFile(self):
		"""
		This returns the parameter file class as defined in Nab.pf.parameterFile()
		"""
		return self.__parameterFile
	def eventFile(self):
		"""
		This returns the event file class as defined in Nab.ef.eventFile()
		"""
		return self.__eventFiles
	def singleWaves(self):
		"""
		This returns the singles waveforms in a waveformFile class as defined in Nab.wf.waveformFile()
		"""
		return self.__singlFiles
	def coincWaves(self):
		"""
		This returns the coincidence waveforms in a waveformFile class as defined in Nab.wf.waveformFile()
		"""
		return self.__coincFiles
	def pulsrWaves(self):
		"""
		This returns the pulser waveforms in a waveformFile class as defined in Nab.wf.waveformFile()
		"""
		return self.__pulsrFiles
	def noiseWaves(self):
		"""
		This returns the long baseline traces waveforms in a waveformFile class as defined in Nab.wf.waveformFile()
		"""
		return self.__noiseFiles
	def triggers(self):
		"""
		This returns the triggers in a triggerFile class as defined in Nab.tf.triggerFile()
		"""
		return self.__triggerFiles
	def temperatures(self):
		"""
		This returns the FPGA temperatures in a temperatureFile class as defined in Nab.tmf.temperatureFile()
		"""
		return self.__temperatures
	#now the basic grabbing of file functions have been defined
	#now some additional functionality and wrapping of functions from the other classes
	def runStartTime(self):
		"""
		This function goes and determines when the run was started.
		It grabs this information from a singles waveform file header.
		
		Parameters: None
		
		Returns:
			Unix timestamp in UTC timezone
		"""
		#check if this data is in the parameter file
		if self.parameterFile().startTime is not None:
			#this should go off for HDF5 formatted files
			return self.parameterFile().startTime
		else: #if that data isn't there, move this to another dataset
			if self.singleWaves() is not None:
				return self.singleWaves().getFileStartTime()
			elif self.coincWaves() is not None:
				return self.coincWaves().getFileStartTime()
		
	def plotHitLocations(self, sourceFile = 'trigger', orig = False, **kwargs):
		"""
		This function plots the hit locations from a particular file.
		This effectively wraps around the function plotOneDetector as defined in Nab.bf.plotOneDetector()
		
		Parameters:
			sourceFile: str, defaults to 'trigger'
				This defines the source file to grab hit information from.
				Options: 'trigger', 'triggers', 'single', 'singles', 'coincidence', 'coincidences'
			orig: bool, defaults to False
				If true, return the original hit locations before cuts
				If false, return hit locations after cuts
		"""
		sourceFile = sourceFile.lower() #convert to lower case
		#this function goes through and plots the hit locations for any file
		#first figure out the source
		numPixels = 127
		if self.parameterFile().NumChannels > 128:
			numPixels = 254
			print('2 detector operations not supported yet in this function')
			return None
		bins = np.arange(1, numPixels+2)
		pixels = None
		if sourceFile == 'trigger' or sourceFile == 'triggers': #in this case to plot is obvious, just plot the main stuff
			pixels = self.triggers().triggers(orig)['pixel']
		elif sourceFile == 'single' or sourceFile == 'singles':
			#first calculate the bc number, the unique value from 0 - 128 that each has
			pixels = self.singleWaves().headers(orig)['pixel']
		elif sourceFile == 'coincidence' or sourceFile == 'coincidences' or sourceFile == 'coinc':
			pixels = self.coincWaves().headers(orig)['pixel']
		elif sourceFile == 'pulsers' or sourceFile == 'pulser' or sourceFile == 'pulsr':
			pixels = self.pulsrWaves().headers(orig)['pixel']
		elif sourceFile == 'noise':
			pixels = self.noiseWaves().headers(orig)['pixel']
		else:
			print('unknown sourceFile option:', sourceFile)
			print('expected trigger(s), single(s), coincidence(s). pulser(s), noise. Case does not matter')
		hist = np.histogram(pixels, bins = bins)[0]
		bf.plotOneDetector(hist, **kwargs)
		return
