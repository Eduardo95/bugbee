import _io
import json
import inspect
import copy
import pickle
import weakref

import jsonpickle
import hashlib
import types


def get_hash(obj):
    return hashlib.sha256(pickle.dumps(obj)).hexdigest()


def get_code(func):
    try:
        src = inspect.getsource(func)
    except:
        return "[Unable to get source]"
    return src


def has_circ(obj, visited=None):
    if visited is None:
        visited = set()
    if id(obj) in visited:
        return True
    visited.add(id(obj))

    # Handle built-in types and lists/dicts
    if isinstance(obj, (list, tuple)):
        for item in obj:
            if has_circ(item, visited):
                return True
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if has_circ(key, visited) or has_circ(value, visited):
                return True
    elif hasattr(obj, '__dict__'):
        for attr in vars(obj).values():
            if has_circ(attr, visited):
                return True

    visited.remove(id(obj))
    return False


def has_special(obj):
    if isinstance(obj, type):
        return True
    if isinstance(obj, types.GeneratorType):
        return True
    if isinstance(obj, _io.TextIOWrapper):
        return True
    if isinstance(obj, weakref.WeakKeyDictionary):
        return True


    if isinstance(obj, (list, tuple)):
        for item in obj:
            if has_special(item):
                return True
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if has_special(key) or has_special(value):
                return True
    elif hasattr(obj, '__dict__'):
        for attr in vars(obj).values():
            if has_special(attr):
                return True
    return False


def remove_circ(obj, visited=None):
    if isinstance(obj, (list, tuple)):
        result = []
    else:
        result = {}

    if visited is None:
        visited = set()

    obj_id = id(obj)

    if obj_id in visited:
        return "[Circulation]"

    visited.add(obj_id)

    if isinstance(obj, list):
        for i in range(len(obj)):
            if not has_circ(obj[i], visited):
                result.append(obj[i])
            else:
                result.append(remove_circ(obj[i], visited))
    elif isinstance(obj, tuple):
        obj = list(obj)
        for i in range(len(obj)):
            if not has_circ(obj[i], visited):
                result.append(obj[i])
            else:
                result.append(remove_circ(obj[i], visited))
        obj = tuple(obj)
        result = tuple(result)
    elif isinstance(obj, dict):
        for key in obj:
            if not has_circ(obj[key], visited):
                result[key] = obj[key]
            else:
                result[key] = remove_circ(obj[key], visited)
    elif hasattr(obj, '__dict__'):
        for attr in obj.__dict__.keys():
            if not has_circ(obj.__dict__[attr], visited):
                result[attr] = obj.__dict__[attr]
            else:
                result[attr] = remove_circ(obj.__dict__[attr], visited)

    visited.remove(obj_id)
    return result


def to_json(obj):
    # return ""
    temp_obj = obj
    jsonp = lambda obj_tmp: jsonpickle.encode(obj_tmp, make_refs=False)

    if has_circ(obj):
        temp_obj = remove_circ(obj)

    if has_special(temp_obj):
        return "[Unable to pickle]"

    if inspect.isfunction(obj) or inspect.ismethod(obj):
        obj_ref = {}
        if jsonp(temp_obj) != 'null':
            obj_ref = json.loads(jsonp(temp_obj))
        obj_ref = obj_ref | {'$SourceCode$': get_code(obj)} | to_json(vars(temp_obj) if hasattr(temp_obj, '__dict__') else {})
    else:
        if hasattr(temp_obj, '__dict__'):
            # obj_ref = {}
            obj_ref = to_json(vars(temp_obj))
            # obj_ref = to_json(vars(temp_obj))
        else:
            obj_ref = json.loads(jsonp(temp_obj))

    return obj_ref
