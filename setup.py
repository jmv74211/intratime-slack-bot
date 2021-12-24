from setuptools import setup, find_namespace_packages
import shutil
import glob

setup(name='clockzy',
      version='3.0',
      description='Application for clocking via slack commands',
      url='https://github.com/jmv74211/clockzy',
      author='jmv74211',
      author_email='jmv74211@gmail.com',
      license='GPLv3',
      package_dir={"": "src"},
      packages=find_namespace_packages(where="src"),
      zip_safe=False)

# Clean build files
shutil.rmtree('dist')
shutil.rmtree('build')
shutil.rmtree(glob.glob('src/*.egg-info')[0])
