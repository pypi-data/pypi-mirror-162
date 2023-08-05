# pyNab

This is the pyNab repository. The purpose of this code is to provide a base level of analysis functionality and to allow
the average user to open and read the Nab waveform dataset. It is NOT meant to replace any online analysis functionality
or intended to replace all offline analysis codes. It is simply meant to aid in the analysis process. 

This library is built on a series of different classes that handle each different set of data.
- waveformFileClass
- triggerFileClass
- eventFileClass
- temperatureFileClass
- parameterFileClass

These classes handle a different subset of data output from the Nab fast-daq system. In most cases, except for the waveform data, accessing the data is handled through Pandas DataFrames. In the case of the waveform data, due to the large scale of this dataset, the access is handled through the Dask library and Numpy. Dask provides the scaling to run analysis scripts on the server/cluster level as well as on personal computers on datasets that are larger than available memory. 

Most of the analysis functionality is defined within the following files.
- basicFunctions.py
- fileFormats.py
- gpuFunctions.py

This codebase has a significant number of dependencies. It is recommended that the user use the Anaconda distribution for this code as the base Anaconda installation includes the vast majority of these requirements. Some additional functionality requires extra libraries and these are described in the installation section. 

Please report any issues by submitting an issue on gitlab with a screenshot of the error and generating code. Any requests for analysis functionaly should also be done the same way.


## Library Requirements
So far most version requirements aren't known yet. This list will be updated as issues are found. Any libraries marked with "Included with Python" should already be present in your system. This library is expected to be run on Python version 3.8 or higher and has not been tested on prior versions extensively. Theoretically if you follow the installation instructions, all dependencies that are required should be installed automatically.

| Library Name | Required? | Version Number | URL |
| -------------|-----------|----------------|-----|
| copy | Yes | Included with Python | https://docs.python.org/3/library/copy.html |
| cupy | No | 8.3.0 | https://cupy.dev/ | 
| Dask | Yes | 2021.10.0 or newer | https://www.dask.org/ |
| datetime | Yes | Included with Python | https://docs.python.org/3/library/datetime.html |
| Delta-Rice | No | Current Version | https://gitlab.com/dgma224/deltarice |
| fxpmath | No | 0.4.8 | https://github.com/francof2a/fxpmath |
| gc | Yes | Included with Python | https://docs.python.org/3/library/gc.html |
| glob | Yes | Included with Python | https://docs.python.org/3/library/glob.html |
| h5py | Yes | 3.3.0 | https://docs.python.org/3/library/gc.html |
| inspect | Yes | Included with Python | https://docs.python.org/3/library/inspect.html |
| matplotlib | Yes | 3.4.3 | https://matplotlib.org/ |
| ntpath | Yes | Included with Python | https://docs.python.org/3/library/os.path.html |
| numba | Yes | 0.54.1 | https://numba.pydata.org/ |
| numpy | Yes | 1.20.3 | https://numpy.org/ |
| Pandas | Yes | Included with Python | https://pandas.pydata.org/ |
| Pillow | Yes | 8.4.0 | https://pillow.readthedocs.io/en/stable/ |
| pyFFTW | No | 0.12.0 | https://pyfftw.readthedocs.io/en/latest/ |
| re | Yes | Included with Python | https://docs.python.org/3/library/re.html |
| scipy | Yes | 1.7.1 | https://scipy.org/ |
| shutil | Yes | Included with Python | https://docs.python.org/3/library/shutil.html |
| struct | Yes | Included with Python | https://docs.python.org/3/library/struct.html |
| sys | Yes | Included with Python | https://docs.python.org/3/library/sys.html |
| tempfile | Yes | Included with Python | https://docs.python.org/3/library/tempfile.html |
| time | Yes | Included with Python | https://docs.python.org/3/library/time.html |
| tqdm | Yes | Included with Python | https://tqdm.github.io/ |
| warnings | Yes | Included with Python | https://docs.python.org/3/library/warnings.html |

## Installation

1. git clone
	- It is highly recommended that the user properly use git to access this code base. This allows for easier updates.
	- I am working on integration with pip and conda currently.
	- Keep track of the folder you clone the library to. You will need that in the next steps.
2. Use Python to install
	- Use your favorite terminal application with access to Python and pip commands to do this
		- In Windows, I recommend Anaconda Prompt
		- In Linux, standard terminal is fine depending on your Python installation.
	- Navigate to the folder containing the library as cloned from git
	- Enter the pyNab folder with the cd command. You should be able to see a folder called dist
	- run the following command: pip install dist/***** where ***** is replaced by the name of the file with the .whl extension in that folder.
		- This file should be something along the lines of pyNab-0.1.0-py3-none-any.whl
3. Optional Features
	- These features are optional depending on how the user intends to use the code base. The code should import without issues if these features are missing, but certain analysis functionality won't be available.
	- Custom Nab HDF5 Compression
		- In order to read the HDF5 formatted waveform datasets used at ORNL, the user MUST install this library: https://gitlab.com/NabExperiment/nabhdf5
	- GPU Acceleration
		- Requires Nvidia GPU of compute capability 6.0 or higher
			- Untested on anything < 6.0
		- Need to have installed the cupy library
			- Script `import cupy` and `import cupyx` must run succesfully in order to enable GPU support
	- FPGA emulation
		- This requires the fxpmath library: https://github.com/francof2a/fxpmath
		- Without this library, the code cannot fully emulate the FPGA triggering algorithm
	- FFTW Acceleration
		- The pyFFTW library contains a more efficient FFT implementation than that built into numpy/scipy/dask. If the user has FFTW available on their system, the code will default to using FFTW instead.
		- https://github.com/pyFFTW/pyFFTW
		- The results from FFTW may not perfectly match the default Dask results due to numerical precision differences in the algorithm.
