#!/usr/bin/python

import argparse
import collections as coll
import csv
from itertools import islice
import random


# Parse the arguments passed in at the command line

parser = argparse.ArgumentParser(description='This script samples a '
                                 'datafile downloaded from DataFerret to '
                                 'determine column types and then prints a '
                                 'schema appropriate for defining a table '
                                 'in BigQuery')
parser.add_argument('-f', '--file', help='Codebook Location', required=True)
args = parser.parse_args()

# Since the order of the columns matters, we'll use an OrderedDict to store
# the schema

census_datafile = args.file
schema = coll.OrderedDict()


def get_types(datafile):
    with open(datafile, "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # The names of the columns should be contained in the first row of
        # the data file
        header_row = next(reader)

        # To begin, we'll set the type for all columns to integer and then
        # work through the data to correct that assumption where it's
        # incorrect
        for c in header_row:
            schema[c] = "INTEGER"

        # We'll sample 100 random rows in the first 10,000 rows to check
        # whether the columns really are ints
        sample_rows = random.sample(range(100), 100)

        for r in sample_rows:
            # Skip forward in the file r rows
            sample_row = next(islice(reader, r, r+1))
            # Check each column in the row
            for c in range(len(header_row)):
                # If the column is already a string in our schema, no need
                # to check it (since that is the least restrictive type)
                if not schema[header_row[c]] == "STRING":
                    # We'll try to cast the value to a Python float
                    try:
                        val = float(sample_row[c])
                    # If the casting fails, it's because there's a non-digit
                    # in the value and so we should designate that column as
                    # a string
                    except ValueError:
                        schema[header_row[c]] = "STRING"
                    # If we succeed at casting the value, then we check whether
                    # it's an int. If not, we change the type to float in the
                    # schema. If it is an integer, we leave the type as int
                    # in the schema.
                    if not val.is_integer():
                        schema[header_row[c]] = "FLOAT"
    return schema


def main():
    parsed_schema = get_types(census_datafile)
    # Once we've parsed the schema, we print it to stdout in the format
    # required by BigQuery
    print ", ".join([":".join([k, v]) for k, v in parsed_schema.items()])

main()
