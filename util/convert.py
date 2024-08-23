"""Script to convert all YAML files to JSON and vice versa."""

# Note that this script does NOT automatically regenerate json files if the corresponding yaml files have changed (or vice versa).
# You have to delete the existing file, and then run this script

from wilson.wcxf.converters import yamljson
import glob
import os
import logging

logging.basicConfig(level=logging.DEBUG)

bases_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

bases_yml = glob.glob(bases_path + '/**/*.yml', recursive=True)
bases_json = glob.glob(bases_path + '/**/*.json', recursive=True)

logging.info("Found {} .yml and {} .json files"
             .format(len(bases_yml), len(bases_json)))

for b in bases_yml:
    b_json = b.replace('yml', 'json')
    if os.path.isfile(b_json):
        logging.info("File {} already has a JSON file".format(b))
    else:
        logging.info("File {}: converting to JSON".format(b))
        with open(b, 'r') as f_in:
            with open(b_json, 'w') as f_out:
                yamljson.convert_json(f_in, f_out)

for b in bases_json:
    b_yaml = b.replace('json', 'yml')
    if os.path.isfile(b_yaml):
        logging.info("File {} already has a YAML file".format(b))
    else:
        logging.info("File {}: converting to YAML".format(b))
        with open(b, 'r') as f_in:
            with open(b_yaml, 'w') as f_out:
                yamljson.convert_yaml(f_in, f_out)
