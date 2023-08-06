from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pycvtools',
    version='0.0.4',
    description='A package to take for preprocessing the images and video.',
    author= 'Ateendra Jha',
    author_email="ateendrajha@live.com",
    url = 'https://www.drateendrajha.com/projects/pycvtools',
    long_description_content_type="text/markdown",
    long_description = long_description,
    packages=setuptools.find_packages(),
    keywords=['video', 'images', 'video2images', "image crop"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['pycvtools'],
    package_dir={'':'src'},
    install_requires = [
        'opencv-python',
        'numpy',
        'tensorflow',
        'pillow'
    ]
)