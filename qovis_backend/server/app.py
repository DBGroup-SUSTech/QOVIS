import os
import sys
import argparse

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from flask import Flask, request
from gevent import pywsgi

from utils.common_io import read_json_obj, write_json_obj
from align.tree_align_algo_generic import TreeNode, TreeAlignAlgoGeneric

app = Flask(__name__)


args = argparse.ArgumentParser()
args.add_argument('-d', '--dataset', required=True, type=str)

args = args.parse_args()

ARG_DATASET = args.dataset


RES_PATH = os.path.join(ROOT_PATH, 'data', ARG_DATASET, 'result')
TEST_PATH = os.path.join(ROOT_PATH, 'data', ARG_DATASET, 'test')

QUESTION_PATH = os.path.join(ROOT_PATH, 'data_question_results')


@app.get("/api/example-list")
def get_example_list():
    lst = os.listdir(RES_PATH)
    lst = list(filter(lambda x: not x.startswith('.'), lst))
    # remove the cases without trace2.json inside
    lst = list(filter(lambda x: os.path.exists(os.path.join(RES_PATH, x, 'trace2.json')), lst))
    lst.sort()
    return lst


@app.get("/api/trace-data")
def get_trace_data():
    example_name = request.args.get('example_name')
    filepath = os.path.join(RES_PATH, example_name, 'trace2.json')
    data = read_json_obj(filepath)
    return data


@app.get("/api/probe-list")
def get_probe_list():
    lst = os.listdir(TEST_PATH)
    lst = list(filter(lambda x: not x.startswith('.'), lst))
    lst.sort()
    return lst


@app.get("/api/probe-data")
def get_probe_data():
    filename = request.args.get('probe_name')
    filepath = os.path.join(TEST_PATH, filename)
    with open(filepath, 'r') as f:
        data = f.read()
    return data


@app.post("/api/align")
def tree_align():
    # get t0 and t1
    t0 = request.json['src']
    t1 = request.json['dst']

    def json2tree(json) -> TreeNode:
        nodes = []
        for v in json['nodes']:
            node = TreeNode(v['vid'], v['name'], v['str'])
            nodes.append(node)
        vid2node = {node.vid: node for node in nodes}
        for v in nodes:
            v.children = [vid2node[vid] for vid in v.children]
        return vid2node[json['root']]

    t0 = json2tree(t0)
    t1 = json2tree(t1)

    align = TreeAlignAlgoGeneric(t0, t1)

    # min_cost = align.get_min_cost()
    align_tree = align.get_align_tree()
    transforms = align_tree.get_transforms()

    return transforms


@app.post("/api/question-result")
def question_result():
    try:
        # get the post body as a json
        data = request.json
        print(data)
        # save the data to a file
        filename = f'{data["person"]["pid"]} {data["person"]["name"]}.json'
        filepath = os.path.join(QUESTION_PATH, filename)
        write_json_obj(filepath, data, indent=2)
        return ''
    except Exception as e:
        print(e)
        return e



if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 14001), app)
    print('server start')
    server.serve_forever()
