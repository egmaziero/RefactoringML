import csv
import os
import sys
import re
import pandas as pd
import nltk
csv.field_size_limit(sys.maxsize)


samples =  {'source_code': [],
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
                source_code.append(tokenize_code(line).replace('"', '""').replace("'", "''"))
    text = ' '.join(source_code)
    return text





dirs_apache = os.listdir("../data/apache")
dirs_fdroid = os.listdir("../data/fdroid")
dirs_github = os.listdir("../data/github")




groups = [(dirs_apache, 'apache'), (dirs_fdroid, 'fdroid'), (dirs_github, 'github')]
for repo in groups:
    for i, d in enumerate(repo[0]):
        print("{} from {}".format(i, len(repo[0])))
        look_up = {}
        with open('{}/process.csv'.format(d), 'r') as pro_file:
            pro_csv = csv.DictReader(pro_file, delimiter=';')
            for row in pro_csv:
                look_up["{}_{}".format(row["commit"], row["file"])] = get_values(row)

        with open('{}/yes-refactoring.csv'.format(d), 'r') as pos_file:
            pos_csv = csv.DictReader(pos_file, delimiter=';')
            for row in pos_csv:
                try:
                    samples['source_code'].append("{}/storage/{}/before/{}".format(d,row['before'],row['path']))
                except KeyError:
                    samples['source_code'].append(None)
                    
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
                    samples['source_code'].append("{}/storage/{}/not-refactored/{}".format(d,row['commit'],row['path']))
                except UnicodeDecodeError:
                    samples['source_code'].append(None)
                    
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
    df.to_pickle('../data/instances_{}.pkl'.format(repo[1]))
