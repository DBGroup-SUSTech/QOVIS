import os
import sys

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from flask import Flask, request
from gevent import pywsgi

from common.opt_type import OPT_INFO_MAP
from utils.common_io import read_json_obj

app = Flask(__name__)

DATASET = 'data2'
DATA_PATH = os.path.join(ROOT_PATH, 'data', DATASET, 'result')


@app.get("/api/example-list")
def get_example_list():
    lst = os.listdir(DATA_PATH)
    lst.sort()
    return lst


@app.get("/api/dynamic-graph")
def get_trace_data():
    example_name = request.args.get('example_name')
    example_path = os.path.join(DATA_PATH, example_name, 'dynamic_graph.json')
    data = read_json_obj(example_path)
    return data


@app.get("/api/summary-list")
def get_summary_list():
    example_name = request.args.get('example_name')
    summary_path = os.path.join(DATA_PATH, example_name, 'summary')
    if os.path.exists(summary_path):
        lst = os.listdir(summary_path)
        lst.sort()
    else:
        lst = []
    return lst


@app.get("/api/summary-data")
def get_summary_data():
    example_name = request.args.get('example_name')
    summary_name = request.args.get('summary_name')
    summary_filepath = os.path.join(DATA_PATH, example_name, 'summary', summary_name)
    data = read_json_obj(summary_filepath)
    return data


@app.get("/api/opt-data")
def get_opt_data():
    return [info for info in OPT_INFO_MAP.values()]


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 12001), app)
    print('server start')
    server.serve_forever()
