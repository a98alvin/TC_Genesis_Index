#!/bin/bash -l
#PBS -N PI_2002-2012
#PBS -A UMCP0022
#PBS -l walltime=24:00:00
#PBS -l select=1:ncpus=36:mem=45GB
#PBS -q casper
#PBS -o /glade/work/acheung/outfile
#PBS -e /glade/work/acheung/errfile

module load conda/latest; conda activate picalc
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2002 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2003 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2004 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2005 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2006 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2007 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2008 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2009 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2010 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2011 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2012 &
wait
