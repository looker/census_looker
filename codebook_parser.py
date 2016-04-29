#!/usr/bin/python

import argparse
import collections as coll
import math
import re


# Parse the arguments passed in at the command line

parser = argparse.ArgumentParser(description='This script parses codebooks '
                                 'downloaded from DataFerret into LookML')
parser.add_argument('-f', '--file', help='Codebook Location', required=True)
args = parser.parse_args()

# The codebook is composed of definitions for all downloaded variables.
# Each line can be parsed independently to figure out what part of a definition
# it makes up.

codebook = open(args.file)

# These define the regular expressions needed to identify the different
# definition parts.

# The dataset name is prefaced by Dataset:
dataset_re = re.compile(r'^Dataset: .*')
# The topic name is prefaced by Topic:
topic_re = re.compile(r'^Topic: [A-z ]*')
# Question names are composed of up to 8 capital letters and/or digits
q_name_re = re.compile(r'^[A-Z\d]{1,8}$')
# Question descriptions have the topic name, then a dash, and the q description
q_description_re = re.compile(
    r'[\w\s\W]*-(?!\s)[\w\d\W\s]*$')

# Some questions' valid values are defined as a set of key/value pairs while
# others are composed of ranges of valid values

# For key/value pairs, format is a number, then two spaces and then the name
key_val_re = re.compile(r'^-?[0-9]* {2}[A-z 0-9\W]*$')
# For value ranges, the range is shown as min:max, then the name of the range
val_range_re = re.compile(r'^-?[0-9.]+:-?[0-9.]+  (?:Hours|Range)$')
# We also need to be able to pass whitespace and known section titles
whitespace_re = re.compile(r'^\s*$')

# These regular expressions are the same as above, but with a capturing
# group
dataset_cap_re = re.compile(r'^Dataset: (.*)')
topic_cap_re = re.compile(r'^Topic: ([A-z ]*)')
q_name_cap_re = re.compile(r'(^[A-Z\d]{1,8})$')
q_description_cap_re = re.compile(
    r'-(?!\s)([\w\d\W\s]*$)')
key_cap_re = re.compile(r'(^-?[0-9]*)')
value_cap_re = re.compile(r'^-?[0-9]* {2}([A-z 0-9\W]*$)')
val_range_cap_re = re.compile(
    r'(^-?[0-9.]+:-?[0-9.]+)  (?:Hours|Range)$')

weird_lines = ("Demographics - age topcoded at 85, 90 or 80 (see full description)",
               "Educational Attainment (recode - 4 categories)",
               "Educational Attainment (recode - 5 categories)")

ignorable = ("DataFerrett Codebook - Created", "With the following Ranges:",
             "Is a recode of the variable(s) PEMLR",
             "Is a recode of the variable(s) PEEDUCA")


def parseCodebook(cb):
    lines = cb.readlines()

    # The order of the questions in the codebook isn't strictly necessary, but
    # preserving the order lets value sorting work and makes it easier to
    # compare input to output, so we'll use OrderedDict to preserve order

    parsed_cb = coll.OrderedDict()
    i = 0

    # For each line, we'll work our way down the hierarchy (dataset -> topic ->
    # question -> values) looking for regex matches and filling out the nested
    # dictionary as we go
    for line in lines:
        i += 1
        if re.match(dataset_re, line):
            dataset = re.findall(dataset_cap_re, line)[0]
            if dataset not in parsed_cb:
                parsed_cb[dataset] = coll.OrderedDict()
        elif re.match(topic_re, line):
            topic = re.findall(topic_cap_re, line)[0]
            if topic not in parsed_cb[dataset]:
                parsed_cb[dataset][topic] = coll.OrderedDict()
        elif re.match(q_name_re, line):
            q_name = re.findall(q_name_cap_re, line)[0]
            if q_name not in parsed_cb[dataset][topic]:
                parsed_cb[dataset][topic][q_name] = coll.OrderedDict()
        elif re.match(key_val_re, line):
            if "Keys" not in parsed_cb[dataset][topic][q_name]:
                parsed_cb[dataset][topic][q_name]["Keys"] = coll.OrderedDict()
            key = re.findall(key_cap_re, line)[0]
            value = re.findall(value_cap_re, line)[0]
            parsed_cb[dataset][topic][q_name]["Keys"][key] = value
        elif re.match(val_range_re, line):
            value_range = re.findall(val_range_cap_re, line)[0]
            parsed_cb[dataset][topic][q_name]["Range"] = value_range
        # Since Q description requires relatively permissive regex, its elif
        # is after the more restrictive fields
        elif re.match(q_description_re, line):
            q_description = re.findall(q_description_cap_re, line)[0]
            parsed_cb[dataset][topic][q_name]["Description"] = q_description
        # If a line is empty or has a section title, we ignore it.
        elif re.match(whitespace_re, line) or line.rstrip() in set(ignorable):
            pass
        # Finally, check the line against our list of non-conforming lines
        elif line.rstrip() in set(weird_lines):
            q_description = line
            parsed_cb[dataset][topic][q_name]["Description"] = q_description
        # If we don't recognize a line, we print it for examination
        else:
            print "Unable to parse line " + str(i) + " - " + line
    return parsed_cb


def writebaseLookMLview(nested_cb):

    for dat, top in nested_cb.iteritems():
        # We name the output file after the dataset
        file_name = re.sub(r'[/\s\-]', '_', dat)
        lookml = open("{}.view.lookml".format(file_name), "w")

        # First we write the view definitions
        lookml.write("- view: {}\n".format(file_name))
        lookml.write("  sql_table_name: [ENTER DATA FILE NAME HERE]\n\n\n")

        lookml.write("  fields:\n")

        for tops, que in top.iteritems():
            for ques, des in que.iteritems():
                # We write definitions for fields differently depending
                # on whether it has key/value pairs or a value range
                if ('Keys' in des and 'Range' not in des):
                    # Key/value pairs get written as string dimensions
                    # We preserve the shortname of the question as the
                    # dimension name for easy searchability
                    lookml.write("  - dimension: {}\n".format(ques.lower()))
                    lookml.write("    sql: ${{TABLE}}.{}\n".format(ques))
                    # We use the question name as the label
                    lookml.write("    label: \"{}\"\n".format(
                        des["Description"].capitalize().rstrip()))
                    # We use the topic as view_label for easy categorization
                    lookml.write("    view_label: '{}'\n".format(tops))
                    lookml.write("    type: string\n")
                    lookml.write("    sql_case:\n")
                    for key, value in des["Keys"].iteritems():
                        lookml.write("      {}: |\n".format(
                            value.rstrip().replace(
                                '#', '\\#').replace(':', '":"')))
                        lookml.write("        ${{TABLE}}.{0} = {1}\n".format(
                            ques.lower().rstrip(), key))
                    lookml.write("\n\n")
                # For value ranges, we split the range into 5 tiers
                # evenly spaced between the min and max
                elif ('Range' in des):
                    ends = des["Range"].split(':')
                    tiers = []
                    for x in range(0, 5):
                        tiers.append(math.ceil((float(ends[0]) +
                                                x * float(ends[1]) / 4)))

                    lookml.write("  - dimension: {}\n".format(ques.lower()))
                    if ("Description" in des):
                        lookml.write("    label: \"{}\"\n".format(
                                des["Description"].capitalize().rstrip()))
                    lookml.write("    view_label: '{}'\n".format(tops))
                    lookml.write("    type: tier\n")
                    lookml.write("    tiers: [{},{},{},{},{}]\n".format(
                                    int(tiers[0]),
                                    int(tiers[1]),
                                    int(tiers[2]),
                                    int(tiers[3]),
                                    int(tiers[4])))
                    lookml.write("    style: classic\n")
                    lookml.write("    sql: ${{TABLE}}.{}\n".format(ques))
                    lookml.write("    sql: CASE WHEN "
                                 "${{TABLE}}.{} between {} AND {} "
                                 "THEN ${{TABLE}}.{} END".
                                 format(ques.lower(), ends[0],
                                        ends[1], ques.lower()))
                    lookml.write("\n\n")
        lookml.close()
        return "{}.view.lookml".format(file_name)


def main():
    print "Parsing codebook....."
    cb_dict = parseCodebook(codebook)
    print "Done parsing codebook"
    lookml_name = writebaseLookMLview(cb_dict)
    print "LookML Codebook written as {}".format(lookml_name)

main()
