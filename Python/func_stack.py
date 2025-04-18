class FuncID:
    def __init__(self, file_path, func_name, func_hash):
        self.file_path = file_path
        self.func_name = func_name
        self.func_hash = func_hash

    @staticmethod
    def is_Lambda(func_name: str):
        return func_name.split("@")[0] == "Lambda"

    @staticmethod
    def read(id):
        return FuncID(id['file_path'], id['func_name'], id['func_hash'])

    @staticmethod
    def compare_func_id_json(id1, id2):
        l_id = FuncID.read(id1)
        r_id = FuncID.read(id2)
        if l_id.file_path != r_id.file_path or len(l_id.func_name) != len(r_id.func_name):
            return False
        if l_id.func_hash != r_id.func_hash:
            return False
        return True

    @staticmethod
    def compare_func_id(l_id, r_id):
        if l_id.file_path.split('@')[0] != r_id.file_path.split('@')[0] or len(l_id.func_name) != len(r_id.func_name):
            return False
        return True

    def to_str(self):
        return self.file_path + "/" + self.func_name + "," + self.func_hash


class FuncStack:
    def __init__(self, func_stack):
        self.func_id = FuncID.read(func_stack['func_id']) if func_stack['func_id'] != "ENTRY_POINT" else "ENTRY_POINT"
        self.index = func_stack['index']
        self.before_args = func_stack['pre_run_args']
        self.after_args = func_stack['post_run_args']
        self.return_val = func_stack['return_val']
        self.callee = []
        for i in range(len(func_stack['callee'])):
            self.callee.append(FuncStack(func_stack['callee'][i]))

    @staticmethod
    def get_func_stack(base_func_stack, index):
        func_stack = base_func_stack
        for i in range(len(index)):
            func_stack = func_stack.callee[index[i]]
        return func_stack

    def get_depth(self):
        return len(self.index)

    def is_deepest(self):
        return len(self.callee) == 0

    def is_top(self):
        return self.func_id == "ENTRY_POINT"
