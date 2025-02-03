#!/usr/bin/bash

if command -v which nwchem &> /dev/null; then
    echo "Found NWChem."
else
    echo "Please set NWCHEM_TOP/bin/LINUX64 to PATH."
    exit 1
fi

if [ -x ../dplot.py ]; then
        echo "dplot.py has execute permission."
    else
        echo "Please set permision for dplot.py (chmod +x)"
		exit 1
fi

echo ""

echo "-------"
echo "autosym"
nwchem co2_autosym.nw > co2_autosym.out
../dplot.py -i co2_autosym.nw -o co2_autosym.out -m co2_autosym.movecs -l 11 
nwchem dplot.nw > 1.out
echo "-------"
echo "noautosym nocenter"
nwchem co2_noautosym_nocenter.nw > co2_noautosym_nocenter.out
../dplot.py -i co2_noautosym_nocenter.nw -o co2_noautosym_nocenter.out -m co2_noautosym_nocenter.movecs -l 11 
nwchem dplot.nw > 2.out
echo "-------"
echo "noautosym"
nwchem co2_noautosym.nw > co2_noautosym.out
../dplot.py -i co2_noautosym.nw -o co2_noautosym.out -m co2_noautosym.movecs -l 11 
nwchem dplot.nw > 4.out
echo "-------"
echo "nocenter"
nwchem co2_nocenter.nw > co2_nocenter.out
../dplot.py -i co2_nocenter.nw -o co2_nocenter.out -m co2_nocenter.movecs -l 11 
nwchem dplot.nw > 3.out
echo "-------"
echo "noprint"
nwchem co2_noprint.nw > co2_noprint.out
../dplot.py -i co2_noprint.nw -o co2_noprint.out -m co2_noprint.movecs -l 11 
nwchem dplot.nw > 4.out


echo ""
echo ""
echo "Note: For noprint (the same as --output no), no output is used to define limitXYZ."
echo "WARNING is expected. Users need to swap axes manually [autosym] if plots are not as expected."
echo "----------------------------------------------"
echo "It is better to use dplot.py with output file."
