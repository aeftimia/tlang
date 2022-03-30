###########
Introduction
###########

.. currentmodule:: tlang.core

Tlang is a DSL designed to make writing readable mainainable transpilers less
impossible. Tlang is similar in spirit to `Ohm <https://github.com/harc/ohm>`_,
however Tlang differs in its goals and implementation.

Tlang approaches building transpilers as an extension of context sensitive
parsing by allowing parsers to compose. The underlying parser is probably best
described as a scannerless context sensitive packrat parser that handles left
recursion and ambiguity. Rather than returning one parse, parsers return
generators. Alterations catch an :class:`InfiniteLoop` exception and reverse
the order of their branches accordingly. The parser essentially reduces to a
packrat parser for PEG grammars.

Tlang defines a parser as a map from a context object (in our case a `Hash
Array Mapped Trie <https://en.wikipedia.org/wiki/Hash_array_mapped_trie>`_) to
a generator of tuples containing an output string and a new context object.
Tlang currently powers its context objects using `MagicStack's immutables.Map
<https://github.com/MagicStack/immutables>`_. We hope to customize this
implementation in future releases. The input string is an entry in the context
stored under the empty string ``""``. Static analysis is used to determine the
subtrie of the context read by each parser, and only that subset is stored as a
lookup key for cached parses. Furthermore, only the output string and changes
to the context are stored under this key. This maximizes cache hits when
irrelevant aspects of the context have changed while maintaining asymptotic
performance.

Recognizing the immense variety of possible operators needed in production
environments, Tlang aims to be a minimal framework that makes it
straightforward to define new parsers and operations that integrate nicely with
its core constructs.

**********
Quickstart
**********
I get it. You don't want to read a manual about something you're not sure you
care about. I'm assuming you're interested in quickly building something that
can manipulate code in complex ways. Here's an example of a script that will
change ``lambda`` s to ``def`` s (multiple args, no keyward arguments, no
escaping newlines) while formatting whitespace.

.. exec::

    import tlang

    whitespace = tlang.Greedy(tlang.Terminal(" "))
    trim_whitespace = whitespace.compT(" ")
    delete_whitespace = whitespace.compT("")
    variable = tlang.letter + (tlang.alphanum | "_")[:]
    definition = variable.ref("name") + whitespace + "=" + whitespace
    args = tlang.delimeted(variable, delete_whitespace + "," + trim_whitespace)
    definition += "lambda" + whitespace + args.ref("args")
    content = tlang.Terminal("\n").inv()[1:]
    definition += whitespace + ":" + whitespace + content.ref("content")
    definition *= tlang.Template("def {name}({args}):\n  return {content}")
    print(list(definition.run("add  =   lambda   x ,  y :     x + y")))

**********
Terminals
**********

Transpilers created with Tlang are designed to ingest context objects and
return a generator of tuples containing output strings and new context objects.
The context object stores the input string under the ``""`` key. The input
string is generally your source code, and output strings are one or more new
versions of your code. Like writing a `BNF
<https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form>`_ spec, Tlang allows
you to specify terminals, and combine rules with alterations and
concatenations.

Let's start with a simple example.

.. exec::

    import tlang

    select = tlang.Terminal("select")
    print(list(select.run("select")))
    print(list(select.run("select * from table")))
    print(list(select.run("from table select *")))

There is a subtly however. :meth:`Transpiler.run` only returns *complete* parses that
transform the entire input string. Under the hood, ``select`` actually matches
the string ``"select"`` from the beginning of its input. :meth:`Transpiler.run`
just eliminates transforms that haven't been applied to the entire string. You
can see this by calling it.

.. exec::

    import tlang
    from immutables import Map

    select = tlang.Terminal("select")
    print(list(select(Map({"": "select"}))))
    print(list(select(Map({"": "select * from table"}))))
    print(list(select(Map({"": "from table select *"}))))

While defining input inthis way is admittedly clunky, it greatly streamlines
static analysis.  We can see the terminal "ingested" the leading ``"select"``
from any input strings that started with it. That is, it removed the matched
string from the beginning of the input, and returned it as output.  More
generally, all Tlang transpilers ingest a context object, and return a
generator of tuples containing an output string and a new context object.

**********
Combinators
**********

Like rules in a BNF spec, Tlang transpilers can be applied sequentially with
concatenations or combined as a series of alternatives with alterations.

.. exec::

    import tlang

    select = tlang.Terminal("select")
    from_stuff = tlang.Terminal(" * from table")
    statement = select + from_stuff
    print(list(statement.run("select")))
    print(list(statement.run("select * from table")))
    print(list(statement.run("from table select *")))

Concatenations combine two transpilers by exectuting them sequentially left to
right. That is, the second transpiler is applied to the new input strings
generated by the first transpiler. The output string of the second transpiler is
appended to the output of the first.

There are generally cases in which we want to combine two transpilers into a
new transpiler that returns both outputs of the originals. Since the original
transpilers return generators, this new combinator can be thought of as an "or"
statement, and just chains the generators returned by its children together.

.. exec::

    import tlang
    from immutables import Map

    select = tlang.Terminal("select")
    from_stuff = tlang.Terminal("from table")
    statement = select | from_stuff
    print(list(select(Map({"": "select"}))))
    print(list(select(Map({"": "select * from table"}))))
    print(list(select(Map({"": "from table select *"}))))

Tlang uses list comprehension syntax for repetition. The start index specifies
the minimum number of repetitions, the end index specifies the maximum number
of repetitions, and the step size specifies the same.

.. exec::

    import tlang

    a = tlang.Terminal("a")[:]
    print(list(a.run('')))
    print(list(a.run('a')))
    print(list(a.run('aaaaa')))

    a = tlang.Terminal("a")[2:5:2]
    print(list(a.run('a')))
    print(list(a.run('aa')))
    print(list(a.run('aaa')))
    print(list(a.run('aaaa')))
    print(list(a.run('aaaaa')))

.. note::
   Repetitions can be recursive or loopy, and greedy or not. All have
   advantages and disadvantages. List comprehension implements loopy non-greedy
   repetition. You can access the API for the four implementations directly at
   :class:`Repetition`, :class:`Greedy`, :func:`repetition`, :func:`greedy`.
   For maximum performance on long repetitions, apply `decache` to remove any
   caching from the parser to be repeated before creating the repetition.

Sometimes it's useful to return the first of multiple matches. As is customary,
this `PEG <https://en.wikipedia.org/wiki/Parsing_expression_grammar>`_
alteration is introduced with the division operator.

.. exec::

    import tlang
    from immutables import Map

    select = tlang.Terminal("select")
    from_stuff = tlang.Terminal("from table")
    statement = select / from_stuff
    print(list(select(Map({"": "select"}))))
    print(list(select(Map({"": "select * from table"}))))
    print(list(select(Map({"": "from table select *"}))))

At this point, you're probably wondering how Tlang is different from a parser
generator framework that returns strings instead of parse trees. Because the
output of Tlang parsers shares the same type as its input string, Tlang parsers
can be composed seamlessly. Compositions (in conjuction with lookaheads) can be
used to specify a superset of `Boolean grammars
<https://en.wikipedia.org/wiki/Boolean_grammar>`_.

.. exec::

   import tlang
   from immutables import Map

   select = tlang.Terminal("select")
   from_stuff = tlang.Terminal("from table")
   statement = select | from_stuff
   statement = statement * select
   print(list(statement(Map({"": "select"}))))
   print(list(statement(Map({"": "select * from table"}))))
   print(list(statement(Map({"": "from table select *"}))))

This composition is effectively parsing "select" or "from stuff" and then just
"select" out of that result. This is of course equivalent to just parsing
"select".

**********
Templates and References
**********

To make use of this concept for transpilation, we introduce our first context
sensitive parser: the :class:`Template`.

.. exec::

   import tlang
   from immutables import Map

   select = tlang.Terminal("select")
   from_stuff = tlang.Terminal("from table")
   statement = select | from_stuff
   statement = statement * tlang.Template("drop")
   print(list(statement(Map({"": "select"}))))
   print(list(statement(Map({"": "select * from table"}))))
   print(list(statement(Map({"": "from table select *"}))))
   print(list(statement(Map({"": "from table select *"}))))

Templates can be thought of as string formatting. In this case, the template
will ingest anything and return ``drop``. This behavior can be useful for
trimming or removing whitespace. However, Templates become very powerful when
combined with references.

.. exec::

   import tlang

   select = tlang.Terminal("select")
   from_stuff = tlang.Terminal("from table")
   statement = (select | from_stuff).ref('match')
   statement = statement * tlang.Template("don't {match}")
   print(list(statement.run("select")))
   print(list(statement.run("from table")))
   print(list(statement.run("from table select *")))

References store the output string of the parse under a specified key within
the context. Templates can make use of those entries for string formatting.
Let's take a look.

.. exec::

   import tlang

   select = tlang.Terminal("select")
   from_stuff = tlang.Terminal("from table")
   statement = (select | from_stuff).ref('match')
   statement *= tlang.Template("don't {match}")
   print(list(statement.run("select", return_context=True)))

Note that Templates will return no parses (but not raise an exception) when a
nonexistant key is referenced from the context.

.. exec::

   import tlang

   select = tlang.Terminal("select").ref('nested')
   from_stuff = tlang.Terminal("from table")
   statement = (select | from_stuff).ref('match')
   print(list(statement.compT("don't {match}").run("from table")))
   print(list(statement.compT("{} don't {match.nested}").run("from table")))
   print(list(statement.compT("don't {nonexistent}").run("from table")))

Composition with Templates is common enough we included :meth:`Transpiler.compT`
as a shortcut. Note that empty delimiters denote the text passed to the
template since the context key for the input string is an empty string.

You can parse exact matches of the results of previous parses with :class:`Ref`.

.. exec::

   import tlang

   variable = tlang.Terminal("x") | tlang.Terminal("y")
   x = variable.ref('v1')
   y = variable.ref('v2')
   perfect_square = x + '^2 + ' + y + '^2 + 2' + tlang.Ref('v1') + tlang.Ref('v2')
   factor = perfect_square.compT('({v1} + {v2})^2')
   print(list(factor.run("x^2 + y^2 + 2xy")))
   print(list(factor.run("y^2 + x^2 + 2yx")))
   print(list(factor.run("y^2 + x^2 + 2xx")))


**********
Recursion
**********

BNF handles self reference nicely because it's a spec that doesn't inherently
need to compile. However, like most langauges, Python requires variables be
declared before they are referenced. This makes creating self-referencing
transpilers less straightfoward.

For example, let's say I want a json spec. Json can be embedded in json. So how
do we define json without defining json? Tlang starts with a placeholder and
introduces the self reference later.

.. exec::

    import tlang

    quote = tlang.Terminal("\"")
    string = quote + (-quote + tlang.wild)[:] + quote
    integer = tlang.digit[1:]
    # doesn"t start with 0 unless is 0
    integer = (-tlang.Terminal("0") + integer) / "0"
    value = integer | string | tlang.Placeholder("json")
    whitespace = tlang.Terminal(" ")[:]
    trim_whitespace = whitespace.compT(" ")
    delete_whitespace = whitespace.compT("")
    key_value = string + delete_whitespace + ":" + trim_whitespace + value
    array = tlang.delimeted(key_value, delete_whitespace + "," + trim_whitespace)
    mapping = "{" + delete_whitespace + array + delete_whitespace + "}"
    mapping = tlang.delimeted(key_value, delete_whitespace + "," + trim_whitespace)
    mapping = "{" + delete_whitespace + mapping + delete_whitespace + "}"
    fmt_json = array | mapping
    # fill placeholder with self reference
    fmt_json = fmt_json.recurrence("json")
    print(list(fmt_json.run('{ "key"   : ["value" , 3,  {"two : 2 } ]  }')))


**********
Macros
**********

Sometimes you have a perfectly good transpiler for one task that's *almost*
perfect for another task. For example, say you built something that traspiles
some dialect of SQL. Now you're working on something that transpiles a slightly
different dialect. You probably have a lot of lines that are just fine with one
or two rules that need to be changed to something else.  You could write a
function or class that can return a transpiler for either option, but do you
really want to refactor that function every time you come up with a slightly
different use case? Tlang transpilers come with a :meth:`Transpiler.recur`
method for this scenario. :meth:`Transpiler.recur` will recursively apply a
function to each component of your transpiler, building a modified copy from
the ground up.

.. exec::

    import tlang

    quote = tlang.Terminal('"')
    string = quote + (-quote + tlang.wild)[:] + quote
    integer = tlang.digit[1:]
    # doesn't start with 0 unless is 0
    integer = (-tlang.Terminal('0') + integer) / '0'
    value = integer | string | tlang.Placeholder('json')
    whitespace = tlang.Terminal(' ')[:]
    trim_whitespace = whitespace.compT(' ')
    delete_whitespace = whitespace.compT('')
    def comma_sep(entry):
        entry += delete_whitespace
        return delete_whitespace + entry + (',' + trim_whitespace + entry)[:]
    array = '[' + comma_sep(value) + ']'
    key_value = string + delete_whitespace + ':' + trim_whitespace + value
    mapping = '{' + comma_sep(key_value) + '}'
    fmt_json = array | mapping
    # fill placeholder with self reference
    fmt_json = fmt_json.recurrence('json')
    def swap_brackets(t):
        if t.text == '[':
            return tlang.Terminal('(')
        if t.text == ']':
            return tlang.Terminal(')')
        return t
    fmt_not_quite_json = fmt_json.recur(tlang.typed({tlang.Terminal: swap_brackets}))
    print(list(fmt_json.run('{"key": ["value" , 3,  2]  }')))
    print(list(fmt_json.run('{"key": ("value" , 3,  2)  }')))

    print(list(fmt_not_quite_json.run('{"key": ["value" , 3,  2]  }')))
    print(list(fmt_not_quite_json.run('{"key": ("value" , 3,  2)  }')))

Tlang also provides a :func:`typed` convenience method for generating single
dispatch functions. As another example, consider swapping concatenations for
alterations.

.. exec::

    import tlang

    rule1 = tlang.Terminal('a') | 'b'
    rule2 = tlang.Terminal('c') | 'd'
    rule3 = rule1 + rule2

    rule4 = rule3.recur(tlang.typed({
        tlang.Alteration: lambda t: t.left + t.right,
        tlang.Concatenation: lambda t: t.left | t.right}))

    print(list(rule3.run('ac')))
    print(list(rule3.run('bc')))
    print(list(rule3.run('ad')))
    print(list(rule3.run('bd')))

    print(list(rule3.run('ab')))
    print(list(rule3.run('cd')))

    print(list(rule4.run('ac')))
    print(list(rule4.run('bc')))
    print(list(rule4.run('ad')))
    print(list(rule4.run('bd')))

    print(list(rule4.run('ab')))
    print(list(rule4.run('cd')))

**********
Static Analysis
**********

Under the hood, transpilers work similar to packrat parser generators. There
are of course more Tlang transpiler primitives than in most implementations of
packrat parser generators, and Tlang's parsers can be context sensitive as well.
In practice, this means some piece of the context is cached as well as the
input text. However, you may notice that for every transpiler but :class:`Lazy`
one can deduce what information the transpiler needs to read and write to
without running it on any inputs. This sort of static analysis is handled under
the hood within Tlang. Every transpiler has a ``read_context`` attribute. These
are or behave like ``frozenset`` s.

.. exec::

    import tlang

    rule = tlang.Template('{name1} {name3}')
    print(rule.read_context)


Why? Under the hood, transpilers that are not guaranteed to be O(1) runtime
(e.g. :class:`Combinator` instances) will attempt to cache their operations.
These transpilers use their read_context in conjunction with the context it
receives to derive a key for its own cache. They likewise derive the piece of
output context stored within the cache from the write_context. This is
respectively merged with the true input context upon cache lookups to simulate
a true execution.

Combinators (like alterations, concatenations, and compositions) effectively
union child ``read_context`` attributes since caching them needs to cover all
possibilities of their child parsers.

:class:`Anything` is a class that implements just enough ``frozenset`` methods
to act like it stores everything. Kind of like ``nan`` in floating point
arithmetic.

Cache Sharing
============

If you create two instances of the same transpiler, they'll have their own
caches. That may be fine if they never end up seeing the same inputs, but
would otherwise lead to caching the same process separately within each
transpiler. So double the memory, and double the execution time to get
complete caching. Addressing this automatically is nontrivial. While it is
straightforward to catch the same transpiler type being initialized with the
same arguments, it's less straightforward to catch ad hoc scenarios. For
example, you need to account for associativity of concatenations and
commutativity of alterations. If that was *all* there was to it, we'd have you
covered. But once you start iterating over de Morgan's laws to switch between
``a | (b + c)`` and ``(a | b) + (a | c)``,  you have to start asking *which*
caches you want to share. There may be multiple options if ``b + c`` and
``a | b`` both exist elsewhere in isolation! We do hope to build out a series
of optimization passes for this kind of thing using :class:`Transpiler.recur`
in the future, but for now we consider it premature optimization for the
project roadmap.

In the mean time, reusing variables goes a long way to overcome this issue and
speed up the resulting transpiler. Also it tends to makes your code more
readable anyway!

**********
Creating Custom One-Offs
**********

There were two directions Tlang take from here. Either we try to anticipate
every circumstance and keep creating new ``Transpiler`` classes for them, or we
make it as simple as possible to build your own transpilers for one-off
scenarios. After a bit of eating our own dog food, Tlang switched to the latter.

A common scenario is tracking declared variables. There seem to be too many
variations of this task to maintain a one-size-fits-all transpiler class for
them. While you may end up with multiple such scenarios that fit neatly under
one class, you probably are going to have a parser that adds declared variables
to a registry, maybe another that tests whether a variable name is listed in
different registries, etc. If you're not a religious follower of OO doctrine,
you probably just want to reduce boilerplate without sacrificing readability.
Enter the following decorators.

.. topic:: One off decorators

    * :func:`transpiler()` for general transpilers
    * :func:`contextonly()` for transpilers that output the empty string
    * :func:`contextfree` for transpilers that only read the input string

You can use :func:`transpiler()` for anything you can use :func:`contextonly()`
and :func:`contextfree()` for, but the latter make their respective use cases
more readable. The first two take an iterable of keys the that your transpiler
will read from the context. They default to defining a transpiler that only
reads the input string.

**********
Generative Mode
**********

A side effect of Tlang's structure is being able to enumerate instances of the
language it generates with little modification. This feature was included for
debugging, educational purposes, and the potential to build training synthetic
training data to train ML based approaches to code transformation. To enumerate
all possible outputs of a transpiler, just call the :meth:`Transpiler.run` method with no
arguments, or equivalently, pass ``None`` as the input string.

.. exec::

    import tlang

    rule1 = tlang.Terminal('a') | 'b'
    rule2 = tlang.Terminal('c') | 'd'
    rule3 = rule1 + rule2
    print(list(rule3.run()))
