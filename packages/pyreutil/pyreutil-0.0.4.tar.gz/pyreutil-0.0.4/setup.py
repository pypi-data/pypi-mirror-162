from setuptools import setup

with open("README.md",'r') as fh:
    long_description = fh.read()

setup(
    name='pyreutil',
    version=open('VERSION','r').read().strip(),
    author='Michelle Sun',
    author_email='michelle.sun032@icloud.com',
    url='https://github.com/michsun/pyreutil',
    description='Pyreutil is a command line utility to bulk edit plain text files or filenames using regex.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
    packages=['pyreutil'],
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points= {
        'console_scripts': ['pyreutil = pyreutil.__main__:main']
    }
)