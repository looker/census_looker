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

codebook = open(args.file)

dataset_re = re.compile(r'^Dataset: .*')
topic_re = re.compile(r'^Topic: [A-z ]*')
q_name_re = re.compile(r'^[A-Z\d]{1,8}$')
q_description_re = re.compile(
    r'^[A-Z]{1}[a-z]*?[\s\.]?&?[A-Z]?[a-z]*\.?-[\w\d\W]*$')
key_val_re = re.compile(r'^-?[0-9]* {2}[A-z 0-9\W]*$')
val_range_re = re.compile(r'^-?[0-9.]+:-?[0-9.]+  (?:Hours|Range)$')
whitespace_re = re.compile(r'^\s*$')
range_title_re = re.compile(
    r'With the following Ranges:|Is a recode of the variable')


dataset_cap_re = re.compile(r'^Dataset: (.*)')
topic_cap_re = re.compile(r'^Topic: ([A-z ]*)')
q_name_cap_re = re.compile(r'(^[A-Z\d]{1,8})$')
q_description_cap_re = re.compile(
    r'^[A-Z]{1}[a-z]*?[\s\.]?&?[A-Z]?[a-z]*\.?-([\w\d\W]*$)')
key_cap_re = re.compile(r'(^-?[0-9]*)')
value_cap_re = re.compile(r'^-?[0-9]* {2}([A-z 0-9\W]*$)')
val_range_cap_re = re.compile(
    r'(^-?[0-9.]+:-?[0-9.]+)  (?:Hours|Range)$')


def parseCodebook(cb):
    lines = cb.readlines()

    parsed_cb = coll.OrderedDict()
    i = 0

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
        elif re.match(q_description_re, line):
            q_description = re.findall(q_description_cap_re, line)[0]
            parsed_cb[dataset][topic][q_name]["Description"] = q_description
        elif re.match(key_val_re, line):
            if "Keys" not in parsed_cb[dataset][topic][q_name]:
                parsed_cb[dataset][topic][q_name]["Keys"] = coll.OrderedDict()
            key = re.findall(key_cap_re, line)[0]
            value = re.findall(value_cap_re, line)[0]
            parsed_cb[dataset][topic][q_name]["Keys"][key] = value
        elif re.match(val_range_re, line):
            value_range = re.findall(val_range_cap_re, line)[0]
            parsed_cb[dataset][topic][q_name]["Range"] = value_range
        elif re.match(whitespace_re, line) or re.match(range_title_re, line):
            pass
        else:
            print "Unable to parse line " + str(i) + " - " + line
    return parsed_cb


def writeLookML(nested_cb):

    for dat, top in nested_cb.iteritems():
        file_name = re.sub(r'[/\s\-]', '_', dat)
        lookml = open("{}.view.lookml".format(file_name), "w")

        lookml.write("- view: {}\n".format(file_name))
        lookml.write("  sql_table_name: [ENTER DATA FILE NAME HERE]\n\n\n")
        lookml.write("  fields:\n")
        for tops, que in top.iteritems():
            for ques, des in que.iteritems():
                if ('Keys' in des and 'Range' not in des):
                    lookml.write("  - dimension: {}\n".format(ques.lower()))
                    lookml.write("    sql: ${{TABLE}}.{}\n".format(ques))
                    lookml.write("    label: \"{}\"\n".format(
                        des["Description"].capitalize().rstrip()))
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


def main():
    cb_dict = parseCodebook(codebook)
    writeLookML(cb_dict)


main()
