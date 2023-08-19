#!/bin/bash -l
#PBS -N Vort_1980-1990
#PBS -A UMCP0022
#PBS -l walltime=12:00:00
#PBS -l select=1:ncpus=36:mem=45GB
#PBS -q regular
#PBS -o /glade/work/acheung/outfile
#PBS -e /glade/work/acheung/errfile

module load conda/latest; conda activate squalls
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1980 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1981 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1982 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1983 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1984 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1985 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1986 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1987 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1988 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1989 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/Vorticity.py --year 1990 &
wait