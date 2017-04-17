import csv
import re
import collections as coll
import pandas as pd

allcaps = re.compile('^[^a-z]*$')

lookup_dict = coll.OrderedDict()


def parse_lookup(f):
    with open(f, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        lookup_values = dict()

        # Skip header row
        next(reader)

        for i, row in enumerate(reader):
            if row[3] == "":
                if re.match(allcaps, row[7]):
                    lookup_values['category'] = row[8]
                    lookup_values['q_name'] = re.sub(r'\([^)]*\)', '', row[7])
                    start_pos = int(row[4])
                elif re.match(r'^Universe:.*$', row[7]):
                    lookup_values['universe'] = re.sub(r'Universe:  ', '', row[7])
            elif re.match(r'^[0-9]*$', row[3]):
                a_num = str(int(float(row[3])) + start_pos - 1)
                lookup_values['q_id'] = row[1] + '_' + a_num.zfill(3)
                lookup_dict[row[2] + ':' + a_num] = [lookup_values['category'],
                                                     lookup_values['q_id'],
                                                     lookup_values['q_name'],
                                                     lookup_values['universe']]
        print len(lookup_dict)
        return lookup_dict


def parse_templates(location):

        templates = []
        final_template = coll.OrderedDict()

        for i in range(0, 122):
            df = pd.read_excel(location + "Seq" + str(i+1) + ".xls",
                               header=None).transpose()
            df.columns = ['location', 'answer_key']
            templates.append(df)

        raw = pd.concat(templates).set_index('location').to_dict()['answer_key']

        # Order the dictionary
        raw_df = pd.concat(templates)
        raw_df.columns = ['location', 'answer_key']
        raw_df.set_index('location')
        ordered_raw = coll.OrderedDict((k, raw.get(k)) for k in raw_df.location)

        # Start cleaning
        for k, v in ordered_raw.iteritems():
            # First exclude headers
            if k == v:
                pass
            # Find rows with no % and mark as totals
            elif re.match(r'^((?!%).)*$', v):
                final_template[k] = 'Total'
            elif re.match(r'.*% .*', v):

                # Try splitting to check mirroring (which also indicates total)
                m = re.split(r'% ', v, maxsplit=1)
                if m[0] == m[1]:
                    final_template[k] = 'Total'
                else:
                    # Split for hierarchies
                    h = v.split('% ')
                    # Remove question description
                    h.pop(0)
                    # Strip out random :s
                    h = [re.sub(':', '', s) for s in h]
                    if len(h) == 1:
                        final_template[k] = h[0]
                    else:
                        final_template[k] = ': '.join(h)
            elif re.match(r'.*%.*', v):
                # Split for hierarchies
                h = v.split('%')
                # Remove question description
                h.pop(0)
                # Strip out random :s
                h = [re.sub(':', '', s) for s in h]
                if len(h) == 1:
                    final_template[k] = h[0]
                else:
                    final_template[k] = ': '.join(h)

        print len(final_template)
        # print final_template
        return final_template


def main():

    parse_lookup(f='/Users/Daniel/Downloads/' +
                   'ACS_5yr_Seq_Table_Number_Lookup.csv')
    parse_templates("/Users/Daniel/Downloads/" +
                    "2015_5yr_Summary_FileTemplates/2015_5yr_Templates/")


main()

# re.match(r'(.*)(?=% )', v) == re.match(r'(?<=% )(.*)', v):
