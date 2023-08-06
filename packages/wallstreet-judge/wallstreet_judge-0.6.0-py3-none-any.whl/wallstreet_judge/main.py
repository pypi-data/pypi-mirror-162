import json
import traceback
from typing import Dict, Any
import os
import logging
import re

import typer
from requests import request
from colorama import Fore, Style

from wallstreet_judge.utils import get_logger
from .schema import Result, Test, TestLayer, TestRequest, TestResult, ResponseDataTypes

app = typer.Typer()

state = {}


def get_alias(parameter: str) -> str:
    if parameter.startswith("$"):
        alias = parameter[1:]
        return state[alias]
    return parameter

def parse_nested_validation(key: str, value: str, response_data: Any, test: Test):
    fields = key.split(".$")
    data = response_data
    for field in fields:
        is_array_elem = re.match(r"^\[(\d+)\]$", field)
        if is_array_elem is not None:
            data = data[int(is_array_elem.group(1))] # extract element from array
            continue
        data = data.get(field, None)
        if data == None:
            return TestResult(
                result=Result.FAIL, message="response did not have expected schema", 
                points=0, detail=f"key {key} missing from response body", test_request=test.request
            )
    if str(data) == str(value):
        return TestResult(result=Result.PASS, message="success", points=test.points, test_request=test.request, detail="nest body is valid")
    else:
        return TestResult(result=Result.FAIL, message=f"key {key} has incorrect value", test_request=test.request, detail=f"expected {str(value)}, received: {str(data)}")

def preprocess(test: Test):
    splits = test.request.path.split("/")

    splits = [str(get_alias(split)) for split in splits]
    test.request.path = "/".join(splits)

    for key, value in test.request.body.items():
        if type(value) == str:
            test.request.body[key] = get_alias(value)

    for key, value in test.request.headers.items():
        test.request.headers[key] = get_alias(value)
        if key == "Authorization":
            test.request.headers[key] = f"Token {get_alias(value)}"
    
    for index, validation in enumerate(test.response.validations):
        if validation.value is not None:
            test.response.validations[index].value = get_alias(validation.value)
    return test

def is_response_valid(test: Test, response_data: Any, test_request:TestRequest)->TestResult:

    for validation in test.response.validations:
        if (".$" in validation.key or ".[" in validation.key) and validation.value is not None:
            nested_validation_result = parse_nested_validation(validation.key, validation.value, response_data=response_data, test=test)
            if nested_validation_result.result == Result.FAIL:
                return nested_validation_result
            continue
        if validation.key not in response_data:
            return TestResult(result=Result.FAIL, message=f"Expected key {validation.key} not found in response", test_request=test_request, detail=f"expected keys: {[v.key for v in test.response.validations]}, received: {response_data.keys()}")
        if validation.value is None:
            continue  # we're only checking for existence of the field
        elif not str(validation.value) == str(response_data[validation.key]):
            return TestResult(
                result=Result.FAIL, message=f"key \"{validation.key}\" has incorrect value", 
                detail=f"expected value: {str(validation.value)}, received: {str(response_data[validation.key])}", test_request=test_request
            )
    return TestResult(result=Result.PASS, message="Successful",detail="Response body validated", points=test.points, test_request=test_request)


def print_result_summary(results: Dict[str, Dict[str, TestResult]],logger: logging.Logger):
    for layer in results:
        points = 0
        logger.info(Style.RESET_ALL)
        for test_name, test_result in results[layer].items():
            logger.debug(Fore.BLACK + f"Request: path: {test_result.test_request.path}, body: {test_result.test_request.body}, headers: {test_result.test_request.headers}")
            if test_result.result == Result.FAIL:
                logger.info(Fore.RED + f"{test_name} FAILED. message: {test_result.message}")
                logger.debug(Fore.RED + f"detail: {test_result.detail}")
            else:
                logger.info(Fore.GREEN + f"{test_name} PASSED. message: {test_result.message}")
                logger.debug(Fore.GREEN + f"detail: {test_result.detail}")
            points += test_result.points
        logger.info(Style.RESET_ALL)

        failed = len(list(filter(lambda x: x.result == Result.FAIL, results[layer].values())))
        total = len(results[layer])
        if failed == 0:
            logger.info(Fore.GREEN + Style.BRIGHT +
                  f"{layer} PASSED. {total}/{total} Successful")
        else:
            logger.info(Fore.RED + Style.BRIGHT +
                  f"{layer} FAILED. {total - failed}/{total} Successful")
        logger.info(Fore.BLUE + Style.BRIGHT + f"Points Received: {points}")
        logger.info(Fore.LIGHTBLACK_EX +
              f"===============================================")


@app.command()
def test_runner(
        port: int = typer.Argument(default=8000, help="The port at which your app is running", show_default=True),
        level: int = typer.Argument(default=logging.INFO, help="Logging level")
    ):

    logger = get_logger(__name__, level=level)

    current_dir_name = os.path.dirname(os.path.realpath(__file__))

    os.chdir(current_dir_name)

    data_dir = os.path.join(os.getcwd(), "data")
    test_files = ["auth.json", "sectors.json", "stocks.json", "orders.json", "market.json", "holdings.json"]

    total = len(test_files)
    logger.info(f"{total} Layers to test")
    results = {}
    completed = 0
    for test_file in test_files:
        with open(os.path.join(data_dir, test_file), "r+") as file:
            test_layer = json.load(file)
            test_layer = TestLayer(**test_layer)
            results[test_layer.name] = {}
            for test in test_layer.tests:
                try:
                    test = preprocess(test)
                    response = request(
                        method=test.request.method, json=test.request.body, 
                        headers=test.request.headers, url=f"http://localhost:{port}/api/v1/{test.request.path}",
                        params=test.request.query
                    )
                    if response.status_code != test.status_code:
                        results[test_layer.name][test.name] = TestResult(
                            result=Result.FAIL, message="Wrong Status code", detail=f"Expected {test.status_code}, Received: {response.status_code}", 
                            test_request=test.request
                        )
                        continue
                    elif response.status_code >= 300:
                        # not pulling out any data from 300+ status codes
                        results[test_layer.name][test.name] = TestResult(
                            result=Result.PASS, message="Successful",detail="Non 2XX status codes matched", points=test.points, test_request=test.request
                        )
                        continue
                    if response.status_code == 204:
                        results[test_layer.name][test.name] = TestResult(
                            result=Result.PASS, message="Successful", detail="No content expected", points=test.points, test_request=test.request
                        )
                        continue
                    response_data = response.json()

                    if test.response.type == ResponseDataTypes.ARRAY:
                        response_data = response_data[0]
                    validation_result = is_response_valid(test, response_data=response_data, test_request=test.request)
                    if validation_result.result == Result.FAIL:
                        results[test_layer.name][test.name] = validation_result
                        continue
                    for parameter in test.store:
                        if parameter.alias not in state or parameter.overwrite:
                            state[f"{parameter.alias}"] = response_data[parameter.key]
                    results[test_layer.name][test.name] = validation_result
                except KeyError as ke:
                    results[test_layer.name][test.name] = TestResult(result=Result.FAIL, message=f"Test depends on a previous test that has failed. Skipped for now", detail=f"needs value {str(ke)} from a previous test", test_request=test.request)
                except Exception as ex:
                    results[test_layer.name][test.name] = TestResult(result=Result.FAIL, message=f"Internal Error: {type(ex)}", detail=str(ex), test_request=test.request)
                    logger.info("")
        completed += 1
        logger.info(f"Done")
    print_result_summary(results=results,logger=logger)
