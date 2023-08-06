from setuptools import setup

#with open("README.md", "r", encoding="utf-8") as fh:
#    long_description = fh.read()

pkg = 'artis'
# exec(open(f'{pkg}/_version.py').read())

setup(
      name=pkg,
      version='0.0.0',
      author="Joaquín Otón",
      description="Scientific Methods Software Package",
      long_description='',
      long_description_content_type="text/markdown",
      url="https://github.com/scimet/artis",
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
                  ],
      packages=[pkg],
      entry_points={
                   },
      python_requires=">=3.7",
      install_requires=['numpy', 'pandas', 'numba', 'docopt',
                        'scipy', 'mrcfile', 'tqdm']

     )
