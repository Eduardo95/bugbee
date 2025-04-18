import json
from func_stack import FuncStack, FuncID


class Comparator:
    def __init__(self, base_func_stack_file, buggy_func_stack_file):
        with open(base_func_stack_file, 'r') as f1, open(buggy_func_stack_file, 'r') as f2:
            self.base_func_stack_json = json.load(f1)
            self.buggy_func_stack_json = json.load(f2)
        self.base_func_stack = FuncStack(self.base_func_stack_json)
        self.buggy_func_stack = FuncStack(self.buggy_func_stack_json)
        self.count = {}

    def compare(self):
        for i in range(min(len(self.base_func_stack.callee), len(self.buggy_func_stack.callee))):
            baseFS = FuncStack.get_func_stack(self.base_func_stack, [i])
            buggyFS = FuncStack.get_func_stack(self.buggy_func_stack, [i])
            if not FuncID.compare_func_id(baseFS.func_id, buggyFS.func_id):
                print("cannot compare level 1")
                break
            self.compare_func_stack([i], [i])
        for key, value in self.count.items():
            print(value, key)

    def record_diff(self):
        pass

    def compare_func_stack(self, base_index, buggy_index):
        baseFS = FuncStack.get_func_stack(self.base_func_stack, base_index)
        buggyFS = FuncStack.get_func_stack(self.buggy_func_stack, buggy_index)
        is_before_changed = (baseFS.before_args != buggyFS.before_args)
        is_after_changed = (baseFS.after_args != buggyFS.after_args)
        is_return_changed = (baseFS.return_val != buggyFS.return_val)
        is_code_changed = (baseFS.func_id.func_hash != buggyFS.func_id.func_hash)
        diff = (base_index, buggy_index, is_before_changed, is_after_changed, is_return_changed, is_code_changed)
        if not FuncID.compare_func_id(baseFS.func_id, buggyFS.func_id):
            return
        if is_before_changed or is_after_changed or is_return_changed or is_code_changed:
            print(diff)
            if baseFS.func_id.to_str() not in self.count:
                self.count[baseFS.func_id.to_str()] = 1
            else:
                self.count[baseFS.func_id.to_str()] += 1
            print(baseFS.func_id.to_str())

        for i in range(min(len(baseFS.callee), len(buggyFS.callee))):
            self.compare_func_stack(base_index + [i], buggy_index + [i])


c = Comparator("/black-19-base.json", "/black-19-buggy.json")
c.compare()
