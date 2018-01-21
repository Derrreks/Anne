import csv


def get_file_description(csv_file_loc):
    """Read in the CSV file and return the required data"""
    data = {}

    with open(csv_file_loc) as fp:
        reader = list(csv.reader(fp))
        labels = reader[0]
        labels[0] = 'id'
        all_rows = reader[1:]

    for row in all_rows:
        name = int(row[2]) # the name of the PMC file
        if name in data:
            data[name].append(gen_row_dictionary(labels, row))
        else:
            data[name] = [gen_row_dictionary(labels, row)]
    return data


def gen_row_dictionary(labels, row):
    """Take a row and put all the data into a dictionary.

    @param labels represents the name of that column and what type of data it is.
    @param row represents all the data in that row.
    """
    data = {}
    for label, datum in zip(labels, row):
        data[label] = datum
    return data
