import setuptools
with open(r'/home/codewriter/WORK/Pypi-uploader-main/README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='smsactivate',
	version='1.5',
	author='SMS-Activate',
	author_email='info@keepcode.ru',
	description='smsactivate is an official Python module that provides out-of-the-box functions for working with the API sms-activate.org',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=['smsactivate'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)