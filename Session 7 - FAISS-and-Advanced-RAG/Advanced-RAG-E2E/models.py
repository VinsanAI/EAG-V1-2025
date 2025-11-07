from pydantic import BaseModel
from typing import List

# Input/Output Models for Tools

class AddInput(BaseModel):
    a: int
    b: int

class AddOutput(BaseModel):
    result: int

class TwoFloatInputs(BaseModel):
    a: float
    b: float

class OneFloatOutput(BaseModel):
    result: float

class OneFloatInput(BaseModel):
    a: float

class SqrtInput(BaseModel):
    a: int

class SqrtOutput(BaseModel):
    result: float

class StringsToIntsInput(BaseModel):
    string: str

class StringsToIntsOutput(BaseModel):
    ascii_values: List[int]

class ExpSumInput(BaseModel):
    int_list: List[int]

class ExpSumOutput(BaseModel):
    result: float

class ScheduleMeetingInput(BaseModel):
    audience_email_dl: str
    meeting_date: str
    meeting_duration: int
    start_time: str
