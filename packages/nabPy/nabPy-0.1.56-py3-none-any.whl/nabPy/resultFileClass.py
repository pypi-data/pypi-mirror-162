'''
This is a script that defines the result file class that can be utilized for 
most of the analysis for the Nab experiment. The purpose of this class is to
make opening and analysis of output files from the GPU server easier.

This class can open and analyze results from both Nab and Ca45 data file formats.

It is also capable of handling files from the trapezoidal filter and from
the fitting code, though the capabilities may be different.

'''
#import the required libraries
import numpy as np
import dask.dataframe as dd
import os
import struct
import matplotlib.pyplot as plt

from . import fileFormats as ff
from . import basicFunctions as bf

#test

#now define the class itself
class resultFile:
	def __init__(self, fileName = None, data = None, debug = False, mapping = None, fileFormatNumber = None):
		self.fileFormatNumber = fileFormatNumber
		self.__debug = debug
		if fileName is None:#in this case we don't read in the data from a file, we take it from the data passed in
			if data is None: #uhhh then this is garbage
				print('needs either fileName or data to be passed')
				return None
			else:
				#in this case data was passed, just need to pack it up and parse it
				self.__files = data
		else:
			#save the name of the file
			self.fileName = fileName
			#open the file and figure out that information
			self.__openFile()
			#with the file open, go ahead and determine the boards and channel
			#in this file along with how many events are on each one
		self.__pixelMap = mapping
		self.__getFileInfo()
		#determine the categories that are present and allowed for cutting on
		self.names = self.__files.dtypes.index.values
		#the containers for the cuts
		#one specifies what was done during the cut, basically defines the operations
		#the other is the map of the cut itself on the data, a truth array
		self.__cutDefinitions = [] #defines the operations
		self.__currentCut = self.__files.index.values #the map of the current cut on the data, updated by each function call, initilized to all included
	#this function opens the result file
	def __openFile(self):
		#check if the file is from trapezoidal filter, or from fitting
		fileNameStart, self.__extension = os.path.splitext(self.fileName)
		file = open(self.fileName, mode='rb')
		#check if it came from nab or from ca45
		byte = file.read(4)
		nabOrCa45 = struct.unpack('I',byte)[0]#read it as a signed integer
		#if this is a 0, means Nab
		self.fileFormat = 'Nab'
		self.searched = False
		if nabOrCa45 == 2 or nabOrCa45 == 3: #check to see if the searchRange parameter was non-zero or not
			self.searched = True
		if nabOrCa45 == 1 or nabOrCa45 == 3:#ca45 format
			#read past the next 8 bytes, we don't care about those
			_ = file.read(8)
			self.fileFormat = 'Ca45'
		#now do something different depending on if the file is .trapres or .fitres	
		if self.__extension=='.trapres':
			self.__dtype = ff.trapResultsType(fileFormat = self.fileFormat, fileFormatNumber = self.fileFormatNumber)
			#now read in the data
			self.__files = dd.from_array(np.memmap(file, dtype=self.__dtype, count = -1))
		elif self.__extension == '.fitres':
			#now determine how many fit functions of each type there were
			byte = file.read(4)
			numIdealPulse = struct.unpack('i',byte)[0]
			byte = file.read(4)
			numFitTotal = struct.unpack('i',byte)[0]
			#now set up the fit results data type
			self.__dtype = ff.fitResultsType(numIdealPulse, numFitTotal, fileFormat = self.fileFormat, fileFormatNumber = self.fileFormatNumber, searched = self.searched, debug = self.__debug)
			self.__files = dd.from_array(np.memmap(file, dtype=self.__dtype, count = -1))
		#close the input file
		file.close()
	#this grabs the information regarding what boards and channels were present
	#how many triggers each one had
	#and how many triggers there were total
	def __getFileInfo(self):
		#how many waveforms were there
		self.numWaves = len(self.__files)
		#what boards and channels are present
		#also determines how many counts each one had
		self.bcs, self.trigCount = np.unique(self.__files['bc'], axis=0, return_counts = True)
	#this function returns a copy of the original file
	def files(self):
		"""
		Returns the full original file as a Pandas DataFrame
		"""
		return self.__files
	def data(self):
		"""
		This returns the data stored in this class after all of the cuts have been applied.
		It returns the data as a dask DataFrame.
		"""
		return self.files().loc[self.returnCut(),:]
	def addColumn(self, name, data, overwite = True):
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
				temp = np.zeros(len(self.data(orig=True)), dtype=data.dtype)
				temp[:] = np.nan
				temp[self.data().index] = data[:]
				self.__files[name] = temp[:]
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
		self.__currentCut = self.files().index.values
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
	#now define all the plotting routines
	def hist(self, category, bins, norm = None, **kwargs):
		histogram, bin_edges = np.histogram(self.data()[category], bins = bins)
		width = bin_edges[1]-bin_edges[0]
		if norm is not None:
			histogram = histogram / norm
		plt.step(bin_edges[:-1], histogram, where='post', **kwargs)
		return histogram, bin_edges
	def fitHist(self, category, bins, function = None, rounding = None, p0=None, bounds=None, parameterNames = None, **kwargs):
		"""
		This fits one category of data to an arbitrary fit function. 
		If no arbitrary fit function is provided it will just fit to a gaussian instead.
		It returns the fit parameters to the user and also prepares a plot with the fit
			overlayed on the dataset.
		This function effectively wraps around the scipy.curve_fit function so for details
			on how the fits are implemented read the scipy documentation. They also have 
			examples on defining custom fit functions that are helpful.
		
		Parameters
		----------
		category: str
			the category of the data to be fit on
		bins: np.ndarray or list
			A list of x coordinates to fit over. This defines the fit window.
		function: None, or function
			This defines the fit function that will be used.
			If None, it defaults to a gaussian
		rounding: 'int' or int
			If the user passes 'int', it rounds values to an integer
			If the user passes an actual integer such as 1, it rounds to that number of 
				decimal places
		p0: list
			The initial guesses at the fit parameters. This isn't necessary but highly recommended.
			They need to be in the same order in the list as they are defined in the function.
			In the case of the gaussian, the order is [amplitude, mean, sigma, offset]
				Where offset is a constant offset from 0
		bounds: list
			The bounds of the fit. See the scipy.curve_fit function for more details
				on the implementation of this function
		parameterNames: list[string]
			A list of strings that define the names of the parameters. This is used for
				making the legend on the plot. If no parameters are passed the function
				will use p0, p1, p2, p3, etc to describe the fit parameters.
		**kwargs:
			Input for generic plotting kwargs, not for the scipy.curve_fit
		
		Returns
		-------
		popt: the optimal fit parameters in a list in order of definition in the function
			If the fit fails this returns None
		pcov: the covariance matrix for those fit parameters
			If the fit fails this returns None
			See scipy.curve_fit for more details on these values
		"""
		histogram, bin_edges = np.histogram(self.data()[category], bins = bins)
		width = bin_edges[1]-bin_edges[0]
		if function is None:
			function = bf.gaussian
		fitres = bf.fitFunction(bin_edges[:-1]+width/2, histogram, function = function, p0=p0, bounds=bounds)
		if fitres[0] is not None and fitres[1] is not None:
			popt, pcov = fitres
			if popt is not None and pcov is not None:
				vals = []
				for val in popt:
					if rounding is None:
						vals.append(val)
					elif rounding =='int':
						vals.append(int(val))
					else:
						vals.append(round(val, rounding))
				label=''
				for i in range(len(vals)):
					if parameterNames is None:
						label+= 'p'+str(i)+': '+str(vals[i])+'\n'
					else:
						label+=parameterNames[i]+': '+str(vals[i])+'\n'
				label=label.strip()
				plt.plot(bin_edges+width/2, function(bin_edges+width/2, *popt), label=label, **kwargs)
				return popt, pcov
			else:
				return None, None
		else:
			return None, None
	def scatter(self, cat1, cat2, **kwargs):
		data = self.data()
		plt.scatter(data[cat1], data[cat2], **kwargs)
	def savefig(self, filename):
		plt.savefig(filename)
	def legend(self, **kwargs):
		plt.legend(**kwargs)
	def xlim(self, low, high, **kwargs):
		plt.xlim(low, high, **kwargs)
	def ylim(self, low, high, **kwargs):
		plt.ylim(low, high, **kwargs)
	def xlabel(self, label, **kwargs):
		plt.xlabel(label, **kwargs)
	def ylabel(self, label, **kwargs):
		plt.ylabel(label, **kwargs)
	def xscale(self, val, **kwargs):
		plt.xscale(val, **kwargs)
	def yscale(self, val, **kwargs):
		plt.yscale(val, **kwargs)
	def title(self, val, **kwargs):
		plt.title(val, **kwargs)
	def show(self, **kwargs):
		plt.show(**kwargs)
