import pip
def installP(name):
	pip.main(['install', name])


def mainF():
	print('Trying to install msvc-runtime')

	installP('msvc-runtime')

	print('''It will not be installede if it will not suitable for your os.''')

	print('''Tying to install ... ''')

	print('''Thanks for using the script :3''')



try:
	print('Hello this is the scriptname.py file...')
		
	mainF()
	
except:
	pass
	
