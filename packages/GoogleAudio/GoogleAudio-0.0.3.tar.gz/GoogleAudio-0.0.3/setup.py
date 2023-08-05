import setuptools
from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GoogleAudio", # Replace with your own username
    version="0.0.3",
    license='MIT',
    author="Falahgs.G.Saleih",
    author_email="falahgs07@gmail.com",
    description="Google Colab Microphone Audio Recoring Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/falahgs/",
    packages=find_packages(),
    keywords = ['Google Colab', 'Audio', 'Wav file'],   # Keywords that define your package best
    install_requires=[ 'ffmpeg-python'],
    classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent",],
    python_requires='>=3.6',)