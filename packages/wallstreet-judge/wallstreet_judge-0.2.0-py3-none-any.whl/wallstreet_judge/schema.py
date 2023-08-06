from typing import Any, Optional, List
from enum import Enum

from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):
    class Config:
        extra = 'allow'


class RequestMethod(str, Enum):
    POST = "post"
    GET = "get"
    DELETE = "delete"
    PATCH = "patch"
    PUT = "put"


class AuthHeader(BaseModel):
    Authorization: str
    pass


class TestRequest(BaseModel):
    method: RequestMethod
    path: str
    body: Any
    headers: Any
    query: Any = {}


class Validation(BaseModel):
    key: str
    value: Optional[str]


class ResponseDataTypes(str, Enum):
    OBJECT = 'object'
    ARRAY = 'array'


class TestResponse(BaseModel):
    type: ResponseDataTypes
    validations: List[Validation]


class StoredParameter(BaseModel):
    key: str
    alias: str
    overwrite: bool = False


class Test(BaseModel):
    name: str
    request: TestRequest
    store: List[StoredParameter]
    status_code: int
    response: TestResponse
    points: int = 0

class TestLayer(BaseModel):
    name: str
    tests: List[Test]
    total_points: int


class Result(str, Enum):
    FAIL = "fail"
    PASS = "pass"

class TestResult(BaseModel):
    result: Result
    message: str
    points: int = 0
    detail: str = "None"
    test_request: TestRequest