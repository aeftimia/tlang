# Transpile yacc sql spec into tlang
# Also serves as stress test
import os
import tlang

from immutables import Map


@tlang.transpiler(["", "declared", "undeclared"])
def reference(context):
    tokens, context = context[""], context.set("", "")
    if tokens in context.get("declared", Map()):
        yield tokens, context
    else:
        context = tlang.set_scoped(context, ("undeclared", tokens), None)
        yield f'tlang.Placeholder("{tokens}")', context


@tlang.contextonly(["declared", "name"])
def declare(context):
    yield tlang.set_scoped(context, ("declared", context["name"]), None)


@tlang.contextonly(["declared"])
def create_lookup(context):
    lookup = ""
    for name in context["declared"]:
        lookup += f'    "{name}": {name},\n'
    yield context.set("lookup", lookup)


newline = tlang.Terminal("\n")
not_newline = newline.inv()
# performant greedy


def pgreedy(t):
    return tlang.Greedy(tlang.decache(t))


var_name = not_newline + pgreedy(not_newline)
build_python_name = tlang.digit.T("var_{}") / tlang.null + pgreedy(
    tlang.alphanum / tlang.wild.T("_")
)
python_from_token = var_name.ref("terminal string") * build_python_name
python_from_token = python_from_token.ref("name")
token_assignment = "%token " + python_from_token
token_assignment *= tlang.Template(
    '{name} = tlang.Terminal("""{terminal string}""") + whitespaces'
)
token_assignment += declare
whitespace = tlang.Terminal("\n") / " " / "\t" / "\r" / "\f"
whitespaces = pgreedy(whitespace)
remove_whitespaces = whitespaces.T("")
quote = tlang.Terminal("'")
quoted = quote + pgreedy((tlang.Terminal("\\") + quote) / quote.inv()) + quote
quoted = quoted.T("tlang.Terminal({}) + whitespaces")
start_comment = tlang.Terminal("/*")
end_comment = tlang.Terminal("*/")
single_line_comment = start_comment
content = pgreedy((newline / end_comment).inv())


@tlang.contextfree
def strip(tokens):
    yield tokens.strip(), ""


content *= strip
content = content.ref("slc")
single_line_comment += content
single_line_comment += end_comment
single_line_comment *= tlang.Template("# {slc}\n")
multi_line_comment = start_comment
multi_line_comment += pgreedy(end_comment.inv())
multi_line_comment += end_comment
comment = single_line_comment / multi_line_comment.T("")
comment = remove_whitespaces + comment + remove_whitespaces
varchar = tlang.alphanum / "_" / "-" / "."
rule_name = varchar + pgreedy(varchar)
rule_name *= build_python_name
referenced = rule_name * reference
rule_or_token = referenced / quoted / single_line_comment.T("tlang.null")
concatenation = tlang.delimeted(rule_or_token, whitespaces.T(" + "))
pipe = tlang.Terminal("|").T(" | ") + remove_whitespaces
alteration = tlang.delimeted(concatenation, remove_whitespaces + pipe)
rule_assignment = (
    rule_name.ref("name") + remove_whitespaces + tlang.Terminal(":").T(" = ")
)
rule_assignment += (
    (whitespaces.T("tlang.null") + pipe) / remove_whitespaces
    + alteration
    + (whitespaces + ";").T("")
)
rule_assignment += declare
rule_assignment_lines = tlang.delimeted(rule_assignment / comment, whitespaces.T("\n"))
token_line = comment / (token_assignment + pgreedy(newline))
token_lines = pgreedy(token_line)
start_lines = "%start"
start_lines += whitespaces
start_lines += rule_name.ref("start")
start_lines += pgreedy(tlang.Terminal("%%").inv())
end_header = tlang.Terminal("%}")
header = tlang.Terminal("%{") + pgreedy(end_header.inv()) + end_header
header_lines = pgreedy(comment) + header.T("")
body = header_lines
body += whitespaces + token_lines
body += (whitespaces + start_lines).T("")
rule_delimeter = whitespaces.T("\n") + ("%%" + whitespaces).T("")
body += rule_delimeter + rule_assignment_lines + rule_delimeter.T("")
body += create_lookup
transpiler = body.T(
    r"""import tlang

# performant greedy
def pgreedy(t):
    return tlang.Greedy(tlang.decache(t))

whitespace = tlang.Terminal('\n') / ' ' / '\t' / '\r' / '\f'
whitespaces = pgreedy(whitespace)

{{}}

lookup = {
{{lookup}}
}

transpiler = tlang.stitch(lookup)["{{start}}"]""",
    ldelim="{{",
    rdelim="}}",
)
transpiler /= body
body = header_lines

tlang.test(
    quoted,
    {
        "'this text'": ["tlang.Terminal('this text') + whitespaces"],
        "'\\''": ["tlang.Terminal('\\'') + whitespaces"],
    },
)
tlang.test(
    start_comment + pgreedy(end_comment.inv()) + end_comment,
    {"/* test */": ["/* test */"]},
)
tlang.test(
    comment, {"/* some \n comment */": [""], "/* some comment */": ["# some comment\n"]}
)
tlang.test(
    token_assignment,
    {
        "%token something here": [
            'something_here = tlang.Terminal("""something here""") + whitespaces'
        ]
    },
)
tlang.test(
    concatenation,
    {"high there": ['tlang.Placeholder("high") + tlang.Placeholder("there")']},
)
tlang.test(
    alteration,
    {
        "high there | 3jkl": [
            'tlang.Placeholder("high") + tlang.Placeholder("there") | tlang.Placeholder("var_3jkl")'
        ],
        "high there | 3jkl ']'": [
            """tlang.Placeholder("high") + tlang.Placeholder("there") | tlang.Placeholder("var_3jkl") + tlang.Terminal(']') + whitespaces"""
        ],
        "'2' | High left": [
            """tlang.Terminal('2') + whitespaces | tlang.Placeholder("High") + tlang.Placeholder("left")"""
        ],
    },
)
tlang.test(
    rule_assignment,
    {
        "high : '2' | High left  ;": [
            """high = tlang.Terminal('2') + whitespaces | tlang.Placeholder("High") + tlang.Placeholder("left")"""
        ],
        "low : '2' | /*nothing*/ | left  ;": [
            """low = tlang.Terminal('2') + whitespaces | tlang.null | tlang.Placeholder("left")"""
        ],
        """bnf_program :	bnf_statement |	bnf_program bnf_statement ;""": [
            'bnf_program = tlang.Placeholder("bnf_statement") | tlang.Placeholder("bnf_program") + tlang.Placeholder("bnf_statement")'
        ],
        """c : | t;""": ['c = tlang.null | tlang.Placeholder("t")'],
        """concatenation_operator
	:	
	|	'|'
    ;""": [
            """concatenation_operator = tlang.null | tlang.Terminal('|') + whitespaces"""
        ],
    },
)
tlang.test(
    header_lines,
    {
        """/* comments
    go here
    */
    /* more comments */
    %{
      /* more comments
      ** go here
      */
    %}""": [
            "# more comments\n"
        ]
    },
)

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "sql-92.yacc.txt"), "r") as f:
    yacc = f.read()[:-1]

out = list(transpiler.run(yacc))
assert len(out) == 1
out = out[0]
with open(os.path.join(here, "sql_92.py"), "w") as f:
    f.write(out)
