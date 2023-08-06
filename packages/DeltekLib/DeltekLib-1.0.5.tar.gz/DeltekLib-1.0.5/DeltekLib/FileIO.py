# Deltek Python Library
# Copyright 2021

import os
import csv


def file_exists(file: str) -> bool:
    return os.path.exists(file)


def file_contains_text(file: str, text: str):
    with open(file) as fInfo:
        if text not in fInfo.read():
            return False
        else:
            return True


def read_csv_file(filename):
    data = []
    with open(filename, 'rt') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            data.append(row)
    return data
