#!/usr/bin/env python3
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
    -o, --output <nwchem.out>       Specify the output file name (auto, set to "no" to disable)
    -b, --beta                      Plot beta MOs instead of alpha (not valid with -c/--civecs)
    -a, --alpha-beta                Plot both alpha and beta MOs (not valid with -c/--civecs)
    -c, --civecs <nwchem.civecs>    Print Transition Densities (TD) instead of MOs
    -g, --grid <value>              Change default grid parameter [default=50]
    -e, --extent <value>            Change default extent of box size [default=2.0]

Note: dplot will find output to define limitXYZ correctly if autosym and center are turned on
"""

def get_limit_xyz_from_output(outfile):
    x_arr=[]
    y_arr=[]
    z_arr=[]
    with open(outfile,'r') as f:
        line=f.readline()
        while "            XYZ format geometry" not in line:
            line=f.readline()
        line=f.readline() # Skip ------------------- line
        line=f.readline() # This line contains number of atoms
        natom=int(line.split()[0])
        line=f.readline() # Skip geometry line
        for i in range(natom):
            line=f.readline()
            x_arr.append(float(line.split()[1]))
            y_arr.append(float(line.split()[2]))
            z_arr.append(float(line.split()[3]))
    return min(x_arr), max(x_arr),min(y_arr),max(y_arr),min(z_arr),max(z_arr)


def split_mo_list(mos):
    '''
    This function converts a string such as '1-2,7,10-20'
    to a sorted list of integers, then outputs that list
    '''
    out = []
    for i in mos.split(','):
        if '-' in i:
            sp = i.split('-')
            [out.append(x) for x in range(int(sp[0]), int(sp[1]) + 1)]
        else:
            out.append(int(i))
    return sorted(out)

def begin_dplot_block(f, args, x, y, z):
    '''
    This function writes all necessary info to start a dplot block
    '''
    f.write('dplot\n')
    f.write('vectors {0}\n'.format(args['--movecs']))
    f.write('limitxyz\n')
    f.write(f'''{x[0]-args['--extent']:.4f} {x[1]+args['--extent']:.4f} {args['--grid']}\n''')
    f.write(f'''{y[0]-args['--extent']:.4f} {y[1]+args['--extent']:.4f} {args['--grid']}\n''')
    f.write(f'''{z[0]-args['--extent']:.4f} {z[1]+args['--extent']:.4f} {args['--grid']}\n''')
    f.write('gaussian\n')

def end_dplot_block(f):
    '''
    This function completes the dplot block
    '''
    f.write('end\n')
    f.write('task dplot\n')


# Import various functions and libraries
from docopt import docopt
from sys import exit
from os.path import isfile, splitext
import glob
import os


try:
    # docopt parses the command line via the doc string above
    arguments = docopt(__doc__, version='dplot.py version 0.0.1')
    
    # Input Check 1: Can not use -b/--beta or -a/--alpha-beta with -c/--civecs
    #   No reason to move on if this is incorrect
    if arguments['--civecs'] and (arguments['--beta'] or arguments['--alpha-beta']):
        raise Exception('Input Error: -b/--beta and -a/--alpha-beta options cannot be used with -c/--civecs option')

    # Input Check 2: does '--input' file exists, if not continue to propmt user until they enter a file that exists
    while True:
        if not isfile(arguments['--input']) or splitext(arguments['--input'])[-1] != '.nw':
            arguments['--input'] = input(("'{0}' does not exist or does not have the expected file extension!\n" + 
                "Please enter an appropriate input file to continue, or try '-h/--help' option:\n").format(arguments['--input']))
        else:
            break

    # Input Check 3: does '--movecs' file exists, if not continue to propmt user until they enter a file that exists
    while True:
        if not isfile(arguments['--movecs']) or splitext(arguments['--movecs'])[-1] != '.movecs':
            arguments['--movecs'] = input(("'{0}' does not exist or does not have the expected file extension!\n"
                + "Please enter an appropriate movecs file to continue, or try '-h/--help' option:\n").format(arguments['--movecs']))
        else:
            break

    # Input Check 4: Conditional, if user wants civecs analysis
    #   does '--civecs' file exist, if not continue to prompt user until they enter a file that exists
    if arguments['--civecs']:
        while True:
            if not isfile(arguments['--civecs']) or splitext(arguments['--civecs'])[-1] not in ['.civecs_singlet', '.civecs_triplet']:
                arguments['--civecs'] = input(("'{0}' does not exist or does not have the expected file extension!\n"
                    + "Please enter an appropriate civecs file to continue, or try '-h/--help' option:\n").format(arguments['--civecs']))
            else:
                break

    # Input Check 5: Set default grid value if necessary
    if not arguments['--grid']:
        arguments['--grid'] = '50'
    
    # Input Check 6: Set default extent value if necessary, also convert to float
    #  if you cannot we need to exit
    try:
        if arguments['--extent']:
            arguments['--extent'] = float(arguments['--extent'])
        else:
            arguments['--extent'] = 2.0
    except ValueError:
        raise Exception("Extent Error: The '-e/--extent' option accepts a float value only!") 

    # Input Check 7: Is density switch set, if yes is it a valid string?
    if arguments['--density'] and arguments['--density'] not in ['total', 'alpha', 'beta', 'spin']:
        raise Exception('Density Error: {} is not a valid option, try -h/--help'.format(arguments['--density']))
    
    # Input Check 8: Does output file exist?
    if not arguments['--output'] :
        out_files= [out for out in glob.glob(f"{os.getcwd()}/*.out") if 'dplot.out' not in out]
        if len(out_files)>1:
            print("Please specify which output will be used:")
            for out in out_files:
                print(out.split('/')[-1], end="  ")
                print()
            SystemExit
        elif len(out_files)==1:
            arguments['--output']=out_files[0]  # if ONLY 1 output is found and not dplot.out   
        elif len(out_files)==0:
            arguments['--output']="no"   # This is set to "none" because there's no output
    elif arguments['--output'].lower()=="no":  # This "none" comes from user
        print("Output will not be used to define limitXYZ")
    else:
        if not isfile(arguments['--output']):
            print(f"{arguments['--output']} does not exist")
            SystemExit

    
    # Input file exists, let's read it
    with open(arguments['--input'], 'r') as f:
        lines = f.readlines()

    # We are now in a position to parse the input file:
    #   The only information we need is the geometry to calculate the output cube size
    #   We will use a boolean 'read' to indicate when we should add coordinates
    #   x, y, and z will contain the geometric coordinates of our system
    read = False
    x, y, z = [], [], []
    noautosym = False
    nocenter = False
    noprint = False
    for i in range(0, len(lines)):
        if 'geometry' in lines[i].lower():  # .lower() here to normalize the case sensitive. Users may use GEOMETRY rather than geometry. Both are accepted by NWChem
            read = True
            if 'noautosym' in lines[i].lower():
                noautosym = True 
            if 'nocenter' in lines[i].lower():
                nocenter = True
            if 'noprint' in lines[i].lower():
                noprint= True
        elif 'end' in lines[i].lower():
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
    if noprint==False:  # NWChem will print geometry after transformation
        if arguments['--output'].lower()=="no":  # CASE 1: User does not want to use output or output is not found  
            if (nocenter and noautosym):
                x = [min(x),max(x)]
                y = [min(y),max(y)]
                z = [min(z),max(z)]
            else:
                print('''WARNING: LimitXYZ might be not properly set because NWChem will rotate and/or translate your structure.
-----------
Input does not contain "nocenter" and "noautosym" for GEOMETRY block. NWChem will try to rotate and/or translate your structure. No output file was found at current dir.''')
                r_x = max(x) - min(x)
                r_y = max(y) - min(y)
                r_z = max(z) - min(z)
                x = [-r_x/2.0, r_x/2.0]
                y = [-r_y/2.0, r_y/2.0]
                z = [-r_z/2.0, r_z/2.0]
        else: # CASE 2: Output is available to use
            xmin,xmax,ymin,ymax,zmin,zmax = get_limit_xyz_from_output(arguments['--output'])
            x = [xmin,xmax]
            y = [ymin,ymax]
            z = [zmin,zmax]
    else:  # CASE 3: Output might be found, but no geometry "noprint" --> dont try to parse output
        if (nocenter and noautosym):
            x = [min(x),max(x)]
            y = [min(y),max(y)]
            z = [min(z),max(z)]
        else:
            print('''WARNING: LimitXYZ might be not properly set because NWChem will rotate and/or translate your structure.
-----------
Input does not contain nocenter and noautosym for GEOMETRY block. NWChem will try to rotate and/or translate your structure. No output file was found at current dir.''')
            r_x = max(x) - min(x)
            r_y = max(y) - min(y)
            r_z = max(z) - min(z)
            x = [-r_x/2.0, r_x/2.0]
            y = [-r_y/2.0, r_y/2.0]
            z = [-r_z/2.0, r_z/2.0]
    
    # We are now in a position to write the 'dplot.nw' file
    with open('dplot.nw', 'w') as f:
        # first we add copy the '--input' file to dplot.nw but comment any task directives
        for i in lines:
            if 'task' in i.lower():
                f.write('#' + i)
            else:
                f.write(i)
        
        # now we can add the dplot blocks!
        #   --> if '--density' is set, we will only process one block
        #   --> need some logic here for the '--alpha-beta' and '--beta' options
        base = splitext(arguments['--input'])[0]
        if arguments['--density']:
            f.write('\n')
            begin_dplot_block(f, arguments, x, y, z)
            # I hate using the full spindens as an argument, therefore I deal
            #   with the spin case separately (mainly the output format looks like
            #   base-spindens-dens.cube i.e. dumb)
            if arguments['--density'] == 'spin':
                f.write('spin spindens\n')
            else:    
                f.write('spin {}\n'.format(arguments['--density']))
            f.write('output {}-{}-dens.cube\n'.format(base, arguments['--density']))
            end_dplot_block(f)
        else:
            mos = split_mo_list(arguments['--list'])
            if arguments['--alpha-beta']:
                for spin in ['alpha', 'beta']:
                    for i in mos:
                        num = str(i).zfill(5)
                        f.write('\n')
                        begin_dplot_block(f, arguments, x, y, z)
                        f.write('spin {}\n'.format(spin))
                        f.write('orbitals view;1;{}\n'.format(i))
                        f.write('output {}-{}-{}.cube\n'.format(base, spin, num))
                        end_dplot_block(f)
            elif arguments['--beta']:
                spin = 'beta'
                for i in mos:
                    num = str(i).zfill(5)
                    f.write('\n')
                    begin_dplot_block(f, arguments, x, y, z)
                    f.write('spin {}\n'.format(spin))
                    f.write('orbitals view;1;{}\n'.format(i))
                    f.write('output {}-{}.cube\n'.format(base, num))
                    end_dplot_block(f)
            elif arguments['--civecs']:
                for i in mos:
                    num = str(i).zfill(5)
                    f.write('\n')
                    begin_dplot_block(f, arguments, x, y, z)
                    f.write('root {}\n'.format(i))
                    f.write('output {}-root-{}.cube\n'.format(base, num))
                    f.write('civecs {}\n'.format(arguments['--civecs']))
                    end_dplot_block(f)
            else:
                spin = 'alpha'
                for i in mos:
                    num = str(i).zfill(5)
                    f.write('\n')
                    begin_dplot_block(f, arguments, x, y, z)
                    f.write('spin {}\n'.format(spin))
                    f.write('orbitals view;1;{}\n'.format(i))
                    f.write('output {}-{}.cube\n'.format(base, num))
                    end_dplot_block(f)

# Some common exceptions
except KeyboardInterrupt:
    exit('Interrupt Detected! exiting...')

except SystemExit:
    print('==> Input Error: Printing usage, or see documentation! <==')
    print(__doc__)

except Exception as e:
    print(e)
