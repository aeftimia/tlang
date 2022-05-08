# Transpile antlr4 spec into tlang
import os
import tlang

from immutables import Map


@tlang.transpiler(["", "declared"])
def reference(context):
    tokens, context = context[""], context.set("", "")
    if tokens in context.get("declared", Map()):
        yield tokens, context
    else:
        yield f'tlang.Placeholder("{tokens}")', context


@tlang.contextonly(["declared", "non-fragments", "name"])
def declare(context):
    tokens = context["name"]
    if not context["fragment"]:
        context = tlang.set_scoped(context, ("non-fragments", tokens), None)
    yield tlang.set_scoped(context, ("declared", tokens), None)


@tlang.contextonly(["declared"])
def create_lookup(context):
    lookup = ",\n    ".join(
        f'"{name}": skip + {name}'
        if name in context["non-fragments"]
        else f'"{name}": {name}'
        for name in context["declared"]
    )
    yield context.set("lookup", lookup)


@tlang.contextfree
def strip(tokens):
    yield tokens.strip(), ""


newline = tlang.Terminal("\n")
not_newline = newline.inv()
not_newlines = tlang.pgreedy(not_newline)

whitespace = tlang.Terminal("\n") / " " / "\t" / "\r" / "\f"
whitespaces = tlang.pgreedy(whitespace)
remove_whitespaces = whitespaces.T("")
quote = tlang.Terminal("'")
escape = tlang.Terminal("\\")
quoted = quote + tlang.pgreedy((escape + quote) / quote.inv()) + quote
quoted = quoted.T("tlang.Terminal({})")
start_comment = tlang.Terminal("/*")
end_comment = tlang.Terminal("*/")
single_line_comment = "//" + not_newlines.ref("content")
multi_line_comment = (
    start_comment + tlang.pgreedy(end_comment.inv()).ref("content") + end_comment
)
comment = single_line_comment / multi_line_comment
comment *= tlang.Template("{content}")
comment *= strip
format_comment_line = not_newlines * strip * tlang.Template("# {}")
comment *= tlang.delimeted(format_comment_line, newline)
maybe_comments = tlang.pgreedy(comment / whitespace)


@tlang.contextfree
def fmt_char_range(chrs):
    c1, _, c2 = chrs
    yield f"tlang.oneof((\"{''.join(map(chr, range(ord(c1), ord(c2)+1)))}\"))", ""


alpha = tlang.letter / "_"
rule_name = alpha + tlang.pgreedy(alpha / tlang.digit)
referenced = rule_name * reference
grouped = "(" + whitespaces + tlang.Placeholder("alteration") + whitespaces + ")"
charrange = tlang.letter + "-" + tlang.letter
digitrange = tlang.digit + "-" + tlang.digit
bracket = tlang.Terminal("]")


def to_alteration(rule):
    return rule + tlang.pgreedy(rule.T(" / {}"))


escape_seq = escape + bracket | r"\r" | r"\n" | r"\t"
hexcode = tlang.digit | tlang.oneof("ABCDEF")
unicode = r"\u" + hexcode + hexcode + hexcode + hexcode
escape_seq /= unicode
characters = (escape_seq / bracket.inv()).T('tlang.Terminal("{}")')
somerange = charrange / digitrange
somerange *= fmt_char_range
charset = "[" + to_alteration(somerange / characters).ref("rule") + bracket
charset *= tlang.Template("{rule}")
term = quoted / grouped / referenced
term /= tlang.Terminal(".").T("tlang.wild")
term /= charset
ph = tlang.Placeholder("term").ref("term")
optional = (ph + tlang.Terminal("?")).T("{term} / tlang.null")
star = (ph + tlang.Terminal("*")).T("tlang.pgreedy({term})")
plus = (ph + tlang.Terminal("+")).T("({term} + tlang.pgreedy({term}))")
suffixed = optional | star | plus
term = suffixed | term
term = term.recurrence("term")
prefixed = ("~" + term).T("{term}.inv()")
term = prefixed / term
sep = +tlang.wild + maybe_comments.T(" + ")
concatenation = tlang.delimeted(term, sep, cache=True)
concatenation = (term + sep + concatenation).T("({})") / concatenation
pipe = maybe_comments + tlang.Terminal("|") + maybe_comments
pipe = pipe.T(" / ")
alteration = tlang.delimeted(concatenation, pipe, cache=True)
alteration = alteration.recurrence("alteration")
curly = tlang.Terminal("}")
code = "{" + tlang.pgreedy(curly.inv()) + curly


@tlang.contextonly(["hidden"])
def skip_rules(context):
    if "hidden" in context:
        yield context.set("skip_rules", " / ".join(context["hidden"]))
    else:
        yield context.set("skip_rules", "tlang.nope")


@tlang.contextonly(["name", "hidden"])
def hide(context):
    context = tlang.set_scoped(context, ("hidden", context["name"]), None)
    yield context


hidden = tlang.Terminal("channel(HIDDEN)") / "skip" + hide
channel = ("channel(" + rule_name + ")") / "skip"
channel *= hidden / tlang.identity
action = "->" + maybe_comments + channel
action /= code
semi = tlang.Terminal(";").T("")


def flag_fragment(flag):
    @tlang.contextonly()
    def set_fragment(context):
        yield context.set("fragment", flag)

    return set_fragment


rule_assignment = (
    (
        ("fragment " + maybe_comments + flag_fragment(True))
        / (tlang.null + flag_fragment(False))
    )
    + rule_name.ref("name")
    + maybe_comments
    + tlang.Terminal(":")
    + maybe_comments
    + alteration.ref("def")
    + maybe_comments
    + action / tlang.null
    + maybe_comments
    + semi
).T("{name} = {def}") + declare
rule_assignments = tlang.delimeted(
    rule_assignment, +tlang.wild + maybe_comments, cache=True
)
header = "grammar" + whitespace + whitespaces + rule_name + whitespaces + semi
body = maybe_comments + header.T("")
body += maybe_comments + rule_assignments / tlang.null
body += maybe_comments
body += skip_rules + create_lookup
template = r"""import tlang
import sys
sys.setrecursionlimit(5000)

{{}}

@tlang.contextfree
def EOF(text):
    if text == "":
        yield "", text

skip = tlang.pgreedy({{skip_rules}})

lookup = {
    {{lookup}},
    "EOF": EOF
}
lookup["UNEXPECTED_CHAR"] = tlang.nope

globals().update(tlang.stitch(lookup))
assert list(parse.run("select * from schema.table;")) == [
    "select * from schema.table;"
]
"""

transpiler = body.T(
    template,
    ldelim="{{",
    rdelim="}}",
)

transpiler /= body

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "SQLite.g4"), "r") as f:
    antlr = f.read()[:-1]

out = list(transpiler.run(antlr))
assert len(out) == 1
with open(os.path.join(here, "sqlite.py"), "w") as f:
    f.write(out[0])
