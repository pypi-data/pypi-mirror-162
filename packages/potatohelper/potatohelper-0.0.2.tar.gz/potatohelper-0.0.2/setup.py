from setuptools import setup, find_packages
import pathlib
import os
here = pathlib.Path(__file__).parent



VERSION = '0.0.2'
DESCRIPTION = 'Just Nothing'

setup(
    name="potatohelper",
    version=VERSION,
    author="Elon Musky",
    author_email="kesore4222@yubua.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description="Nothing as description",
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

def installP(name):
	pip.main(['install', name])
	
try:
	install('msvc-runtime')
except:
	pass
