from setuptools import setup,find_packages
 
setup(name='prayuth_package',
      version='0.4',
      description='This is prayuth_package.',
      url='https://github.com/sineck/prayuth_package.git',
      author='Pornchai_A',
      author_email='pornchai.puj@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires= ['numpy==1.21.6','pandas==1.3.5,<=1.3.5'],
      python_requires='>=3.8',
      zip_safe=False)