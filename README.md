dplot.py
========

Here is a `dplot` task generator for [NWChem](https://nwchemgit.github.io/).
The input is mostly self explanatory; try the `--help` option. You will need the 
[docopt](https://github.com/docopt/docopt) python package. 
For example, install `docopt` with your favorite python package installer.

`dplot.py` uses an NWChem input file and a `movecs` file with orbital data 
to generate a list of `dplot` task inputs, to create volume data files in the Gaussian
cube format. The molecular coordinates from the input file are used to set up
a suitable numerical grid for the volume data files. You can visualize the resulting
cube-format files with the Mathematica notebooks in [this repository](https://github.com/jautschbach/mathematica-notebooks), for example.
