#this script contains the definition of the dataFile class
import os
import numpy as np
import struct
from . import fileFormats as ff
import matplotlib.pyplot as plt
import h5py

from . import basicFunctions as bf

#These are some helper functions that are used frequently in this class definition

#the conversion operation from 14 bit to 16 bit needed by the files
def boardChannelConversion(bc):
	if isinstance(bc, list):
		return bc
	else:
		return [bc,]

class parameterFile:
	#constructor
	def __init__(self, filename):
		#load the singular parameter file, there is just one per batch of waveform data
		#technically multiple files can be passed in the case of using HDF5
		#however they are the same at the moment so treat them like they are identical
		self.__hdf5 = None
		if isinstance(filename, str): #using old school format
			self.__hdf5 = False
			self.filenames = self.filename = filename
		elif isinstance(filename, h5py._hl.group.Group): #using HDF5 format
			self.__hdf5 = True
			self.filenames = filename
		else: #unknown format
			print('Unknown format passed to parameterFile')
			return None
		self.__openFile()
		self.__parameterSanityCheck()
	def __openFile(self): #open all the files
		if self.__hdf5:
			self.file = self.filenames
		else:
			self.file = open(self.filename, 'r')
		#first section is the config file information
		self.__readFormatGitInfo()
		self.__readConfigFile()
		#read the blank line out
		if not self.__hdf5:
			self.file.readline()
		#now the filter parameters
		self.__readFilterParameters()
		#another blank line between sections
		self.__readPixelReadoutMap()
		self.__readBoardChannelToPixelMap()
		self.__readCoincidenceMap()
		self.__readSettings()
		if not self.__hdf5:
			self.file.close()
		if self.__hdf5:
			self.startTime = self.file['StartTime'][()]
		else:
			self.startTime = None
	def __parameterSanityCheck(self):
		#first thing to check is if the number of boards matches the length of the board channel pixel mapping
		#because if not, that's not ideal
		if self.NumChannels != len(self.BoardChannelPixelMap):
			print('Number of Channels != len(BoardChannelPixelMap): '+str(self.NumChannels)+' != '+str(len(self.BoardChannelPixelMap)))
			print('Possibly an error in DAQ Configuration File: BoardChannelToPixelMap.csv')
			print('Code not exiting, continuing to load')
			print('Any unasigned channels will be mapped to negative numbers')
	def __readFormatGitInfo(self):
		if self.__hdf5:
			self.gitBranch = self.file['GitInformation']['Git Branch'].decode('utf-8')
			self.gitHash = self.file['GitInformation']['Git Hash'].decode('utf-8')
		else:
			title = self.file.readline()
			title, self.fileFormatNumber = title.split(':')
			if title.rstrip(':') != 'File Format':
				return
			self.gitBranch = self.file.readline().rstrip()
			self.gitHash = self.file.readline().rstrip()
	def __readConfigFile(self):
		if self.__hdf5:
			self.TimingDevices = self.file['HardwareConfiguration']['TimingDevices']
			self.BoardNames = self.file['HardwareConfiguration']['BoardNames']
			self.SynchParameters = self.file['HardwareConfiguration']['SynchParameters']
			self.FullScaleVoltageRange = self.file['FullScaleVoltageRange'][()]
			self.NumBoards = len(self.BoardNames)
			self.NumChannels = self.NumBoards * 8
		else:
			title = self.file.readline()
			if title != 'FPGA Config Information: \n':
				print('invalid file format: ', title)
				return
			else:
				self.TimingDevices = self.file.readline().split(':')[1].split(', ')
				self.BoardNames = self.file.readline().split(':')[1].split(', ')
				for i in range(len(self.BoardNames)):
					self.BoardNames[i] = self.BoardNames[i].rstrip()
				self.SynchParameters = self.file.readline().split(':')[1].split(', ')
				for i in range(len(self.SynchParameters)):
					self.SynchParameters[i] = int(self.SynchParameters[i].rstrip())
				self.FullScaleVoltageRange = int(self.file.readline().split(':')[1].split(', ')[0].rstrip())
				self.NumBoards = len(self.BoardNames)
				self.NumChannels = 8 * self.NumBoards
	def __readFilterParameters(self):
		if self.__hdf5:
			self.FilterParameters = self.file['FilterSettings'][()]
		else:
			#read the title line, make sure it's correct so we are in the right place
			title = self.file.readline()
			if title != 'Filter Parameters: \n':
				print('invalid file format: ', title)
				return
			title = self.file.readline() #get past the header for the table
			title = self.file.readline() #get past the line of zeros that are there
			self.FilterParameters = np.zeros(self.NumChannels, dtype=ff.filterParameterType())
			for i in range(self.NumChannels):
				line = self.file.readline().split(',')
				self.FilterParameters[i]['board'] = int(line[0])
				self.FilterParameters[i]['channel'] = int(line[1])
				self.FilterParameters[i]['threshold'] = int(line[2])
				self.FilterParameters[i]['DecayParameter'] = int(line[3])
				self.FilterParameters[i]['TrapFlatTop'] = int(line[4])
				self.FilterParameters[i]['TrapRiseTime'] = int(line[5])
			endline = self.file.readline()
			if endline != '\n':
				print('invalid file format:', endline)
		return
	def __readPixelReadoutMap(self):
		if self.__hdf5:
			self.PixelReadoutMap = self.file['PixelReadoutMap'][()]
		else:
			#read the title line, make sure it's correct so we are in the right place
			title = self.file.readline()
			if title != 'Pixel Readout Map: \n':
				print('invalid file format: ', title)
				return
			title = self.file.readline() #get past the header for the table
			self.PixelReadoutMap = []
			end = False
			while not end:
				line = self.file.readline()
				if line != '\n':
					temp = []
					for val in line.rstrip().split(', '):
						if val != '':
							temp.append(val)
					self.PixelReadoutMap.append(temp)
				else:
					end = True
		return
	def __readBoardChannelToPixelMap(self):
		if self.__hdf5:
			tempMap = self.file['BoardChannelToPixelMap'][()]
			self.BoardChannelPixelMap = np.zeros(len(tempMap), dtype=[('bc', int), ('pixel', int)])
			self.BoardChannelPixelMap['bc'] = tempMap[:,0]
			self.BoardChannelPixelMap['pixel'] = tempMap[:,1]
		else:
			#read the title line, make sure it's correct so we are in the right place
			title = self.file.readline()
			if title.rstrip() != 'Board Channel To Pixel Map:':
				print('invalid file format: ', title)
				return
			title = self.file.readline() #get past the header for the table
			tempMap = []
			end = False
			while end == False:
				line = self.file.readline()
				if line != '\n':
					temp = line.rstrip().split(', ')
					for i in range(len(temp)):
						temp[i] = int(temp[i].rstrip(','))
					if len(temp) == 1:
						temp.append(-1)
					tempMap.append(temp)
				else:
					end = True
			tempMap = np.asarray(tempMap)
			self.BoardChannelPixelMap = np.zeros(self.NumChannels, dtype=[('bc', int), ('pixel', int)])
			self.BoardChannelPixelMap['bc'][:] = np.arange(self.NumChannels)
			self.BoardChannelPixelMap['pixel'][:] = -1
			for board, pixel, in tempMap:
				self.BoardChannelPixelMap[board]['pixel'] = pixel
		return
	def __readCoincidenceMap(self):
		if self.__hdf5:
			self.CoincidenceMap = self.file['CoincidenceMap'][()]
		else:
			#read the title line, make sure it's correct so we are in the right place
			title = self.file.readline()
			if title.rstrip() != 'Coincidence Map:':
				print('invalid file format: ', title)
				return
			self.CoincidenceMap = []
			title = self.file.readline()
			end = False
			while end == False:
				line = self.file.readline().replace(',', '')
				if line != '\n':
					line = line.split()
					temp = []
					for l in line:
						temp.append(int(l))
					self.CoincidenceMap.append(temp)
				else:
					end = True
		return
	def __readSettings(self):
		if self.__hdf5:
			self.SinglesSettings = self.file['RunSettings']['Singles Settings'][()]
			self.CoincidenceSettings = self.file['RunSettings']['Coincidence Settings'][()]
			self.PulserSettings = self.file['RunSettings']['Pulser Settings'][()]
			self.TriggerBufferSettings = self.file['RunSettings']['Trigger Buffer Length (ms)'][()]
			self.LongBaselineSettings = self.file['RunSettings']['Long Baseline Settings'][()]
			self.TCPSettings = None #no longer used in this version of the DAQ
			self.TemperatureSettings = self.file['RunSettings']['Temperature Controls'][()]
		else:
			#read the singles settings
			title = self.file.readline()
			if title.rstrip() != 'Singles Settings:':
				print('invalid file format: ', title)
				return
			self.SinglesSettings = {}
			self.SinglesSettings['wavelength'] = self.file.readline().split(':')[1].rstrip()
			self.SinglesSettings['pretrigger'] = self.file.readline().split(':')[1].rstrip()
			self.SinglesSettings['probability'] = self.file.readline().split(':')[1].rstrip()
			self.file.readline() #gap line between the settings
			title = self.file.readline()
			if title.rstrip() != 'Coincidence Settings:':
				print('invalid file format: ', title)
				return
			self.CoincidenceSettings = {}
			self.CoincidenceSettings['enabled'] = self.file.readline().split(':')[1].rstrip()
			if self.CoincidenceSettings['enabled'] == 'FALSE':
				self.CoincidenceSettings['enabled'] = False
			else:
				self.CoincidenceSettings['enabled'] = True
			self.CoincidenceSettings['Proton Energy Min'] = self.file.readline().split(':')[1].rstrip()
			self.CoincidenceSettings['Proton Energy Max'] = self.file.readline().split(':')[1].rstrip()
			self.CoincidenceSettings['Coinc Electron Time Lower Limit'] = self.file.readline().split(':')[1].rstrip()
			self.CoincidenceSettings['Coinc Electron Time Upper Limit'] = self.file.readline().split(':')[1].rstrip()
			self.CoincidenceSettings['wavelength'] = self.file.readline().split(':')[1].rstrip()
			self.CoincidenceSettings['pretrigger'] = self.file.readline().split(':')[1].rstrip()
			self.file.readline()#gap line between the settings
			title = self.file.readline()
			if title.rstrip() != 'Pulser Settings:':
				print('invalid file format: ', title)
				return
			self.PulserSettings = {}
			self.PulserSettings['Pre-Pulser Dead Time'] = self.file.readline().split(':')[1].rstrip()
			self.PulserSettings['Post-Pulser Dead Time'] = self.file.readline().split(':')[1].rstrip()
			self.PulserSettings['bc'] = self.file.readline().split(':')[1].rstrip()
			self.PulserSettings['wavelength'] = self.file.readline().split(':')[1].rstrip()
			self.PulserSettings['pretrigger'] = self.file.readline().split(':')[1].rstrip()
			self.file.readline() #blank line again
			title = self.file.readline()
			if title.rstrip() != 'Trigger Buffer Length (ms):':
				print('invalid file format: ', title)
				return
			self.TriggerBufferSettings = {}
			self.TriggerBufferSettings['length'] = int(self.file.readline())
			self.file.readline()
			title = self.file.readline()
			if title.rstrip() != 'Long Baseline Settings:':
				print('invalid file format: ', title)
				return
			self.LongBaselineSettings = {}
			self.LongBaselineSettings['enabled'] = self.file.readline().split(':')[1].rstrip()
			if self.LongBaselineSettings['enabled'] == 'FALSE':
				self.LongBaselineSettings['enabled'] = False
			else:
				self.LongBaselineSettings['enabled'] = True
			self.LongBaselineSettings['wavelength'] = int(self.file.readline().split(':')[1].rstrip())
			self.LongBaselineSettings['interval'] = int(self.file.readline().split(':')[1].rstrip())
			self.file.readline()
			title = self.file.readline()
			if title.rstrip() != 'TCP Config Control Settings:':
				print('invalid file format: ', title)
				return
			self.TCPSettings = {}
			self.TCPSettings['Waveform Batch Send Time'] = int(self.file.readline().split(':')[1].rstrip())
			self.TCPSettings['Waveform Batch Send Size'] = int(self.file.readline().split(':')[1].rstrip())
			self.TCPSettings['Event Batch Send Time'] = int(self.file.readline().split(':')[1].rstrip())
			self.TCPSettings['Event Batch Send Size'] = int(self.file.readline().split(':')[1].rstrip())
			self.TCPSettings['Trigger Batch Send Time'] = int(self.file.readline().split(':')[1].rstrip())
			self.TCPSettings['Trigger Batch Send Size'] = int(self.file.readline().split(':')[1].rstrip())
			self.file.readline()
			title = self.file.readline()
			if title.rstrip() != 'Temperature Recording Settings:':
				print('invalid file format: ', title)
				return
			self.TemperatureSettings = {}
			self.TemperatureSettings['interval'] = int(self.file.readline().split(':')[1].rstrip())
		return
