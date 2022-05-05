from immutables import Map
import tlang


def test_optional():
    a = tlang.Terminal("a") + ~tlang.Terminal("b")
    opt = ~a
    rule = opt + a
    print(list(tlang.decache(rule).run()))
    print(list(rule.run()))
    print(tlang.decache(rule))
    print(list(a.run()))
    print(list(opt.run()))
    assert list((tlang.decache(rule)).run("ab")) == ["ab"]
    assert list((rule).run("ab")) == ["ab"]


def test_named_alt():
    content = tlang.Terminal("a").ref("content")
    rule = "(" + content + ")"
    rule |= rule.T("{content}")
    assert ["(a)", "a"] == list(rule.run("(a)"))


def test_terminal():
    context = tlang.root_context.set("", "a")
    assert [("a", tlang.root_context.set("", ""))] == list(tlang.Terminal("a")(context))


def test_run():
    a = tlang.Terminal("a")
    assert ["a"] == list(a.run("a"))
    M = tlang.root_context.set("1", 2)
    assert [("a", M.set("", ""))] == list(a.run("a", context=M, return_context=True))
    assert [] == list(a.run("ab", context=M))
    assert [] == list(a.run("b", context=M))


def test_concatenation():
    assert ["ab"] == list((tlang.Terminal("a") + "b").run("ab"))


def test_alteration():
    rule = tlang.Terminal("a") | "b"
    assert ["a"] == list(rule.run("a"))
    assert ["b"] == list(rule.run("b"))
    assert [] == list(rule.run("c"))


def test_right_recursion():
    rule = tlang.Terminal("a") + (tlang.Terminal("b") | tlang.Placeholder("r"))
    rule = rule.recurrence("r")
    assert ["ab"] == list(rule.run("ab"))
    assert ["aab"] == list(rule.run("aab"))
    assert ["aaab"] == list(rule.run("aaab"))


def test_left_recursion():
    rule = tlang.Placeholder("r") + "a" | "b"
    rule = rule.recurrence("r")
    assert ["ba"] == list(rule.run("ba"))
    assert ["baa"] == list(rule.run("baa"))
    assert ["baaa"] == list(rule.run("baaa"))
    assert [] == list(rule.run("a"))
    assert [] == list(rule.run("c"))


def test_left_recursion2():
    rule = tlang.Placeholder("r") + "a" | "c" | "b"
    rule = rule.recurrence("r")
    assert ["ba"] == list(rule.run("ba"))
    assert ["baa"] == list(rule.run("baa"))
    assert ["baaa"] == list(rule.run("baaa"))
    assert [] == list(rule.run("a"))
    assert [] == list(rule.run("d"))


def test_left_recursion3():
    rule = tlang.Placeholder("r") + "a" | "b" | "c"
    rule = rule.recurrence("r")
    assert ["ba"] == list(rule.run("ba"))
    assert ["baa"] == list(rule.run("baa"))
    assert ["baaa"] == list(rule.run("baaa"))
    assert [] == list(rule.run("a"))
    assert [] == list(rule.run("d"))


def test_comp():
    rule = (tlang.Terminal("a") | "b").comp(tlang.Terminal("a"))
    assert ["a"] == list(rule.run("a"))
    assert [] == list(rule.run("b"))


def test_terminal_cat():
    aa = tlang.Terminal("a") + tlang.Terminal("a")
    assert type(aa) is tlang.Terminal
    assert aa.text == "aa"


def test_gen():
    rule = tlang.Terminal("a")[:]
    print(rule)
    language = rule.run()
    for i in range(4):
        assert next(language) == "a" * i

    rule = tlang.repetition(tlang.Terminal("a") | "b")
    language = rule.run()
    prev = [""]
    for _ in range(4):
        prev = [p + "a" for p in prev] + [p + "b" for p in prev]
        for p, e in zip(prev, language):
            assert p == e


def test_left_gen():
    rule = tlang.Placeholder("r") + "a" | "b"
    rule = rule.recurrence("r")
    language = rule.run()
    for i in range(1, 4):
        assert next(language) == "b" + "a" * i


def test_cache_key():
    lookup = Map(
        {
            "x1.parser": "a",
            "x1.cache": 1,
            "x1.updates.x2.parser": "b",
            "x1.updates.x2.cache": 2,
            "y1.parser": "a",
            "y1.cache": 10,
            "y1.updates.x2.parser": "b",
            "y1.updates.x2.cache": "3",
            "y1.updates.y2.parser": "q",
            "y1.updates.y2.cache": 8,
        }
    )
    read_context = frozenset(
        ["x1.parser", "x1.cache", "y1.updates.x2.parser", "y1.updates.x2.cache"]
    )
    test = tlang.apply_mask(lookup, read_context)
    assert test == Map(
        {
            "x1.parser": "a",
            "x1.cache": 1,
            "y1.updates.x2.parser": "b",
            "y1.updates.x2.cache": "3",
        }
    )


def test_recur():
    rule0 = tlang.Terminal("a")
    rule = rule0.recur(tlang.typed({tlang.Terminal: lambda x: x + x}))
    assert ["aa"] == list(rule.run("aa"))
    rule = rule0.recur(tlang.typed({tlang.Terminal: lambda x: x + x}))
    assert ["aa"] == list(rule.run("aa"))


def test_repeat():
    rule0 = tlang.Terminal("ab")[:]
    for i in range(10):
        assert ["ab" * i] == list(rule0.run("ab" * i))
    assert [] == list(rule0.run("c"))
    assert [] == list(rule0.run("abc"))

    rule = tlang.Terminal("ab").ref("A")[:]
    for i in range(10):
        assert ["ab" * i] == list(rule.run("ab" * i))
    assert [] == list(rule.run("c"))
    assert [] == list(rule.run("aba"))


def test_repeat_recur():
    rule0 = tlang.repetition(tlang.Terminal("ab"))
    print("original", rule0)
    for i in range(1, 10):
        assert ["ab" * i] == list(rule0.run("ab" * i))

    def transform(transpiler):
        if transpiler.text:
            return tlang.Terminal("cd")
        return transpiler

    rule = rule0.recur(tlang.typed({tlang.Terminal: transform}))
    print("new", rule)
    for i in range(1, 10):
        assert ["cd" * i] == list(rule.run("cd" * i))


def test_repeat_recur2():
    rule0 = tlang.Terminal("ab")[:]
    print("original", rule0)
    for i in range(10):
        assert ["ab" * i] == list(rule0.run("ab" * i))

    def transform(transpiler):
        if transpiler.text:
            return tlang.Terminal("cd")
        return transpiler

    f = tlang.typed({tlang.Terminal: transform})
    f.tag = "a"
    rule = rule0.recur(f)
    print("new", rule)
    for i in range(10):
        assert ["cd" * i] == list(rule.run("cd" * i))


def test_repeat_recur_identity():
    rule = tlang.repetition(tlang.Terminal("ab"))
    assert str(rule) == str(rule.recur(lambda x: x))


def test_named():
    named = tlang.Terminal("a")[1:].ref("p")
    for output, context in named(named.get_init_context().set("", "aaa")):
        assert "p" in context


def test_match():
    search = tlang.Terminal("a").ref("p")
    match = tlang.Ref("p")
    filler = tlang.Terminal("a") | "b"
    rule = search + filler[:] + match
    assert ["aba"] == list(rule.run("aba"))


def test_ambiguous_match():
    search = tlang.Terminal("a").ref("p")
    match = tlang.Ref("p").T("p")
    filler = tlang.Terminal("a") | "b"
    rule = search + filler[:] + match + filler[:]
    assert ["aap", "apa"] == list(rule.run("aaa"))


def test_context_tracking():
    named = tlang.Terminal("a").ref("p")
    assert frozenset([""]) == named.read_context

    alt = named | "b"
    assert frozenset([""]) == alt.read_context
    alt |= tlang.Ref("L")
    assert frozenset(["", "L"]) == alt.read_context
    alt = alt.reset(["L"])
    assert frozenset(["", "L"]) == alt.read_context


def test_T():
    rule = tlang.Terminal("a").T("1")
    assert ["1"] == list(rule.run("a"))


def test_typed():
    rule = tlang.Terminal("a").T("1")
    rule |= tlang.Terminal("a").T("2")
    print(rule)
    assert ["1", "2"] == list(rule.run("a"))
    assert ["1"] == list(
        rule.recur(
            tlang.typed(
                {tlang.Alteration: lambda x: tlang.PEGAlteration((x.left, x.right))}
            )
        ).run("a")
    )


def test_contextfree():
    class Test(tlang.Wrapper):
        pass

    rule = tlang.Terminal("ab").ref("A")[:]
    cf_rule = Test(rule).reset()
    init_context = rule.get_init_context().set("", "ababab")
    for (output, context), (cf_output, cf_context) in zip(
        rule(init_context), cf_rule(init_context)
    ):
        assert cf_output == output
        try:
            context = context.delete("A")
        except KeyError:
            pass
        assert cf_context == context


def test_indentation_track():
    c = "a" + (tlang.Ref("b") + "b").ref("b")
    c = tlang.Terminal("").ref("b") + c[1:]
    for i in range(2, 10):
        s = ""
        for j in range(1, i):
            s += "a" + "b" * j
        assert [s] == list(c.run(s))


def test_indentation_track2():
    @tlang.transpiler(["b"])
    def append_b(context):
        yield "", context.set("b", context.get("b", "") + "b")

    c = "a" + append_b
    c = c[1:] + tlang.Ref("b")
    for i in range(1, 10):
        s = "a" * i + "b" * i
        assert [s] == list(c.run(s))


def test_indentation_track3():
    block = tlang.Placeholder("nested")
    apply_indent = tlang.Template("\n{indent}{}")
    block *= apply_indent
    block = tlang.delimeted(block, ",", greedy=False)

    @tlang.transpiler(["indent"])
    def indent(context):
        yield "", context.set("indent", context.get("indent", "") + "  ")

    block = indent + block
    block = block.reset()
    t = "[" + block + tlang.Terminal("]")
    t |= "[]"
    print(t)
    t = t.recurrence("nested")
    s = "[[],[[]],[]]"
    assert list(t.run(s, {"indent": ""})) == ["[\n  [],\n  [\n    []],\n  []]"]
    s = "[[],[]]"
    assert list(t.run(s, {"indent": ""})) == ["[\n  [],\n  []]"]


def _find_cache(t):
    if t.cache:
        print("found")
        print(t)
        assert not t.cache
    return t


find_cache = tlang.typed({tlang.Cached: _find_cache})


def test_uncached():
    rule = tlang.decache(tlang.Terminal("a")[:].ref("A"))
    print(rule)
    rule.recur(find_cache)
    list(zip(range(10), rule.run()))
    rule.recur(find_cache)


def test_recurrence():
    rule = tlang.null | tlang.Ref("A") + tlang.Placeholder("B")
    rule = rule.recurrence("B")
    rule = (tlang.Terminal("b") | tlang.Terminal("a")).ref("A") + rule
    print(rule)
    for i in range(1, 10):
        a = "a" * i
        assert list(rule.run(a)) == [a]
        b = "b" * i
        assert list(rule.run(b)) == [b]


def test_recurrence_named_ref():
    rule = tlang.null | (tlang.Ref("A") + tlang.Placeholder("B")).ref("block")
    rule = rule.recurrence("B")
    rule = (tlang.Terminal("b") | tlang.Terminal("a")).ref("A") + rule
    print(rule)
    for i in range(1, 10):
        a = "a" * i
        assert list(rule.run(a)) == [a]
        b = "b" * i
        assert list(rule.run(b)) == [b]


def test_cache_sharing():
    rule = tlang.Terminal("a") | "b"
    rule += rule
    assert rule.left is rule.right
    rule = rule.recur(lambda x: x)
    assert rule.left is rule.right
    rule = rule + rule
    rule = rule.recur(lambda x: x)
    assert rule.left is rule.right


def test_repeat_list_comprehension():
    a = tlang.Terminal("a")[2:5:2]
    assert list(a.run("a")) == []
    assert list(a.run("aa")) == ["aa"]
    assert list(a.run("aaa")) == []
    assert list(a.run("aaaa")) == ["aaaa"]
    assert list(a.run("aaaaa")) == []


def test_tricky():
    spaces = tlang.Terminal(" ")[:]
    a = tlang.Terminal("a")
    a = a[1:]
    a += spaces
    a += a
    text = "aa a"
    for out in a(tlang.root_context.set("", text)):
        print("out", out)
    assert [text] == list(a.run(text))


def test_repeated_placeholder():
    rule = "ab" + ~tlang.repetition("c" + tlang.Placeholder("B"))
    print("original", rule)
    rule = abs(rule.recurrence("B"))
    print("rule", rule)
    for i in range(1, 10):
        a = "ab" + "cab" * i
        assert list(rule.run(a)) == [a]


def test_repeated_named_placeholder():
    rule = "a" + abs(tlang.repetition("b" | tlang.Placeholder("B")))
    rule = rule.ref("block").recurrence("B")
    print("rule", rule)
    for i in range(1, 10):
        a = "ab" * i
        assert list(rule.run(a)) == [a]
        b = a + "b" * i
        assert list(rule.run(b)) == [b]


def test_placeholder():
    subrule = "d" | "e" + tlang.Placeholder("B")
    rule = "a" + subrule
    rule |= "b" + subrule
    rule = rule.recurrence("B")
    print(rule)
    for test in ("ad", "aead", "aeaead"):
        assert [test] == list(rule.run(test))
    for test in ("bd", "bebd", "bebebd"):
        assert [test] == list(rule.run(test))


def test_double_placeholder():
    rule = "b" + tlang.Placeholder("B") | "a" + tlang.Placeholder("B") | "c"
    rule = rule.recurrence("B")
    for test in ("c", "ac", "bc", "abc", "aac", "bbc", "bac"):
        assert [test] == list(rule.run(test))


def test_terminal_equivalence():
    assert tlang.Terminal("a") == tlang.Terminal("a")


def test_stitch():
    lookup = {
        "A": tlang.Terminal("a") + ~tlang.Placeholder("B"),
        "B": tlang.Terminal("b") + ~tlang.Placeholder("A"),
    }
    rule = tlang.stitch(lookup)["A"]
    test = ""
    for i in range(10):
        test += "a"
        assert [test] == list(rule.run(test))
        test += "b"
        assert [test] == list(rule.run(test))


def test_greedy():
    rule = tlang.Greedy(tlang.Terminal("a")) + tlang.Greedy(tlang.wild).T("")
    test = "aaaaab"
    assert ["aaaaa"] == list(rule.run(test))
    test = "abaa"
    assert ["a"] == list(rule.run(test))
    test = "abbbbbbab"
    assert ["a"] == list(rule.run(test))


def test_lookahead():
    a = tlang.Terminal("a")
    rule = a | "b"
    assert list(rule.run("a")) == ["a"]
    assert list(rule.run("b")) == ["b"]
    new = -a + rule
    assert list(new.run("a")) == []
    assert list(new.run("b")) == ["b"]
    new = +a + rule
    assert list(new.run("a")) == ["a"]
    assert list(new.run("b")) == []


def test_custom():
    rule = tlang.oneof("abcd").ref("name")

    @tlang.transpiler(["name", "p"])
    def update(context):
        new = "'" + context["name"] + "'"
        try:
            new = context["p"] + ", " + new
        except KeyError:
            pass
        yield "", context.set("p", new)

    rule += update
    rule = rule[:]
    rule = rule.T("[{p}]")
    for test in ("a", "aa", "abc", "abbca", "ddadbc"):
        assert [str(list(test))] == list(rule.run(test))


def test_double_recursion():
    rule = tlang.Placeholder("r") + "a" | "(" + tlang.Placeholder("s") + ")" | "b"
    rule = rule.recurrence("r")
    s = rule + ~("+" + rule)
    s = s.recurrence("s")
    assert list(s.run("baa")) == ["baa"]
    assert list(s.run("baa+b")) == ["baa+b"]
    assert list(s.run("(ba+b)a+b")) == ["(ba+b)a+b"]


def test_equality():
    r = tlang.Terminal("r") / tlang.null + tlang.Terminal("t")
    s = tlang.Terminal("r") / tlang.null + tlang.Terminal("t")
    assert r == s
    s = tlang.Link(tlang.Terminal("r")) / tlang.null + tlang.Terminal("t")
    assert r == s
