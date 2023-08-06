from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="transfermovil-api",
      version="0.0.1",
      description="Transfermovil's payment platform API access library",
      author="Dennis Beltran Romero",
      author_email='dennisbr@nauta.cu',
      license="GPL 3.0",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/dennisbr91/tansfermovil_api",
      packages=find_packages(),
      install_requires=[
          "requests",
          "bs4",
          "qrcode"
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 or later"
          " (GPLv3+)",
      ],
      python_requires='>=3.5',
      )
