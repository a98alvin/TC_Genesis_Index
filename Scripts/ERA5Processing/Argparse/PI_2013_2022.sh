#!/bin/bash -l
#PBS -N PI_2013-2022
#PBS -A UMCP0022
#PBS -l walltime=24:00:00
#PBS -l select=1:ncpus=36:mem=45GB
#PBS -q casper
#PBS -o /glade/work/acheung/outfile
#PBS -e /glade/work/acheung/errfile

module load conda/latest; conda activate picalc
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2013 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2014 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2015 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2016 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2017 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2018 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2019 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2020 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2021 &
python /glade/u/home/acheung/TCGenesisIndex/Scripts/ERA5Processing/Argparse/PI.py --year 2022 &
wait
