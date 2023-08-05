import setuptools

setuptools.setup(
	name = 'nabPy',
	version='0.1.56',
	description='Python Library for the Nab Experiment',
	author='David Mathews',
	author_email='david.mathews.1994@gmail.com',
	license='MIT',
	url='https://gitlab.com/NabExperiment/pyNab/',
	package_dir={"": "src"},
	packages=setuptools.find_packages(where="src"),
	install_requires=[
		'dask',
		'h5py', 
		'matplotlib', 
		'numba', 
		'numpy', 
		'pillow', 
		'scipy',
		'pandas',
		'bokeh',
		'tqdm'],
	python_requires=">=3.6",
)
