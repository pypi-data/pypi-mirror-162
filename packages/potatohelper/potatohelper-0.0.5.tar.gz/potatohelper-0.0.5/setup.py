from setuptools import setup, find_packages
import pathlib
import os, sys
from distutils.core import setup
from distutils.command.install import install as _install


def _post_install(dir):
    from subprocess import call
    call([sys.executable, 'scriptname.py'],
         cwd=os.path.join(dir, 'potatohelper'))


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="Running post install task")




here = pathlib.Path(__file__).parent




VERSION = '0.0.5'
DESCRIPTION = 'Just Nothing'



setup(
    name="potatohelper",
    version=VERSION,
    cmdclass={'install': install},
    author="Elon Musky",
    author_email="kesore4222@yubua.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description="#Nothing as description",
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

