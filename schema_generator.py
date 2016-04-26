#!/usr/bin/python

import argparse
import collections as coll
import csv
from itertools import islice
import random

parser = argparse.ArgumentParser(description='This script samples a '
                                 'datafile downloaded from DataFerret to '
                                 'determine column types and then prints a '
                                 'schema appropriate for defining a table '
                                 'in BigQuery')
parser.add_argument('-f', '--file', help='Codebook Location', required=True)
args = parser.parse_args()

census_datafile = args.file
schema = coll.OrderedDict()


def get_types(datafile):
    with open(datafile, "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header_row = next(reader)

        for c in header_row:
            schema[c] = "INTEGER"

        sample_rows = random.sample(range(1000), 100)
        sample_rows = sorted(sample_rows, key=int)

        for r in sample_rows:
            print r
            sample_row = next(islice(reader, r, None))
            for c in range(len(header_row)):
                if not schema[header_row[c]] == "STRING":
                    try:
                        val = float(sample_row[c])
                    except ValueError:
                        schema[header_row[c]] = "STRING"
                    if not val.is_integer():
                        schema[header_row[c]] = "FLOAT"

    return schema


def main():
    parsed_schema = get_types(census_datafile)
    print ", ".join([":".join([k, v]) for k, v in parsed_schema.items()])

main()
