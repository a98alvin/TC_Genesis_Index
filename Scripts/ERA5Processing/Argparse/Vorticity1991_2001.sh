#!/bin/bash -l
#PBS -N Vort_1991-2001
#PBS -A UMCP0022
#PBS -l walltime=12:00:00
#PBS -l select=1:ncpus=36:mem=45GB
#PBS -q regular
#PBS -o /glade/work/acheung/outfile
#PBS -e /glade/work/acheung/errfile

module load conda/latest; conda activate squalls
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1991 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1992 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1993 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1994 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1995 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1996 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1997 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1998 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1999 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 2000 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 2001 &
wait
