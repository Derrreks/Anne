import pandas as pd
import numpy as np
import csv


csv_file_loc = 'for-full-text-annotation.csv'


def get_file_description():
    """Read in the CSV file and return the required data"""
    data = {}
    all_rows = pd.read_csv(csv_file_loc)
    all_rows = np.asarray(all_rows)

    labels = get_labels()
    labels[0] = "id"
    for i in range(1, len(all_rows)):
        row = all_rows[i]
        name = row[2] # the name of the PMC file
        if name in data:
            data[name].append(gen_row_dictionary(labels, row))
        else:
            data[name] = [gen_row_dictionary(labels, row)]

    return data


def get_labels():
    """Get the labels/headers for each column"""
    with open(csv_file_loc, newline = '') as csvfile:
        for row in csv.reader(csvfile, delimiter = ",", quotechar='|'):
            return row


def gen_row_dictionary(labels, row):
    """Take a row and put all the data into a dictionary.

    @param labels represents the name of that column and what type of data it is.
    @param row represents all the data in that row.
    """
    data = {}
    for i in range(len(labels)):
        data[labels[i]] = row[i]
    return data
