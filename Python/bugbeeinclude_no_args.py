import os
from funcstack import FuncID, FuncStack, FuncStackEncoder
import atexit
import copy
import json
import sys
sys.setrecursionlimit(10000)


def Bugbee_build(func_id, args, kwargs):
    global __curr_func_stack__
    new_func_stack = FuncStack(func_id, __curr_func_stack__, json.dumps([]))
    __curr_func_stack__.callee.append(new_func_stack)
    __curr_func_stack__ = new_func_stack


def Bugbee_complete(args, kwargs, return_val):
    global __curr_func_stack__
    __curr_func_stack__.post_run_args = json.dumps([])
    __curr_func_stack__.return_val = json.dumps([])
    __curr_func_stack__ = __curr_func_stack__.caller_func_stack


def Bugbee_execLambda(func_id, return_val):
    global __curr_func_stack__
    new_func_stack = FuncStack(func_id, __curr_func_stack__, json.dumps([]))
    __curr_func_stack__.callee.append(new_func_stack)
    __curr_func_stack__ = new_func_stack
    __curr_func_stack__.post_run_args = json.dumps([])
    __curr_func_stack__.return_val = json.dumps([])
    __curr_func_stack__ = __curr_func_stack__.caller_func_stack
    return return_val


def writeTrace(root_node, config=None):
    # TODO
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../examples/trace.json')), 'w') as trace_file:
        json.dump(__Bugbee__, trace_file, cls=FuncStackEncoder, indent=2)


if not hasattr(globals(), "__Bugbee__"):
    __Bugbee__ = FuncStack("ENTRY_POINT")
    __curr_func_stack__ = __Bugbee__


if not hasattr(globals(), "__has_registered__"):
    __has_registered__ = atexit.register(writeTrace, __Bugbee__)
