'''
This file defines the different file formats. Both dataFile and resultFile classes will reference
these for the header file types and whatnot.
'''

import numpy as np
from . import basicFunctions as bf

def readFileHeader(file, formatVersion):
	if formatVersion == 0:
		#grab the git branch name size
		gitBranchNameSize = np.fromfile(file, dtype=np.int32, count=1)[0]
		strbits = np.fromfile(file, dtype=np.int8, count=gitBranchNameSize)
		gitBranchName = ''.join([chr(item) for item in strbits])
		gitBranchHashSize = np.fromfile(file, dtype=np.int32, count=1)[0]
		strbits = np.fromfile(file, dtype=np.int8, count=gitBranchHashSize)
		gitBranchHash = ''.join([chr(item) for item in strbits])
		return gitBranchName, gitBranchHash
	else:
		print("file version not supported yet")
		return

def readFileHeader(file, fileFormat = 'Nab', waveformfile = False, overwriteFileFormat = None):
	'''
	This function reads the reader from the data file and parses it
	
	Parameters
	----------
	file: file object
	
	fileFormat: string, defaults to 'Nab'
		The format of the file
		Supported options: 'Nab', 'LANL2019', 'Ca45'
			Must match cases
	
	waveformFile: bool, defaults to False
		Specifies if the file is a waveform file or not
		Those files have extra pretrigger length information
	
	overwriteFileFormat: list of length 3, defaults to None
		If this is passed, this overwrites the file format information and forces the code to do something different
		element 0:
			the length of the file header
		element 1:
			the format of the datafile
		element 2:
			If a waveform file, element 2 is the pretrigger length
			If not a waveform file, element 2 isn't passed
	
	Returns
	-------
	header length: int
		The length of the file header to be skipped past when reading in the rest of the data
	file header: dictionary
		A dictionary containing the information read from the file header
			The data contained in this dictionary varies with the file format
	'''
	headerOut = {}
	file.seek(0)
	if overwriteFileFormat is not None:
		#if this is passed to the function, then completely ignore whatever is in the file
		#and just "trust" this format
		headerOut['file format'] = 'custom'
		if len(overwriteFileFormat) == 3: 
			headerOut['pretrigger'] = overwriteFileFormat[2]
		return overwriteFileFormat[0], None
	if fileFormat == 'Nab':
		headerOut['file format'] = np.fromfile(file, dtype = np.uintc, count = 1)[0] #file format, 4 bytes
		headerOut['file header size'] = np.fromfile(file, dtype = np.uintc, count = 1)[0] #file header size
		if headerOut['file format'] == 0 or headerOut['file format'] == 1:
			seekAmount = 8 + headerOut['file header size'] #seek amount definition
			headerOut['git branch string length'] = np.fromfile(file, dtype = np.uintc, count = 1)[0] #git branch string length, 11
			headerOut['git branch string'] = bf.convertBinaryString(np.fromfile(file, dtype = 'S1', count = headerOut['git branch string length'])) #git branch string
			headerOut['git branch hash length'] = np.fromfile(file, dtype = np.uintc, count = 1)[0] #git branch hash length
			headerOut['git branch hash'] = bf.convertBinaryString(np.fromfile(file, dtype = 'S1', count = headerOut['git branch hash length'])) #git branch hash string
			headerOut['labview timestamp (s)'] = np.fromfile(file, dtype = 'u8', count = 1)[0] #first part of the labview timestamp
			headerOut['labview timestamp (extra part)'] = np.fromfile(file, dtype = 'u8', count = 1)[0] #second part of labview timestamp
			headerOut['fpga timestamp'] = np.fromfile(file, dtype = 'u8', count = 1)[0] #fpga timestamp
			if waveformfile:
				headerOut['pretrigger'] = np.fromfile(file, dtype='i2', count = 1)[0] #pretrigger offset
			return seekAmount, headerOut
		elif headerOut['file format'] == 2:
			seekAmount = 8 + headerOut['file header size'] #seek amount definition
			headerOut['git branch string length'] = np.fromfile(file, dtype = np.uintc, count = 1)[0] #git branch string length, 11
			headerOut['git branch string'] = bf.convertBinaryString(np.fromfile(file, dtype = 'S1', count = headerOut['git branch string length'])) #git branch string
			headerOut['git branch hash length'] = np.fromfile(file, dtype = np.uintc, count = 1)[0] #git branch hash length
			headerOut['git branch hash'] = bf.convertBinaryString(np.fromfile(file, dtype = 'S1', count = headerOut['git branch hash length'])) #git branch hash string
			headerOut['unix timestamp'] = np.fromfile(file, dtype = 'u8', count = 1)[0] #utc timestamp
			headerOut['fpga timestamp'] = np.fromfile(file, dtype = 'u8', count = 1)[0] #fpga timestamp
			if waveformfile:
				headerOut['pretrigger'] = np.fromfile(file, dtype='i2', count = 1)[0] #pretrigger offset
			return seekAmount, headerOut
		elif headerOut['file format'] == 3:
			seekAmount = 8 + headerOut['file header size'] #seek amount definition
			headerOut['git branch string length'] = np.fromfile(file, dtype = np.uintc, count = 1)[0] #git branch string length, 11
			headerOut['git branch string'] = bf.convertBinaryString(np.fromfile(file, dtype = 'S1', count = headerOut['git branch string length'])) #git branch string
			headerOut['git branch hash length'] = np.fromfile(file, dtype = np.uintc, count = 1)[0] #git branch hash length
			headerOut['git branch hash'] = bf.convertBinaryString(np.fromfile(file, dtype = 'S1', count = headerOut['git branch hash length'])) #git branch hash string
			headerOut['unix timestamp'] = np.fromfile(file, dtype = 'u8', count = 1)[0] #utc timestamp
			headerOut['fpga timestamp'] = np.fromfile(file, dtype = 'u8', count = 1)[0] #fpga timestamp
			if waveformfile:
				headerOut['pretrigger'] = np.fromfile(file, dtype='i2', count = 1)[0] #pretrigger offset
			return seekAmount, headerOut
		else:
			print('unrecognized format: readFileHeader()')
			return 0, []
	elif fileFormat == 'LANL2019':
		headerOut['file format'] = 'LANL2019'
		headerOut['pretrigger'] = None
		return 0, headerOut
	elif fileFormat == 'Ca45':
		headerOut['file format'] = 'Ca45'
		headerOut['unix timestamp'] = np.fromfile(file, dtype=np.double, count=1)[0]
		headerOut['pretrigger'] = 1000
		return 8, headerOut
		

def triggerType(version = 'reading'):
	if version == 'reading':
		return [('timestamp', 'u8'), ('bc', 'u1'), ('energy', 'u2')]
	elif version == 'processing':
		return [('timestamp', 'u8'), ('bc', 'i4', 2), ('energy', 'u2')]
	elif version == 'event':
		return [('timestamp', 'u8'), ('bc', 'u1'), ('energy', 'u2'), ('numNeighbors', 'i4')]
	else:
		print('unrecognized option: use either reading or processing')
		return
	return

def eventNeighborType():
	return [('trigger', triggerType('event')), ('neighbors', 'O')]

def neighborType(num):
	return [('neighbor', 'u1', num)]

def eventHeader():
	return [('type', 'i4'), ('uuid', 'u4'), ('wavelength', 'u2'), ('numtrigs', 'u4')]

def eventType():
	return [('header', eventHeader()), ('triggers', 'O'), ('baselineTimestamp', 'u8')]

def temperatureType():
	return [('board', 'i4'), ('timestamp', 'u8'), ('AlTemp', 'f4'), ('FPGATemp', 'f4'), ('Basecard0Temp', 'f4'), ('Basecard1Temp', 'f4')]

#the waveform header format
def headerType(fileFormat = 'Nab', formatNumber = None):
	if fileFormat == 'Nab':
		if formatNumber is not None:
			if formatNumber == 0:
				return [('result','u1'), ('eventid', 'u4'), ('board', 'i4'), ('channel', 'i4'), ('timestamp', 'u8'), ('req', 'u8'), ('length', 'i4')]
			elif formatNumber == 1 or formatNumber == 2:
				return [('result','u1'), ('eventid', 'u4'), ('bc', 'u1'), ('timestamp', 'u8'), ('req', 'u8'), ('source', 'u2'), ('length', 'i4')]
			elif formatNumber == 3:
				return [('result','u1'), ('eventid', 'u4'), ('eventtype', 'u1'), ('hittype', 'u1'), ('bc', 'u1'), ('timestamp', 'u8'), ('req', 'u8'), ('length', 'i4')]
			elif formatNumber == 4:
				headertype = []
				headertype.append(('result', '<u1'))
				headertype.append(('bc', '<u1'))
				headertype.append(('timestamp', '<u8'))
				headertype.append(('req', '<u8'))
				headertype.append(('event type', '<u1'))
				headertype.append(('hit type', '<u1'))
				headertype.append(('blank', '<u2'))
				headertype.append(('eventid', '<u4'))
				return headertype
			else:
				print('unrecognized file format: ', fileFormat, formatNumber)
				return
	elif fileFormat == 'LANL2019':
		return [('result','u1'), ('eventid', 'u4'), ('board', 'i4'), ('channel', 'i4'), ('timestamp', 'u8'), ('length', 'i4')]
	elif fileFormat == 'Ca45':
		return [('result','u1'), ('eventid', 'u4'), ('board', 'i4'), ('channel', 'i4'), ('timestamp', 'u8'), ('req', 'u8'), ('length', 'i4')]
	else:
		print('unrecognized file format: Use either Nab, Ca45, or LANL2019')
		return

#data type for reading in the waveform and it's header
def headWaveType(wavelength, fileFormat = 'Nab', formatNumber = None):
	header = headerType(fileFormat = fileFormat, formatNumber = formatNumber)
	return [('header', header), ('wave', str(wavelength)+'H')]

def headWaveTypeShort(wavelength, fileFormat = 'Nab'):
	return [('header', headerType(fileFormat = fileFormat, formatNumber = formatNumber)), ('wave', str(wavelength)+'h')]

#an older version of this data type
'''
def headWaveType(wavelength, fileFormat = 'LANL2019'):
  return {'names': ['header','wave'], 'formats': [headerType(fileFormat = fileFormat), str(wavelength)+'H']}
'''

#output format from the trapezoidal filter code
def trapResultsType(fileFormat = 'LANL2019', formatNumber = None):
  returnType = headerType(fileFormat = fileFormat, formatNumber = formatNumber)
  returnType.append(('energy','f4'))
  returnType.append(('t0','f4'))
  return returnType

#output format from the fitting code
def fitResultsType(numIdeal, numFilters, fileFormat = 'LANL2019', formatNumber = None, searched = False, debug = False):
	returnType = headerType(fileFormat = fileFormat, formatNumber = formatNumber)
	returnType.append(('energy','f4'))
	if debug:
		returnType.append(('sumEner','f4'))
	returnType.append(('t0','f4'))
	returnType.append(('chisqr','f4'))
	for ideal in range(numIdeal):
		string = 'ideal'+str(ideal)
		returnType.append((string, 'f4'))
	for filt in range(numFilters - numIdeal):
		string = 'filter'+str(filt)
		returnType.append((string, 'f4'))
	if searched:
		returnType.append(('const', 'f4'))
		returnType.append(('linear', 'f4'))
		returnType.append(('quadratic', 'f4'))
	return returnType

def filterParameterType():
	return [('board', 'i4'), ('channel', 'i4'), ('threshold', 'i4'), ('DecayParameter', 'i4'), ('TrapFlatTop', 'i4'), ('TrapRiseTime', 'i4')]

def boardChannelType():
	return [('bc', 'i4'), ('pixel', 'i4')]
