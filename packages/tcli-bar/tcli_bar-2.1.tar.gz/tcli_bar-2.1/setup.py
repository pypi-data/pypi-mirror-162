from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='tcli_bar',
    version='2.1',
    description='Create a CLI progress bar for your python project\nDon’t forget to add a new line after you add the progress bar You can find out why ;)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SiXFeet",
    author_email='chukunekunwanwene@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    
    py_modules=['tcli_bar'],
    keywords='cli loading bar',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'colorama',
      ],
)
