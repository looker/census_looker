# Census Looker

This is a set of scripts to make public Census data downloaded from the U.S. Census Bureau's [DataFerrett](http://dataferrett.census.gov/) tool explorable in [Looker](http://wwww.looker.com) and [Google BigQuery](https://cloud.google.com/bigquery/).

There are two scripts, one for uploading the data files that come from DataFerrett into BigQuery and one for transforming the DataFerrett codebook(s) into LookML.

## Schema Generator

Because Census datafiles can be extremely wide, it's impractical for users to write out the schemas by hand. And especially when working with multiple data files that often differ in subtle ways, users need a programmatic way to compare and combine the datafiles into a single file in BigQuery.

The Schema Generator takes the location of one or more datafiles as well as the name(s) of an equal number of tables you want to upload those files to on BigQuery. You call the script from the command line as follows:

```python
python schema_generator.py -f /Users/Documents/datafile1.csv  /Users/Documents/datafile12.csv -t table1 table2
```

It examines a sample of rows in each file and returns a text file that contains schema(s) in the format BigQuery expects for each datafile. If you're combining multiple datafiles, it also returns a query that unions that datafiles together into a single unified table (with `NULL`s filling in columns that do not exist in all datafiles) so that you can create one table containing all your data.

You can find sample input and output files in the [samples](https://github.com/looker/census_looker/tree/master/samples) directory.

## Codebook Parser

DataFerrett dynamically creates a codebook based on which data source and columns you download. This codebook is in plaintext (example in [samples](https://github.com/looker/census_looker/tree/master/samples)) and if you download data from multiple data sources, you'll end up with multiple codebooks.

Because you'd need to cross-reference the data values in each codebook by hand, this approach quickly becomes unwieldy for larger datasets. That's where this parser comes in. It takes the location(s) of the codebook(s) you've downloaded, the names of the table(s) the underlying data lives in on BigQuery, the name of the weighting variable (since this data is generally sampled and each respondent is assigned a "weight" to represent some number of Americans like them), and an optional flag to merge the codebooks into one set of LookML files.

Calling the script from the command line looks like this:

```python
python codebook_parser.py -f "/Users/Documents/codebook1.txt" "/Users/Documents/codebook2.txt" -t "table1" "table2" -m "PWCMPWGT" -o merge
```

When you run this script, the output is three LookML view files (if you've merged the codebooks) or three view files for each input file (if you haven't merged them). The first contains all the variables from the codebook(s), rewritten as LookML dimensions. The second (denoted with a `_filters`) contains all the variables from the codebook(s), rewritten as LookML filter-only dimensions. The third (denoted with a `_measures`) contains a measure to calculate the weighted population of the cohort and a weighted population of the group.

Once loaded into Looker, these files lets you dimensionalize the data and select any combination of dimensions to define your cohort. They also let you set the filter-only fields to independently define your group's characteristics. You can then see how many people meet the filters of your cohort and your group, which allows you to ask questions of the form "How many of [cohort] are in [group]?"

This is useful because it allows you to, for example, define your cohort as all women and your group as voters, allowing you to ask "What percentage of women are voters?" To see the power of this approach in action, visit [http://census.looker.com](https://census.looker.com/embed/explore/census/cps_with_groups)
