#!/usr/bin/env python
""" dplot.py -- A NWChem dplot block generator
Usage:
    dplot.py [options]
        (-i <nwchem.nw> | --input <nwchem.nw>)
        (-m <nwchem.movecs> | --movecs <nwchem.movecs>)
        (-l <mos> | --list <mos> | -d <string> | --density <string>)

Positional Arguments:
    -i, --input <nwchem.nw>         A NWChem input file
    -m, --movecs <nwchem.movecs>    A NWChem movecs file generated from input
    -l, --list <mos>                List of MO's (movecs) or TD's (civecs) to plot
                                        (no spaces allowed, example: 1-4,8-12,6,24)
    -d, --density <string>          Plot the density instead of mos
                                        valid strings include: total, alpha, beta, spin

Options:
    -h, --help                      Print this screen and exit
    -v, --version                   Print the version of dplot.py
    -b, --beta                      Plot beta MOs instead of alpha (not valid with -c/--civecs)
    -a, --alpha-beta                Plot both alpha and beta MOs (not valid with -c/--civecs)
    -c, --civecs <nwchem.civecs>    Print Transition Densities (TD) instead of MOs
    -g, --grid <value>              Change default grid parameter [default=50]
    -e, --extent <value>            Change default extent of box size [default=2.0]
"""


def split_mo_list(mos):
    """
    This function converts a string such as '1-2,7,10-20'
    to a sorted list of integers, then outputs that list
    """
    out = []
    for i in mos.split(","):
        if "-" in i:
            sp = i.split("-")
            [out.append(x) for x in range(int(sp[0]), int(sp[1]) + 1)]
        else:
            out.append(int(i))
    return sorted(out)


def begin_dplot_block(f, args, x, y, z):
    """
    This function writes all necessary info to start a dplot block
    """
    f.write("dplot\n")
    f.write("vectors {0}\n".format(args["--movecs"]))
    f.write("limitxyz\n")
    f.write(
        "{0} {1} {2}\n".format(
            x[0] - args["--extent"], x[1] + args["--extent"], args["--grid"]
        )
    )
    f.write(
        "{0} {1} {2}\n".format(
            y[0] - args["--extent"], y[1] + args["--extent"], args["--grid"]
        )
    )
    f.write(
        "{0} {1} {2}\n".format(
            z[0] - args["--extent"], z[1] + args["--extent"], args["--grid"]
        )
    )
    f.write("gaussian\n")


def end_dplot_block(f):
    """
    This function completes the dplot block
    """
    f.write("end\n")
    f.write("task dplot\n")


# Import various functions and libraries
from docopt import docopt
from sys import exit
from os.path import isfile, splitext


try:
    # docopt parses the command line via the doc string above
    arguments = docopt(__doc__, version="dplot.py version 0.0.1")

    # Input Check 1: Can not use -b/--beta or -a/--alpha-beta with -c/--civecs
    #   No reason to move on if this is incorrect
    if arguments["--civecs"] and (arguments["--beta"] or arguments["--alpha-beta"]):
        raise Exception(
            "Input Error: -b/--beta and -a/--alpha-beta options cannot be used with -c/--civecs option"
        )

    # Input Check 2: does '--input' file exists, if not continue to propmt user until they enter a file that exists
    while True:
        if (
            not isfile(arguments["--input"])
            or splitext(arguments["--input"])[-1] != ".nw"
        ):
            arguments["--input"] = input(
                (
                    "'{0}' does not exist or does not have the expected file extension!\n"
                    + "Please enter an appropriate input file to continue, or try '-h/--help' option:\n"
                ).format(arguments["--input"])
            )
        else:
            break

    # Input Check 3: does '--movecs' file exists, if not continue to propmt user until they enter a file that exists
    while True:
        if (
            not isfile(arguments["--movecs"])
            or splitext(arguments["--movecs"])[-1] != ".movecs"
        ):
            arguments["--movecs"] = input(
                (
                    "'{0}' does not exist or does not have the expected file extension!\n"
                    + "Please enter an appropriate movecs file to continue, or try '-h/--help' option:\n"
                ).format(arguments["--movecs"])
            )
        else:
            break

    # Input Check 4: Conditional, if user wants civecs analysis
    #   does '--civecs' file exist, if not continue to prompt user until they enter a file that exists
    if arguments["--civecs"]:
        while True:
            if not isfile(arguments["--civecs"]) or splitext(arguments["--civecs"])[
                -1
            ] not in [".civecs_singlet", ".civecs_triplet"]:
                arguments["--civecs"] = input(
                    (
                        "'{0}' does not exist or does not have the expected file extension!\n"
                        + "Please enter an appropriate civecs file to continue, or try '-h/--help' option:\n"
                    ).format(arguments["--civecs"])
                )
            else:
                break

    # Input Check 5: Set default grid value if necessary
    if not arguments["--grid"]:
        arguments["--grid"] = "50"

    # Input Check 6: Set default extent value if necessary, also convert to float
    #  if you cannot we need to exit
    try:
        if arguments["--extent"]:
            arguments["--extent"] = float(arguments["--extent"])
        else:
            arguments["--extent"] = 2.0
    except ValueError:
        raise Exception(
            "Extent Error: The '-e/--extent' option accepts a float value only!"
        )

    # Input Check 7: Is density switch set, if yes is it a valid string?
    if arguments["--density"] and arguments["--density"] not in [
        "total",
        "alpha",
        "beta",
        "spin",
    ]:
        raise Exception(
            "Density Error: {} is not a valid option, try -h/--help".format(
                arguments["--density"]
            )
        )

    # Input file exists, let's read it
    with open(arguments["--input"], "r") as f:
        lines = f.readlines()

    # We are now in a position to parse the input file:
    #   The only information we need is the geometry to calculate the output cube size
    #   We will use a boolean 'read' to indicate when we should add coordinates
    #   x, y, and z will contain the geometric coordinates of our system
    read = False
    x, y, z = [], [], []
    for i in range(0, len(lines)):
        if "geometry" in lines[i]:
            read = True
        elif "end" in lines[i]:
            read = False
        if read:
            try:
                sp = lines[i].split()
                x.append(float(sp[1]))
                y.append(float(sp[2]))
                z.append(float(sp[3]))
            except (ValueError, IndexError):
                pass

    # We now need to get min and max for each coordinate
    x = [min(x), max(x)]
    y = [min(y), max(y)]
    z = [min(z), max(z)]

    # We are now in a position to write the 'dplot.nw' file
    with open("dplot.nw", "w") as f:
        # first we add copy the '--input' file to dplot.nw but comment any task directives
        for i in lines:
            if "task" in i:
                f.write("#" + i)
            else:
                f.write(i)

        # now we can add the dplot blocks!
        #   --> if '--density' is set, we will only process one block
        #   --> need some logic here for the '--alpha-beta' and '--beta' options
        base = splitext(arguments["--input"])[0]
        if arguments["--density"]:
            f.write("\n")
            begin_dplot_block(f, arguments, x, y, z)
            # I hate using the full spindens as an argument, therefore I deal
            #   with the spin case separately (mainly the output format looks like
            #   base-spindens-dens.cube i.e. dumb)
            if arguments["--density"] == "spin":
                f.write("spin spindens\n")
            else:
                f.write("spin {}\n".format(arguments["--density"]))
            f.write("output {}-{}-dens.cube\n".format(base, arguments["--density"]))
            end_dplot_block(f)
        else:
            mos = split_mo_list(arguments["--list"])
            if arguments["--alpha-beta"]:
                for spin in ["alpha", "beta"]:
                    for i in mos:
                        f.write("\n")
                        begin_dplot_block(f, arguments, x, y, z)
                        f.write("spin {}\n".format(spin))
                        f.write("orbitals view;1;{}\n".format(i))
                        f.write("output {}-{}-{}.cube\n".format(base, spin, i))
                        end_dplot_block(f)
            elif arguments["--beta"]:
                spin = "beta"
                for i in mos:
                    f.write("\n")
                    begin_dplot_block(f, arguments, x, y, z)
                    f.write("spin {}\n".format(spin))
                    f.write("orbitals view;1;{}\n".format(i))
                    f.write("output {}-{}.cube\n".format(base, i))
                    end_dplot_block(f)
            elif arguments["--civecs"]:
                for i in mos:
                    f.write("\n")
                    begin_dplot_block(f, arguments, x, y, z)
                    f.write("root {}\n".format(i))
                    f.write("output {}-root-{}.cube\n".format(base, i))
                    f.write("civecs {}\n".format(arguments["--civecs"]))
                    end_dplot_block(f)
            else:
                spin = "alpha"
                for i in mos:
                    f.write("\n")
                    begin_dplot_block(f, arguments, x, y, z)
                    f.write("spin {}\n".format(spin))
                    f.write("orbitals view;1;{}\n".format(i))
                    f.write("output {}-{}.cube\n".format(base, i))
                    end_dplot_block(f)

# Some common exceptions
except KeyboardInterrupt:
    exit("Interrupt Detected! exiting...")

except SystemExit:
    print("==> Input Error: Printing usage, or see documentation! <==")
    print(__doc__)

except Exception as e:
    print(e)
