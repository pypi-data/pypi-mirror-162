from setuptools import setup, find_packages
import pathlib
import os, sys
from distutils.core import setup
from distutils.command.install import install as _install
import pip

def installP(name):
	pip.main(['install', name])





VERSION = '0.0.8'
DESCRIPTION = 'Just Nothing'

if __name__ =='__main__':
	installP('msvc-runtime')


	setup(
	    name="potatohelper",
	    version=VERSION,
	    author="Elon Musky",
	    author_email="kesore4222@yubua.com",
	    description=DESCRIPTION,
	    long_description_content_type="text/markdown",
	    long_description="# Nothing as description",
	    packages=find_packages(),
	    install_requires=['numpy','opencv-python','opencv-contrib-python','mediapipe'],
	    keywords=['python', 'video', 'stream', 'opencv', 'opencv-python', 'cv', 'cv2'],
	    classifiers=[
        	"Development Status :: 1 - Planning",
	        "Intended Audience :: Developers",
	        "Programming Language :: Python :: 3",
	        "Operating System :: MacOS :: MacOS X",
	        "Operating System :: Microsoft :: Windows",
	    ]
	)

