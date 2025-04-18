import json
from python_results.func_stack import FuncStack, NewFuncStack, FuncID
from openai import OpenAI
import time
client = OpenAI(api_key="")

with open('/youtube-dl-41-base.json', 'r') as f1, \
        open('/youtube-dl-41-base-src.json', 'r') as f2, \
        open('/youtube-dl-41-buggy.json', 'r') as f3, \
        open('/youtube-dl-41-buggy-src.json', 'r') as f4:
    base_func_stack_json = json.load(f1)
    base_func_src_json = json.load(f2)
    buggy_func_stack_json = json.load(f3)
    buggy_func_src_json = json.load(f4)

base_func_stack = FuncStack(base_func_stack_json)
buggy_func_stack = FuncStack(buggy_func_stack_json)
base_src_func_stack = NewFuncStack(base_func_stack, base_func_src_json)
buggy_src_func_stack = NewFuncStack(buggy_func_stack, buggy_func_src_json)


def linearize_func_stack(func_stack, linearized_func_stack):
    linearized_func_stack.append({'func_id': func_stack['func_id'],
                                  'index': func_stack['index'],
                                  'src': func_stack['src']})
    for i in range(len(func_stack['callee'])):
        linearize_func_stack(func_stack['callee'][i], linearized_func_stack)

print(time.time())
linearized_base_func_stack = []
linearized_buggy_func_stack = []
linearize_func_stack(NewFuncStack.to_json(base_src_func_stack), linearized_base_func_stack)
linearize_func_stack(NewFuncStack.to_json(buggy_src_func_stack), linearized_buggy_func_stack)

error_message_black_3 = """"""


for i in range(0, min(len(linearized_base_func_stack), len(linearized_buggy_func_stack))):
    baseFS = linearized_base_func_stack[i]
    buggyFS = linearized_buggy_func_stack[i]

    if baseFS['src'] == buggyFS['src']:
        continue
    messages = []
    print(i)

    for j in range(i - 5, i + 20):
        baseFS = linearized_base_func_stack[j]
        buggyFS = linearized_buggy_func_stack[j]
        message = {"call": [{"correct": {'func': baseFS['func_id'].split(',')[0], 'src': baseFS['src']}},
                            {"buggy": {'func': buggyFS['func_id'].split(',')[0], 'src': buggyFS['src']}}]}
        messages.append(message)

    content = f"You will be given a list of function call pairs and an error message {error_message_youtube_dl_41}" \
              f"In each pair, one is a function call for the correct version, " \
              f"another one is a function call for the buggy version. " \
              f"The list is the order of function calls. " \
              f"Based on the list and the error message, " \
              f"please tell me which function might be the cause of the regression bug.\n" \
              f"{str(messages)}\n\n" \
              f"Please be as precise as possible, and just give me the function name."

    # content = f"You will be given a list of function call pairs." \
    #           f"In each pair, one is a function call for the correct version, " \
    #           f"another one is a function call for the buggy version. " \
    #           f"The list is the order of function calls. " \
    #           f"Based on the list, " \
    #           f"please tell me which function might be the cause of the regression bug.\n" \
    #           f"{str(messages)}\n\n" \
    #           f"Please be as precise as possible, and just give me the function name."

    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": content}]
    )
    answer = completion.choices[0].message.content
    print(answer)
    print("=====================")
    print(time.time())
