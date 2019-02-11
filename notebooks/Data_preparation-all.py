#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv
import os
import sys
import re
import pandas as pd
import nltk
csv.field_size_limit(sys.maxsize)


# In[2]:


samples =  {'source_code': [],
            'type': [],
            'cbo': [],
            'wmc': [],
            'rfc': [],
            'lcom': [],
            'nom': [],
            'nopm': [],
            'nosm': [],
            'nof': [],
            'nopf': [],
            'nosf': [],
            'nosi': [],
            'loc': [],
            "commits": [],
            "linesAdded": [],
            "linesDeleted": [],
            "authors": [],
            "minorAuthors": [],
            "majorAuthors": [],
            "authorOwnership": [],
            'target': []
            }
samples_ASTC =  {'source_code': [],
            'type': [],
            'cbo': [],
            'wmc': [],
            'rfc': [],
            'lcom': [],
            'nom': [],
            'nopm': [],
            'nosm': [],
            'nof': [],
            'nopf': [],
            'nosf': [],
            'nosi': [],
            'loc': [],
            "commits": [],
            "linesAdded": [],
            "linesDeleted": [],
            "authors": [],
            "minorAuthors": [],
            "majorAuthors": [],
            "authorOwnership": [],
            'target': []
            }

metrics = ['cbo','wmc','rfc','lcom','nom','nopm','nosm','nof','nopf','nosf','nosi','loc']

metrics2 = ["commits", "linesAdded", "linesDeleted", "authors", "minorAuthors", "majorAuthors", "authorOwnership"]
metrics2_fake = {k:None for k in metrics2}

def get_values(row):
    metrics_values = {}
    for m in metrics2:
        metrics_values[m] = row[m]
    return metrics_values


def tokenize_code(code):
    return ' '.join(nltk.tokenize.wordpunct_tokenize(code))

def process_content(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        source_code = []
        for line in lines:
            # filter comments
            if not re.match("\s*\/\/\s*isComment", line):
                source_code.append(tokenize_code(line))
    text = ' '.join(source_code)
    return text


# In[3]:


dirs_apache = os.listdir("../data/zips/apache")
dirs_apache = [f for f in dirs_apache if f != '.DS_Store']
dirs_fdroid = os.listdir("../data/zips/fdroid")
dirs_fdroid = [f for f in dirs_fdroid if f != '.DS_Store']


# In[4]:


finaldirs_apache = []
for d in dirs_apache:
    if '.zip' not in d:
        dirs = os.listdir("../data/zips/apache/{}/output".format(d))
        dirs = [di for di in dirs if di != '.DS_Store']
        finaldirs_apache.append("../data/zips/apache/{}/output/{}".format(d, dirs[0]))
print(len(finaldirs_apache))

finaldirs_fdroid = []
for d in dirs_fdroid:
    if '.zip' not in d:
        dirs = os.listdir("../data/zips/fdroid/{}/output".format(d))
        dirs = [di for di in dirs if di != '.DS_Store']
        finaldirs_fdroid.append("../data/zips/fdroid/{}/output/{}".format(d, dirs[0]))
print(len(finaldirs_fdroid))


# In[ ]:


repo_groups = [(finaldirs_apache, 'apache'), (finaldirs_fdroid, 'fdroid')]
for group_repo in repo_groups:
    for i, d in enumerate(group_repo[0]):
        print("{}".format(i/len(group_repo[0])))
        print(d)
        look_up = {}
        with open('{}/process.csv'.format(d), 'r') as pro_file:
            pro_csv = csv.DictReader(pro_file, delimiter=';')
            for row in pro_csv:
                look_up["{}_{}".format(row["commit"], row["file"])] = get_values(row)

        with open('{}/yes-refactoring.csv'.format(d), 'r') as pos_file:
            pos_csv = csv.DictReader(pos_file, delimiter=';')
            for row in pos_csv:
                try:
                    samples['source_code'].append(process_content("{}/storage/{}/before/{}".format(d,row['before'],row['path'])))
                except UnicodeDecodeError:
                    samples['source_code'].append(None)
                samples['type'].append(row['type'])
                samples['target'].append(row['refactoring'])
                for m in metrics:
                    samples[m].append(row[m])
                try:
                    metrics2 = look_up["{}_{}".format(row["before"], row["path"])]
                    for k, v in metrics2.items():
                        samples[k].append(v)
                except KeyError:
                    for k, v in metrics2_fake.items():
                        samples[k].append(v)
                    

        with open('{}/no-refactoring.csv'.format(d), 'r') as neg_file:
            neg_csv = csv.DictReader(neg_file, delimiter=';')
            for row in neg_csv:
                try:
                    samples['source_code'].append(process_content("{}/storage/{}/not-refactored/{}".format(d,row['commit'],row['path'])))
                except UnicodeDecodeError:
                    samples['source_code'].append(None)
                samples['type'].append(row['type'])
                samples['target'].append("NO_REFACTORING")
                for m in metrics:
                    samples[m].append(row[m])

                try:
                    metrics2 = look_up["{}_{}".format(row["before"], row["path"])]
                    for k, v in metrics2.items():
                        samples[k].append(v)
                except KeyError:
                    for k, v in metrics2_fake.items():
                        samples[k].append(v)

    df = pd.DataFrame.from_dict(samples)
    df.head()

    df.to_pickle('../data/instances_{}.pkl'.format(group_repo[1]))


# In[ ]:


print("ASTConverter ....")
repo_groups = [(finaldirs_apache, 'apache'), (finaldirs_fdroid, 'fdroid')]
for group_repo in repo_groups:
    for i, d in enumerate(group_repo[0]):
        print("{} from {}".format(i, len(group_repo[0])))
        look_up = {}
        with open('{}/process.csv'.format(d), 'r') as pro_file:
            pro_csv = csv.DictReader(pro_file, delimiter=';')
            for row in pro_csv:
                look_up["{}_{}".format(row["commit"], row["file"])] = get_values(row)

        with open('{}/yes-refactoring.csv'.format(d), 'r') as pos_file:
            pos_csv = csv.DictReader(pos_file, delimiter=';')
            for row in pos_csv:

                samples['source_code'].append(process_content("{}/astconverter/storage/{}/before/{}".format(d,row['before'],row['path'])))
                samples['type'].append(row['type'])
                samples['target'].append(row['refactoring'])
                for m in metrics:
                    samples[m].append(row[m])
                try:
                    metrics2 = look_up["{}_{}".format(row["before"], row["path"])]
                    for k, v in metrics2.items():
                        samples[k].append(v)
                except KeyError:
                    for k, v in metrics2_fake.items():
                        samples[k].append(v)
                    

        with open('{}/no-refactoring.csv'.format(d), 'r') as neg_file:
            neg_csv = csv.DictReader(neg_file, delimiter=';')
            for row in neg_csv:
                samples['source_code'].append(process_content("{}/astconverter/storage/{}/not-refactored/{}".format(d,row['commit'],row['path'])))
                samples['type'].append(row['type'])
                samples['target'].append("NO_REFACTORING")
                for m in metrics:
                    samples[m].append(row[m])

                try:
                    metrics2 = look_up["{}_{}".format(row["before"], row["path"])]
                    for k, v in metrics2.items():
                        samples[k].append(v)
                except KeyError:
                    for k, v in metrics2_fake.items():
                        samples[k].append(v)

    df = pd.DataFrame.from_dict(samples)
    df.head()

    df.to_pickle('../data/instances_astconverter_{}.pkl'.format(group_repo[1]))


# In[ ]:




