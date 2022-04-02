# Transform json written as valid Python into proper json and pretty print it
import json
import tlang

space_charcter = " " | tlang.Terminal("\n")
whitespace = space_charcter[:]
delete_whitespace = whitespace.T("")

# match single or double but convert to double quotes
quote = (tlang.Terminal('"') | "'").ref("quote").T('"')
string = (
    quote + (-tlang.Ref("quote") + tlang.wild)[:] + tlang.Ref("quote").T('"')
).reset()
remove_zeros = tlang.Terminal("0")[:].T("")
nonzero = -tlang.Terminal("0") + tlang.digit
digits = tlang.digit[:]
full_decimal = (digits + nonzero) + remove_zeros | remove_zeros.T("0")
full_decimal = "." + full_decimal
# 000000.stuff
number = "0" + remove_zeros + ~full_decimal
# 0000stuff.stuff
number |= remove_zeros + nonzero + digits + ~full_decimal
# .stuff
number |= full_decimal.T("0{}")
number = ~tlang.Terminal("-") + number
number *= tlang.Terminal("-0").T("0").complete() / tlang.identity
value = tlang.Terminal("None").T("null")
value |= string | number
empty = "[" + delete_whitespace + "]"
empty |= "{" + delete_whitespace + "}"
value |= empty
value |= tlang.Placeholder("json")


@tlang.transpiler(["indent"])
def adjust_indentation(context):
    yield "", context.set("indent", context["indent"] + "    ")


def make_block(entry):
    block = delete_whitespace + entry + delete_whitespace
    block = block.T("\n{indent}{}")
    # comma separated
    block = tlang.delimeted(block, ",")
    block = adjust_indentation + block
    # reset indentation
    block = block.reset()
    return block


json_formatter = "[" + make_block(value) + \
    tlang.Terminal("]").T("\n{indent}{}")
key_value = string + delete_whitespace + ":" + whitespace.T(" ") + value
json_formatter |= "{" + make_block(key_value) + \
    tlang.Terminal("}").T("\n{indent}{}")
json_formatter = json_formatter.recurrence("json")
json_formatter |= empty
json_formatter = delete_whitespace + json_formatter + delete_whitespace
json_formatter.set_init_context({"indent": ""})

tlang.test(
    number,
    {
        "32.00": ["32.0"],
        "0003.3200": ["3.32"],
        "00.30": ["0.3"],
        "0": ["0"],
        ".0": ["0.0"],
        "0.0": ["0.0"],
        "000.3200": ["0.32"],
        "-0000": ["0"],
        "-0000.": ["-0.0"],
        "": [],
    },
)

tlang.test(
    string,
    {
        '""': ['""'],
        "'3jjk2fds  ; 3'": ['"3jjk2fds  ; 3"'],
        '"3jjk2fds  ; 3"': ['"3jjk2fds  ; 3"'],
    },
)

tlang.test(
    json_formatter,
    {
        "[[[]]]": ["[\n    [\n        []\n    ]\n]"],
        "[None]": ["[\n    null\n]"],
        "[32]": ["[\n    32\n]"],
        "[3, 22,88, 3]": ["[\n    3,\n    22,\n    88,\n    3\n]"],
        "[3, 2 ,-423, 203.0000]": ["[\n    3,\n    2,\n    -423,\n    203.0\n]"],
        "[  ]": ["""[]"""],
        "[ 32, [  ]]": ["[\n    32,\n    []\n]"],
        """{ "key1": {"value"     : [
    2, "three"]}}""": [
            '{\n    "key1": {\n        "value": [\n            2,\n'
            '            "three"\n        ]\n    }\n}'
        ],
    },
)

test_json = """

{ "key1": {"value"     : [
 2, "three",
     None
  ]
    },
"1": [3   ,-0.00,
    {"four": ""},
    -000, [{    "8"
    : 9.32, "-3": 3}], -43, .000, 00.30],
"3.0200": -02.0020
}
"""


formatted = list(json_formatter.run(test_json))
assert len(formatted) == 1
formatted = formatted[0]
print(formatted)
print(json.dumps(eval(test_json), indent=4))
assert formatted == json.dumps(eval(test_json), indent=4)
