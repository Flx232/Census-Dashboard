import os
import csv

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def process_txt(file_path, delimiter):
    data = []
    header = []
    with open(file_path, 'r') as file:
        for index, line in enumerate(file):
            line = line.strip()
            if index == 0:
                header = line.split(delimiter)
            else:
                row = line.split(delimiter)
                datalet = {}
                for index, column in enumerate(header):
                    datalet[column] = row[index]
                data.append(datalet)
        file.close()
    return data

def process_csv(data, file_path):
    with open(file_path, 'w', newline='') as file:
        if data:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        file.close()
