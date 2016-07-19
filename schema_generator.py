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
parser.add_argument('-f', '--file_loc', help='Datafile Location(s)', nargs='+')
parser.add_argument('-t', '--table_name', help='Table Location(s)', nargs='+')
args = parser.parse_args()


datafiles = args.file_loc
tables = args.table_name


def get_types(datafile):
    with open(datafile, "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # The names of the columns should be contained in the first row of
        # the data file
        header_row = next(reader)
        # Since the order of the columns matters, we'll use an OrderedDict
        # to store the schema
        schema = coll.OrderedDict()
        # To begin, we'll set the type for all columns to integer and then
        # work through the data to correct that assumption where it's
        # incorrect
        for c in header_row:
            schema[c] = "INTEGER"

        # We'll sample 100 random rows in the first 10,000 rows to check
        # whether the columns really are ints
        sample_rows = random.sample(range(100), 10)

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
                        if not val.is_integer():
                            schema[header_row[c]] = "FLOAT"
                    # If the casting fails, it's because there's a non-digit
                    # in the value and so we should designate that column as
                    # a string
                    except ValueError:
                        schema[header_row[c]] = "STRING"
                    # If we succeed at casting the value, then we check whether
                    # it's an int. If not, we change the type to float in the
                    # schema. If it is an integer, we leave the type as int
                    # in the schema.
    return schema


def write_table_schemas(ps, output, df, dfs):
    # Once we've parsed the schema, we print it to the output file in the
    # format required by BigQuery
    output.write("For table {}:\n".format(tables[dfs.index(df)]))
    output.write(", ".join([":".join([k, v]) for k, v in ps.items()]) + "\n")


def produce_subselect(mfl, schema, tbl_name):
    field_list = []
    # When working with multiple files, we have field lists that need merging
    # We'll create a subselect for each table that was passed in.
    for field in mfl:
        # If the field from the master field list is in the table, we just
        # select it
        if field in set(schema):
            field_list.append(field)
        # If the field from the master field list is not in the table, we
        # pad that column with a NULL so that each subselect has the same
        # width
        else:
            field_list.append("NULL AS {} ".format(field))
    subselect = "(SELECT " + ", ".join([field for field in field_list])
    subselect += ", " + "'" + tbl_name + "'" + " as src_table"
    subselect += " FROM " + tbl_name + ")"

    return subselect


def main():
    # Make sure there are the same number of files and table names
    if not len(args.file_loc) == len(args.table_name):
        print "Mismatch between number of files and table names provided"
        exit()

    output_file = open("schema_output.txt", "w")
    schemas, master_field_list, subselect_list = [], [], []

    for df in datafiles:
        parsed_schema = get_types(df)
        schemas.append(parsed_schema)
        for field in parsed_schema:
            if field not in set(master_field_list):
                master_field_list.append(field)
        write_table_schemas(parsed_schema, output_file, df, datafiles)

    if len(tables) > 1:
        for schema in schemas:
            ss = produce_subselect(master_field_list, schema,
                                   tables[schemas.index(schema)])

            subselect_list.append(ss)
        output_file.write("\nFor creating final unioned table:\n")
        output_file.write("SELECT * FROM " + ", \n".join([subsel
                                                         for subsel in
                                                         subselect_list]))
    output_file.close()


main()
