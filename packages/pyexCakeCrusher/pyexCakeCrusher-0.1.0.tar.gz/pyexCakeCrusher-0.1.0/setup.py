from setuptools import setup
setup(
    name='pyexCakeCrusher',
    version='0.1.0',   
    description='A example Python package',
    url='https://github.com/shuds13/pyexample',
    author='Seb',
    author_email='s@s.s',
    license='BSD 2-clause',
    packages=['pyexCakeCrusher'],
    install_requires=['mpi4py>=2.0', 'numpy',],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)