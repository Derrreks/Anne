import pandas as pd
import numpy as np
import csv


csv_file_loc = './/data//for-full-text-annotation.csv'

"""
Read in the CSV file and get the required data from it. Format the data.
"""
def get_file_description():
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

"""
Get the lables/headers for each column.
""" 
def get_labels():
    with open(csv_file_loc, newline = '') as csvfile:
        for row in csv.reader(csvfile, delimiter = ",", quotechar='|'):
            return row
        
        
    
"""
Take a row and put all the data into a dictionary.

@param labels represents the name of that column and what type of data it is.
@param row represents all the data in that row.
"""
def gen_row_dictionary(labels, row):
    data = {}
    for i in range(len(labels)):
        data[labels[i]] = row[i]
    return data
    
get_file_description()