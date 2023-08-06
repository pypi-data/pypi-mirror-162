import csv
import json
import os
import shutil
from collections import defaultdict
from datetime import datetime
from os import listdir
from pathlib import Path

import boto3
from dateutil import parser


def get_bucket(aws_access_key_id=None, aws_secret_access_key=None):
    s3 = None
    if aws_access_key_id == None and aws_secret_access_key == None:
        s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                            region_name="us-east-1")
    else:
        s3 = boto3.resource('s3', region_name="us-east-1")
    buck = s3.Bucket('auxdata.johnsnowlabs.com')
    return buck


def read_metadata(bucket, metadata_path=None):
    if metadata_path == None:
        try:
            # set aws credentials
            bucket.download_file('clinical/models/metadata.json', f"{os.path.abspath(os.getcwd())}/metadata.json")
            # print ( f"Model reference file is downloaded as {os.path.abspath(os.getcwd())}/metadata.json")
            lines = []
            with open(f'{os.path.abspath(os.getcwd())}/metadata.json', 'r') as file:
                lines = file.readlines()
        except:
            print('AWS AccessDenied. Please add metadata.json path as metadata_path parameter manually')
            return []

    else:
        lines = []
        with open(metadata_path, 'r') as file:
            lines = file.readlines()

    res_dict = []
    for item in lines:
        line = item.replace('\n', '')
        dic = json.loads(line)
        res_dict.append(dic)

    return res_dict


def extract_model(item):
    date_str = item['time'][0:10]
    datetime_obj = parser.parse(item['time'])
    timestamp = (int(datetime.timestamp(datetime_obj) * 1000))
    lib_version_items = item['libVersion']['parts']
    if len(lib_version_items) == 2:
        lib_version_items.append('0')
    spark_version_items = item['sparkVersion']['parts']
    if len(spark_version_items) == 1:
        spark_version_items.append('0')
    model_name = item['name'] + '_' + item['language'] + '_' + str(lib_version_items[0]) + '.' + str(
        lib_version_items[1]) + '.' + str(lib_version_items[2]) + '_' + str(spark_version_items[0]) + '.' + str(
        spark_version_items[1]) + '_' + str(timestamp) + '.zip'
    strmodel = f"clinical/models/{model_name}"
    return strmodel


def retrieve_spark_version(item):
    spark_version_items = item['sparkVersion']['parts']
    if len(spark_version_items) == 1:
        spark_version_items.append('0')
    return spark_version_items


def get_key(item):
    return item['name'] + '_' + item['language']


def get_possibles_models(model_name, language, metadata_dict):
    metadata_pair = [(get_key(item), item) for item in metadata_dict]
    res = defaultdict(list)
    for k, v in metadata_pair:
        res[k].append(v)
    str_model_name = f"{model_name}_{language}"
    return res[str_model_name]


def get_milliseconds(item):
    datetime_obj = parser.parse(item['time'])
    return (int(datetime.timestamp(datetime_obj) * 1000))


def download_and_extract_model(model_name, language, cache_folder, bucket, metadata_dict):
    models = get_possibles_models(model_name, language, metadata_dict)
    models = sorted(models, key=lambda x: get_milliseconds(x), reverse=True)
    models = list(models)
    if models:
        expected_model = models[0]
        model_name = extract_model(expected_model)
        file_name = model_name[16:-4]
        aa = set(listdir(cache_folder))
        local_file_name = f"{cache_folder}/{file_name}.zip"
        if file_name not in aa:
            bucket.download_file(model_name, local_file_name)
            shutil.unpack_archive(local_file_name, f"{cache_folder}/{file_name}")
            os.remove(local_file_name)
        else:
            print(f'The model {file_name} was found in {cache_folder}')
    else:
        print(f"The model {model_name} was not found")


def freeze_models(models_file, aws_access_key_id=None, aws_secret_access_key=None,
                  cache_folder=f"{Path.home()}/cache_pretrained"):
    with open(models_file, mode='r') as infile:
        reader = csv.reader(infile)
        bucket = get_bucket(aws_access_key_id, aws_secret_access_key)
        metadata_dict = read_metadata(bucket)
        for row in reader:
            model_name = row[0]
            language = row[1]
            print(f"{model_name},{language} is starting to download")
            download_and_extract_model(model_name, language, cache_folder, bucket, metadata_dict)
