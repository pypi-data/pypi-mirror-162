from typing import Any, Optional, List
from enum import Enum

from pydantic import BaseModel


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


class Comparator(str, Enum):
    EQ = "=="
    GTE = ">="
    LTE = "<="
    GT = ">"
    LT = "<"


class Validation(BaseModel):
    key: str
    value: Optional[str]
    comparator: Optional[str]


class ResponseDataTypes(str, Enum):
    OBJECT = 'object'
    ARRAY = 'array'


class TestResponse(BaseModel):
    type: ResponseDataTypes
    validations: List[Validation]


class StoredParameter(BaseModel):
    key: str
    alias: str


class Test(BaseModel):
    name: str
    request: TestRequest
    store: List[StoredParameter]
    status_code: int
    response: TestResponse
    points: Optional[int]


class TestLayer(BaseModel):
    name: str
    tests: List[Test]


class TestResult(str, Enum):
    FAIL = "fail"
    PASS = "pass"
