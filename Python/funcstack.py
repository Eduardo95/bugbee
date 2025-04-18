from utils import to_json
from enum import Enum
import re
import json

LAMBDA = "Lambda"
FUNC = "Func"
ASYNCFUNC = "AsyncFunc"

class FuncID:
    def __init__(self, file_path, line_no, func_type, func_name, func_hash):
        self.file_path = file_path
        self.line_no = line_no
        self.func_type = func_type
        self.func_name = func_name
        self.func_hash = func_hash

    def __str__(self):
        if self.file_path == None:
            return self.func_name
        if self.func_type == LAMBDA:
            return f"{self.file_path}@line{self.line_no}/{self.func_type}"
        return f"{self.file_path}@line{self.line_no}/\
{self.func_type}@{self.func_name}"

    def __repr__(self):
        if self.file_path == None:
            return self.func_name
        return f"{self.__str__()},{self.func_hash}"

    @staticmethod
    # @func_str: the __str__ output of a FuncID
    # @func_hash: the hash value of that function definition
    def parse(func_str):
        pattern = r'([^@]+)@line(\d+)/([^@]+)(?:@([^,]+))?,(.+)'
        match = re.match(pattern, func_str.strip())

        if match:
            file_path = match.group(1)
            line_number = int(match.group(2))
            func_type = match.group(3)
            func_name = match.group(4)
            func_hash = match.group(5)

            if func_type == LAMBDA:
                func_name = None
            return FuncID(file_path, line_number, func_type, \
                    func_name, func_hash)

class FuncStack:
    def __init__(self, func_id_str, caller_func_stack=None, \
            pre_run_args=None, post_run_args=None, return_val=None):
        if caller_func_stack == None:
            # ENTRY POINT
            self.func_id = func_id_str
        else:
            # Parse the complete function ID string to a FuncID object
            self.func_id = FuncID.parse(func_id_str)
        self.pre_run_args = pre_run_args
        self.post_run_args = post_run_args
        self.return_val = return_val
        self.caller_func_stack = caller_func_stack

        # index and callee are automatically generated
        if caller_func_stack is not None:
            self.index = caller_func_stack.index + \
                    [len(caller_func_stack.callee)]
        else:
            self.index = []
        self.callee = []

class FuncStackEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FuncStack):
            return {
                    "index": obj.index,
                    "func_id": obj.func_id,
                    "pre_run_args": obj.pre_run_args,
                    "post_run_args": obj.post_run_args,
                    "return_val": obj.return_val,
                    "callee": obj.callee
                    }
        elif isinstance(obj, FuncID):
            return {
                    "file_path": f"{obj.file_path}@line{obj.line_no}",
                    "func_name": f"{obj.func_type}@{obj.func_name}",
                    "func_hash": obj.func_hash
                    }
        return super().default(obj)
