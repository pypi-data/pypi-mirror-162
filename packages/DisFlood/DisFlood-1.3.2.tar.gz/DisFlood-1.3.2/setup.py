import setuptools
with open(r'C:\Users\podyg\Desktop\dsd\DisFlood\readme.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='DisFlood',
	version='1.3.2',
	author='Lcvb_X',
	author_email='podygka1990@gmail.com',
	description='This library for flood to discord',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=['DisFlood'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)