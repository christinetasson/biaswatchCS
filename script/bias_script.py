#!/usr/bin/python3
# v3
# Last modified 29/03/2021
# Depedency for genderize: pip install genderize
#
# CSV file delimiter = ;


# imports

import sys, getopt, os
import pandas as pd
import csv, re
from genderize import Genderize
from copy import deepcopy
import numpy as np

# Functions

def open_pd_csv(file):
    # input is a csv file separated with ";"
    # return a panda dataframe, with lowered strings
    #detect separator
    with open(file, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.readline())
        sp = dialect.delimiter
    return (pd.read_csv(file, sep=sp)).applymap(lambda s:s.lower().strip() if type(s) == str else s)


def search_gender(df, chunk_size = 10):
    chunks = list()
    num_chunks = len(df) // chunk_size + 1
    newdf = pd.DataFrame()
    namedf = df['firstname']
    for i in range(num_chunks):
        chunks.append(namedf[i*chunk_size:(i+1)*chunk_size])
    for liste in chunks :
        firstname_list = list()
        gender_list = list()
        proba_list = list()
        gender_liste = Genderize().get(list(liste))
        for fname in Genderize().get(liste):
            # add data
            firstname_list.append(fname["name"])
            gender_list.append(fname["gender"])
            proba_list.append(fname["probability"])
        df0 = pd.DataFrame(data={'firstname':firstname_list, 'gender':gender_list, 'probability':proba_list})
        newdf = newdf.append(df0, ignore_index = True)
    return newdf

# Options and Arguments of the script

def get_args(argv):
    inputfile = ''
    outputfile = ''
    statfile = 'stats.csv'
    options = []
    try:
        opts, args = getopt.getopt(argv,"hgrci:o:s:",["gender","region", "compute","ifile", "ofile", "sfile"])
    except getopt.GetoptError:
        print (
            ''' biaswatch.py -i data_file.csv
 # fill the region and gender columns, in the input file data_file.csv
 # compute the stat and save it in stats.csv
biaswatch.py -i input_file.csv -o output_file.csv -s stats_file.csv   
 # fill the region and gender columns, in a new output_file 
 # compute the stat and save it in stats_file.csv
biaswatch.py -i  data_file.csv -g  # add and fill the gender and probability columns
biaswatch.py -i  data_file.csv -r  # add and fill the country and region columns
biaswatch.py -i  data_file.csv -c  # compute the stat of existing columns gender and region
''')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print (
                '''biaswatch.py data_file.csv
 # fill the region and gender columns, in the input file data_file.csv
 # compute the stat and save it in stats.csv
biaswatch.py -i input_file.csv -o output_file.csv -s stats_file.csv   
 # fill the region and gender columns, in a new output_file 
 # compute the stat and save it in stats_file.csv
biaswatch.py -i data_file.csv -g   # add and fill the gender and probability columns
biaswatch.py -i data_file.csv -r  # add and fill the country and region columns
biaswatch.py -i data_file.csv -c  # compute the stat of existing columns gender and region
    ''')
            sys.exit(1)
        else:
            if opt in ("-i", "--ifile"):
                inputfile = arg
            if opt in ("-o", "--ofile"):
                outputfile = arg
            if opt in ("-s", "--sfile"):
                statfile = arg
            if opt in ("-g", "--gender"):
                options.append("gender")
            if opt in ("-r", "--region"):
                options.append("region")
            if opt in ("-c", "--compute"):
                options.append("compute")
    if inputfile == '':
        raise IOError
    if outputfile == '':
        outputfile = inputfile
    if len(options) == 0:
        options = ['gender', 'region', 'compute']
    name = os.path.splitext(outputfile)[0].split('/')[-1]
    return (inputfile, outputfile, statfile, options,name)
         


# Main program

if __name__ == "__main__":
    inputfile, outputfile, statfile, options, name = get_args(sys.argv[1:])
    genderfile = "firstname_gender_proba.csv"
    countryfile = "country_area.csv"

    csv_input = open_pd_csv(inputfile)
    
    if 'gender' in options:
        csv_gender = open_pd_csv('firstname_gender_proba.csv')
        # select only first firstnames
        csv_input['all_firstname']=csv_input["firstname"]
        csv_input['firstname']=csv_input["firstname"].str.split(expand=True)
        try:
            # compute missing firstnames if there are any, fill and save csv_gender
            missing = csv_input[~csv_input['firstname'].isin(csv_gender['firstname'])]
            missing = search_gender(missing)
            csv_gender = pd.concat([csv_gender, missing])
            csv_gender.to_csv(r'firstname_gender_proba.csv', index=False, header=True, sep =";")
        except KeyError as err:
            print('all names already in firstname_gender_proba.csv')
        # if gender filled by hand, then proba  is 1.0
        if 'gender' in csv_input.columns:
            if 'probability' not in csv_input.columns:
                csv_input.loc[~pd.isnull(csv_input['gender']), 'probability'] = 1.0
        # fill csv_input data frame with gender
        common_col = list(set(csv_input.columns).intersection(set(csv_gender.columns)))
        if 'gender'in common_col:
            csv_input = csv_input.fillna(csv_gender)
        else:
            csv_input = pd.merge(csv_input, csv_gender, on=common_col, how="left")
        
        nan_gender =  csv_input.loc[(csv_input['probability']<=0.6)|(pd.isnull(csv_input['gender']))]
        if not nan_gender.empty:
            print("epicene firstnames : ",len(nan_gender)," excluded \n",nan_gender['firstname'])
            

        
    if 'region' in options:
        csv_region = open_pd_csv('country_area.csv')
        # fill csv_input data frame with gender
        common_col = list(set(csv_input.columns).intersection(set(csv_region.columns)))
        csv_input = pd.merge(csv_input,csv_region, how="left", on=common_col)
    # save filled dataframe in outputfile
    csv_input.to_csv(outputfile, index=False, header=True, sep =";")
            
    if 'compute' in options:
        csv_stat = pd.DataFrame()
        total = len(csv_input)
        try:
            if 'area' in csv_input.columns:
                area_mean =pd.DataFrame({name:(round(csv_input['area'].value_counts()/total,3))})
                csv_stat= pd.concat([csv_stat, area_mean.T],axis='columns' )
            csv_stat['total'] = total          
            if 'gender' in csv_input.columns:
                gender = pd.DataFrame({name:csv_input['gender'].value_counts()})
                csv_stat= pd.concat([csv_stat, gender.T],axis='columns' )
                csv_stat['women %'] = round(csv_stat['female']/total,3)
                print(csv_stat.T)
                csv_stat.to_csv(statfile, header=True, sep = ";", mode='a')
        except ZeroDivisionError:
            print("no lines in your csv")
    


            
