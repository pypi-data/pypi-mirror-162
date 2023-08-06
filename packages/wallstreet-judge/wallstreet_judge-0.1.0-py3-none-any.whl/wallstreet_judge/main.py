from cgi import test
import json
from typing import List, Any
import os

import typer
from requests import request
from colorama import Fore, Style

from .schema import Test, TestLayer, TestResult, ResponseDataTypes

app = typer.Typer()

state = {}


def get_alias(parameter: str) -> str:
    if parameter.startswith("$"):
        alias = parameter[1:]
        return state[alias]
    return parameter


def preprocess(test: Test):
    splits = test.request.path.split()
    splits = list(map(get_alias, splits))
    test.request.path = "/".join(splits)

    for key, value in test.request.body.items():
        test.request.body[key] = get_alias(value)

    for key, value in test.request.headers.items():
        test.request.headers[key] = get_alias(value)
    return test


def is_response_valid(test: Test, response_data: Any):
    for validation in test.response.validations:
        if validation.key not in response_data:
            return False
        if validation.comparator is None and validation.value is None:
            continue  # we're only checking for existence of the field
        elif not eval(f"{validation.value} {validation.comparator} {response_data[validation.key]}"):
            return False
    return True


def print_result_summary(results):
    for layer in results:
        failed = 0
        failed = len(list(filter(lambda x: x ==
                                 TestResult.FAIL, results[layer].values())))
        total = len(results[layer])
        if failed == 0:
            print(Fore.GREEN + Style.BRIGHT +
                  f"{layer} PASSED {total}/{total}")
        else:
            print(Fore.RED + Style.BRIGHT +
                  f"{layer} FAILED. {total - failed}/{total}")
        print(Fore.LIGHTBLACK_EX +
              f"===============================================")


@app.command()
def test_runner(port: int = typer.Argument(default=8000, help="The port at which your app is running", show_default=True)):
    current_dir_name = os.path.dirname(os.path.realpath(__file__))
    print(current_dir_name)

    os.chdir(current_dir_name)

    data_dir = os.path.join(os.getcwd(), "data")
    test_files = ["auth.json", "sectors.json"]

    total = len(test_files)
    print(f"{total} Layers to test")
    results = {}
    completed = 0
    for test_file in test_files:
        with open(os.path.join(data_dir, test_file), "r+") as file:
            test_layer = json.load(file)
            test_layer = TestLayer(**test_layer)
            results[test_layer.name] = {}
            print(f"Running {test_layer.name}", end="")
            for test in test_layer.tests:
                try:
                    test = preprocess(test)
                    response = request(method=test.request.method, json=test.request.body,
                                       headers=test.request.headers, url=f"http://localhost:{port}/{test.request.path}")
                    if response.status_code != test.status_code:
                        results[test_layer.name][test.name] = TestResult.FAIL
                        continue
                    elif response.status_code >= 300:
                        # not pulling out any data from 300+ status codes
                        results[test_layer.name][test.name] = TestResult.PASS
                        continue
                    response_data = response.json()

                    if test.response.type == ResponseDataTypes.ARRAY:
                        response_data = response_data[0]
                    if not is_response_valid(test, response_data=response_data[0]):
                        results[test_layer.name][test.name] = TestResult.FAIL
                        continue
                    for parameter in test.store:
                        state[f"{parameter.alias}"] = response_data[parameter.key]
                    results[test_layer.name][test.name] = TestResult.PASS
                except Exception as ex:
                    results[test_layer.name][test.name] = TestResult.FAIL
                print(". ", end="")
        completed += 1
        print(f"Done")
    print_result_summary(results=results)
