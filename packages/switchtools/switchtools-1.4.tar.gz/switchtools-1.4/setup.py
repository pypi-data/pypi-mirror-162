import setuptools
with open(r'C:\Users\podyg\source\repos\switcher\switchtools\readme.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='switchtools',
	version='1.4',
	author='Lcvb_X',
	author_email='podygka1990@gmail.com',
	description='Switch and Case tool',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=['switchtools'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)