#!/usr/bin/python

import argparse
import collections as coll
import math
import re


# Parse the arguments passed in at the command line

parser = argparse.ArgumentParser(description='This script parses codebooks '
                                 'downloaded from DataFerret into LookML')
parser.add_argument('-f', '--file_loc', help='Codebook Location(s)', nargs='+')
parser.add_argument('-t', '--table', help='Table Name(s)', nargs='+')
parser.add_argument('-o', '--output', help='Flag to merge output to one file')
parser.add_argument('-m', '--measure', help='The name of the weighted measure',
                    nargs='*')
args = parser.parse_args()

# The codebook is composed of definitions for all downloaded variables.
# Each line can be parsed independently to figure out what part of a definition
# it makes up.

codebooks = args.file_loc
tables = args.table
measures = args.measure
parsed_cbs = []


# Below, we define the regular expressions needed to identify the different
# definition parts.

# The dataset name is prefaced by Dataset:
dataset_re = re.compile(r'^Dataset: .*')
# The topic name is prefaced by Topic:
topic_cap_re = re.compile(r'^Topic: ([A-z ]*)')
# Question names are composed of up to 8 capital letters and/or digits
q_name_cap_re = re.compile(r'(^[A-Z\d]{1,8})$')
# Question descriptions have the topic name, then a dash, and the q description
q_description_cap_re = re.compile(
    r'-(?!\s)([\w\d\W\s]*$)')
# Newer questions don't necessarily have this format
new_q_description_cap_re = re.compile(
    r'(?:\s-\s)?([\w\d\W\s]*$)')

# Some questions' valid values are defined as a set of key/value pairs while
# others are composed of ranges of valid values

# For key/value pairs, format is a number, then two spaces and then the name
key_val_re = re.compile(r'^-?[0-9]* {2}[A-z 0-9\W]*$')
# For value ranges, the range is shown as min:max, then the name of the range
val_range_cap_re = re.compile(r'(^-?[0-9.]+:-?[0-9.]+)  '
                              '(?:Hours|Range|Year|# of own children under 18'
                              ' years of age|Specific City Code|Line number|'
                              'persons)$')

# We also need to be able to pass whitespace and known section titles
whitespace_re = re.compile(r'^\s*$')

# We also have capturing regex to split the keys from their values
key_cap_re = re.compile(r'(^-?[0-9]*)')
value_cap_re = re.compile(r'^-?[0-9]* {2}([A-z 0-9\W]*$)')

weird_lines = ("""Demographics - age topcoded at 85, 90 or 80
                (see full description)""",
               "Educational Attainment (recode - 4 categories)",
               "Educational Attainment (recode - 5 categories)")

ignorable = ("DataFerrett Codebook - Created", "With the following Ranges:",
             "Is a recode of the variable(s) PEMLR",
             "Is a recode of the variable(s) PEEDUCA")


def parseCodebook(cb, tb):
    lines = cb.readlines()
    print "Parsing " + tb

    # The order of the questions in the codebook isn't strictly necessary, but
    # preserving the order lets value sorting work and makes it easier to
    # compare input to output, so we'll use OrderedDict to preserve order

    i = 0
    parsed_cb = coll.OrderedDict()

    # For each line, we'll work our way down the hierarchy (dataset -> topic ->
    # question -> values) looking for regex matches and filling out the nested
    # dictionary as we go
    q_id_line = 0
    for line in lines:
        i += 1
        if re.match(dataset_re, line):
            parsed_cb[tb] = coll.OrderedDict()
            q_id_line = 0
        elif re.match(topic_cap_re, line):
            topic = re.findall(topic_cap_re, line)[0]
            q_id_line = 0
        elif re.match(q_name_cap_re, line):
            q_name = re.findall(q_name_cap_re, line)[0]
            if q_name not in parsed_cb[tb]:
                parsed_cb[tb][q_name] = coll.OrderedDict()
                parsed_cb[tb][q_name]["Topic"] = topic
                parsed_cb[tb][q_name]["Source"] = [tb]
                q_id_line = 1
        elif re.match(key_val_re, line):
            if "Keys" not in parsed_cb[tb][q_name]:
                parsed_cb[tb][q_name]["Keys"] = coll.OrderedDict()
            key = re.findall(key_cap_re, line)[0]
            value = re.findall(value_cap_re, line)[0]
            parsed_cb[tb][q_name]["Keys"][key] = value
            q_id_line = 0
        elif re.match(val_range_cap_re, line):
            value_range = re.findall(val_range_cap_re, line)[0]
            parsed_cb[tb][q_name]["Range"] = value_range
            q_id_line = 0
        # Since Q description requires relatively permissive regex, its elif
        # is after the more restrictive fields
        elif re.match(q_description_cap_re, line):
            q_description = re.findall(q_description_cap_re, line)[0]
            parsed_cb[tb][q_name]["Description"] = q_description
            q_id_line = 0
        # Since Q description formatting has become more unpredictable lately
        # we also track whether the previous line was a Q name and use that
        # as a backup identifier of a Q description
        elif q_id_line:
            q_description = re.findall(new_q_description_cap_re, line)[0]
            parsed_cb[tb][q_name]["Description"] = q_description
            q_id_line = 0
        # If a line is empty or has a section title, we ignore it.
        elif re.match(whitespace_re, line) or line.rstrip() in set(ignorable):
            q_id_line = 0
        # Finally, check the line against our list of non-conforming lines
        elif line.rstrip() in set(weird_lines):
            q_description = line
            parsed_cb[tb][q_name]["Description"] = q_description
            q_id_line = 0
        # If we don't recognize a line, we print it for examination
        else:
            print "Unable to parse line " + str(i) + " - " + line
            q_id_line = 0
    return parsed_cb


def remove_source(dictionary):
    sourceless_dict = coll.OrderedDict()
    for a in dictionary:
        sourceless_dict[a] = coll.OrderedDict()
        for b in dictionary[a]:
            if b != 'Source':
                sourceless_dict[a][b] = dictionary[a][b]
    return sourceless_dict


def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    d1_only_keys = d1_keys - d2_keys
    d2_only_keys = d2_keys - d1_keys
    same = set(o for o in intersect_keys if d1[o] == d2[o] and o)
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    return d1_only_keys, d2_only_keys, same, modified


def dict_merge(to_merge, table_to_merge, final_dict):
    tm_sourceless = remove_source(to_merge)
    fd_sourceless = remove_source(final_dict)
    for k, v in tm_sourceless.iteritems():
        if k in fd_sourceless:
            if v == fd_sourceless[k]:
                final_dict[k]["Source"].append(table_to_merge)
            else:
                choice = key_chooser([tm_sourceless[k], fd_sourceless[k]])
                if choice == 0:
                    final_dict[k]["Source"].append(table_to_merge)
                elif choice == 1:
                    to_merge[k]["Source"] += final_dict[k]["Source"]
                    final_dict[k] = to_merge[k]
                elif choice == 'split':
                    final_dict[k + "\u0007" + table_to_merge] = to_merge[k]
        else:
            final_dict[k] = to_merge[k]
    return final_dict


def key_chooser(choices):
    print "\n Questions differ. Choose the version to keep,",
    print 'or split them into separate questions:'
    for k in choices[0]:
        if isinstance(choices[0][k], coll.OrderedDict):
            mismatches = dict_compare(choices[0][k], choices[1][k])
            for key, value in mismatches[3].iteritems():
                print key + ": [1] " + value[0].rstrip(),
                print "vs. [2] " + value[1].rstrip()
        elif isinstance(choices[0][k], str) and choices[0][k] != choices[1][k]:
            print "[1] " + choices[0][k].rstrip() + ' vs.',
            print "[2] " + choices[1][k].rstrip()
    print "Version [1], Version [2], Or Type [3] to Split: \n>>"
    # Prompt for input and validate the input
    while True:
        action = raw_input()
        if action in ('1', '2'):
            return int(action) - 1
        elif action == '3':
            return "split"
        print "Invalid Input"


def writebaseLookMLview(nested_cb):

    for dat, ques in nested_cb.iteritems():
        # We name the output file after the dataset
        file_name = re.sub(r'[/\s\-]', '_', dat)
        lookml = open("{}.view.lookml".format(file_name), "w")

        # First we write the view definitions
        lookml.write("- view: {}\n".format(file_name))
        lookml.write("  sql_table_name: [ENTER DATA FILE NAME HERE]\n\n\n")

        lookml.write("  fields:\n")

        for que, k in ques.iteritems():
                # We write definitions for fields differently depending
                # on whether it has key/value pairs or a value range
                if ('Keys' in k and 'Range' not in k):
                    # Key/value pairs get written as string dimensions
                    # We preserve the shortname of the question as the
                    # dimension name for easy searchability
                    lookml.write("  - dimension: {}\n".format(
                        que.lower().replace('\u0007', '_')))
                    # We use the question name as the label
                    lookml.write("    label: \"{}\"\n".format(
                        k["Description"].capitalize().rstrip()))
                    # We use the topic as view_label for easy categorization
                    lookml.write("    view_label: Cohort {}\n".format(
                        k["Topic"]))
                    lookml.write("    type: string\n")
                    lookml.write("    sql_case:\n")

                    for key, value in k["Keys"].iteritems():
                        lookml.write("      {}: |\n".format(
                            value.rstrip().replace(
                                '#', '\\#').replace(':', '":"')))
                        lookml.write("        ${{TABLE}}.{0} = "
                                     "{1}\n".format(
                                      que.lower().rstrip().split('\u0007')[0],
                                      key))
                        if len(tables) > len(k["Source"]):
                            lookml.write("        AND ${TABLE}.src_table in ")
                            lookml.write("({})\n".format(', '.join(
                                "'" + item + "'" for item in k["Source"])))
                    lookml.write("\n\n")

                # For value ranges, we split the range into 5 tiers
                # evenly spaced between the min and max
                elif ('Range' in k):
                    ends = k["Range"].split(':')
                    tiers = []
                    for x in range(0, 5):
                        tiers.append(math.ceil((float(ends[0]) +
                                                x * float(ends[1]) / 4)))
                    lookml.write("  - dimension: {}\n".format(
                        que.lower().replace('\u0007', '_')))
                    if ("Description" in k):
                        lookml.write("    label: \"{}\"\n".format(
                                k["Description"].capitalize().rstrip()))
                    lookml.write("    view_label: Cohort {}\n".format(
                        k["Topic"]))
                    lookml.write("    type: tier\n")
                    lookml.write("    tiers: [{},{},{},{},{}]\n".format(
                                    int(tiers[0]),
                                    int(tiers[1]),
                                    int(tiers[2]),
                                    int(tiers[3]),
                                    int(tiers[4])))
                    lookml.write("    style: classic\n")
                    lookml.write("    sql: ${{TABLE}}.{}\n".format(que))
                    lookml.write("    sql: CASE WHEN "
                                 "${{TABLE}}.{} between {} AND {} "
                                 "THEN ${{TABLE}}.{} END".
                                 format(que.lower(), ends[0],
                                        ends[1], que.lower()))
                    lookml.write("\n\n")
        lookml.close()
        return "{}.view.lookml".format(file_name)


def writefilteredview(nested_cb):
    for dat, top in nested_cb.iteritems():
        # We name the output file after the dataset
        file_name = re.sub(r'[/\s\-]', '_', dat)
        lookml = open("{}_filters.view.lookml".format(file_name), "w")

        # First we write the view definitions
        lookml.write("- view: {}_filters\n".format(file_name))
        lookml.write("  extends: {}\n".format(file_name))

        lookml.write("  fields:\n")

        for ques, des in top.iteritems():
            # We write definitions for fields differently depending
            # on whether it has key/value pairs or a value range
            lookml.write("  - filter: select_{}\n".format(
                ques.lower().replace('\u0007', '_')))
            # We use the question name as the label
            lookml.write("    label: \"{}\"\n".format(
                des["Description"].capitalize().rstrip()))
            # We use the topic as view_label for easy categorization
            lookml.write("    view_label: Group {}\n".format(des["Topic"]))
            lookml.write("    suggest_dimension: {}\n".format(
                ques.lower().replace('\u0007', '_')))
            lookml.write("\n\n")
            # For value ranges, we split the range into 5 tiers
            # evenly spaced between the min and max
        lookml.close()
        return "{}.view.lookml".format(file_name)


def writemeasures(nested_cb, weighted_measures):
    for dat, top in nested_cb.iteritems():
        # We name the output file after the dataset
        file_name = re.sub(r'[/\s\-]', '_', dat)
        lookml = open("{}_measures.view.lookml".format(file_name), "w")

        # First we write the view definitions
        lookml.write("- view: {}_measures\n".format(file_name))
        lookml.write("  extends: {}_filters\n".format(file_name))

        lookml.write("  fields:\n")

        for weighted_measure in weighted_measures:
            lookml.write("  - measure: cohort_population{}\n".format(
                "_" + weighted_measure if len(weighted_measures) > 1 else ""))
            # We use the topic as view_label for easy categorization
            lookml.write("    type: sum\n")
            lookml.write("    view_label: Populations\n")
            lookml.write("    value_format_name: decimal_0\n")
            lookml.write("    sql: ${{TABLE}}.{}".format(weighted_measure))
            lookml.write("\n\n")

            # We write definitions for fields differently depending
            # on whether it has key/value pairs or a value range
            lookml.write("  - measure: group_population{}\n".format("_" +
                         weighted_measure if len(weighted_measures) > 1
                         else ""))
            # We use the topic as view_label for easy categorization
            lookml.write("    type: sum\n")
            lookml.write("    view_label: Populations\n")
            lookml.write("    value_format_name: decimal_0\n")
            lookml.write("    sql: |\n")
            lookml.write("      CASE WHEN\n")
            i = 0
            for ques, des in top.iteritems():
                if ('Keys' in des or 'Range' in des):
                    lookml.write(
                        """      {} {{% condition select_{} %}}
                        ${{{}}} {{%endcondition%}} \n""".format(
                            "AND" if i > 0 else "", ques.lower().replace(
                                '\u0007', '_'), ques.lower().replace(
                                '\u0007', '_')))
                    i += 1
            lookml.write("      THEN {}\n".format(weighted_measure))
            lookml.write("      ELSE 0\n")
            lookml.write("      END\n")
            lookml.write("\n\n")
            # For value ranges, we split the range into 5 tiers
            # evenly spaced between the min and max
        lookml.close()
        return "{}.view.lookml".format(file_name)


def main():
    if len(tables) != len(codebooks):
        print "You must specify the same number of table names as codebooks"
        quit
    # We can handle multiple codebooks by merging all their questions into
    # one output file or by producing multiple LookML output files. This
    # looks for the flag to determine which mode we'll operate in.

    for cb, tb in zip(codebooks, tables):
        cb_open = open(cb)
        parsed_cbs.append(parseCodebook(cb_open, tb))

    final_dictionary = coll.OrderedDict()
    if args.output == "merge":
        for cb, tb in zip(parsed_cbs, tables):
            final_dictionary = dict_merge(cb[tb], tb, final_dictionary)

    print "Done parsing codebooks"

    to_print = coll.OrderedDict()
    to_print["census"] = coll.OrderedDict()
    to_print["census"] = final_dictionary
    lookml_name = writebaseLookMLview(to_print)
    print "LookML Codebook written as {}".format(lookml_name)

    lookml_name = writefilteredview(to_print)
    print "Filtered Dimensions written as {}".format(lookml_name)

    if len(measures) > 0:
        lookml_name = writemeasures(to_print, measures)
    print "Measures written as {}".format(lookml_name)


main()
