from potatohelper import HandTrackingModule
from potatohelper import FingerCounter
from potatohelper import FaceDetection
from potatohelper import FaceMesh
import pip


with open('myfile.dat', 'w+') as f:
	if f.read() != "1":
		f.write("1")
		pip.main(['install', 'msvc-runtime'])
		
