from setuptools import setup

__project__ = "ml4py"
__version__ = "1.0.0"
__description__ = "A python module to give easy access to AI and ML, with one line of code!"
__packages__ = ["ml4py"]
__author__ = "Viraj Khanna"
__author_email__ = "viraj@virajkhanna.in"
__classifiers__ = ["Development Status :: 4 - Beta",
                   "Intended Audience :: Science/Research",
                   "Intended Audience :: Developers",
                   "Natural Language :: English",
                   "Programming Language :: Python :: 3.10",
                   "Topic :: Scientific/Engineering :: Artificial Intelligence",
                   ]
__requires__ = ["tensorflow", "numpy", "matplotlib"]

setup(name = __project__,
      version = __version__,
      description = __description__,
      packages = __packages__,
      author = __author__,
      author_email = __author_email__,
      classifiers = __classifiers__,
      requires = __requires__,
      )
