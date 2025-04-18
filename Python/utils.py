import json
import inspect
import black
import copy
import pickle
import jsonpickle
import hashlib

# Get sha256 of any object's memory byte
def get_hash(obj):
    return hashlib.sha256(pickle.dumps(obj)).hexdigest()

# Get the source code of any function or method object
def get_code(func):
    src = inspect.getsource(func)
    cleaned_src = black.format_str(src, mode=black.FileMode())
    return cleaned_src

# Check whether a object has circular references
def has_circ(obj, visited = None):
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

# Remove the circular references in an object to make it fit for serialization
def remove_circ(obj, visited = None):
    # Create a weakset if not exists
    if visited is None:
        visited = set()

    # Get the identifer of obj
    obj_id = id(obj)

    # Mark this obj as circulation with its unique hash value
    if obj_id in visited:
        return f"[Circulation] {obj.__class__}@{get_hash(obj)}"

    # Mark this obj as visited
    visited.add(obj_id)

    # Recursively check its sub-obj
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = remove_circ(obj[i], visited)
    elif isinstance(obj, tuple):
        obj = list(obj)
        for i in range(len(obj)):
            obj[i] = remove_circ(obj[i], visited)
        obj = tuple(obj)
    elif isinstance(obj, dict):
        for key in obj:
            obj[key] = remove_circ(obj[key], visited)
    elif hasattr(obj, '__dict__'):
        for attr in obj.__dict__.keys():
            obj.__dict__[attr] = remove_circ(obj.__dict__[attr], visited)

    # Unmark this obj when finish iterating it
    visited.remove(obj_id)
    return obj


def to_json(obj):
    temp_obj = obj
    jsonp = lambda obj: jsonpickle.encode(obj, make_refs=False)
    
    # Remove circulation first
    if has_circ(temp_obj):
        temp_obj = remove_circ(copy.deepcopy(temp_obj))
    
    # Serializing any object, but first check whether it's function object
    if inspect.isfunction(temp_obj) or inspect.ismethod(temp_obj):
        obj_ref = {}
        if jsonp(temp_obj) != 'null':
            obj_ref = json.loads(jsonp(temp_obj))
        obj_ref = obj_ref | {'$SourceCode$': get_code(temp_obj)} \
                | (vars(temp_obj) if hasattr(temp_obj, '__dict__') else {})
        #obj_json = json.dumps(obj_ref)
    else:
        if hasattr(temp_obj, '__dict__'):
            obj_ref = json.loads(jsonp(temp_obj)) \
                    | to_json(vars(temp_obj))
            # to_json returns a json object, and json.loads cannot load this json object
            #obj_json = json.dumps(obj_ref)
        else:
            obj_ref = json.loads(jsonp(temp_obj))
            #obj_json = jsonp(temp_obj)

    # Instead of outputing json, output a deepcopyed jsonable object
    return obj_ref
