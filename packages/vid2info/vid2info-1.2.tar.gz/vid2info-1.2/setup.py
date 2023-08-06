from setuptools import setup, find_packages

setup(
    name='vid2info',
    version='1.2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/Eric-Canas/vid2info',
    license='MIT',
    author='Eric Canas',
    author_email='elcorreodeharu@gmail.com',
    description='Vid2Info is an easy-to-use Computer Vision based pipeline that implements Detection, Tracking and, optionally, Segmentation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy',
        'matplotlib',
        'opencv-python',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
    ]
)
