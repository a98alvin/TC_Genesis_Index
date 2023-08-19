#!/bin/bash -l
#PBS -N test
#PBS -A UMCP0022
#PBS -l walltime=00:10:00
#PBS -l select=1:ncpus=1:mem=5GB
#PBS -q regular
#PBS -o /glade/work/acheung/outfile
#PBS -e /glade/work/acheung/errfile

module load conda/latest; conda activate squalls

python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/testargparse.py --year 1951
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/testargparse.py --year 1952
