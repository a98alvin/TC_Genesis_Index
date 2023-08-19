import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True, help="year of choice")
args_dict = parser.parse_args()
year_to_run = args_dict.year
print(year_to_run)
print(type(year_to_run))