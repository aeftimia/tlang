import string as _string

from itertools import starmap as _starmap
from collections import deque as _deque
from immutables import Map as _Map
from functools import lru_cache as _lru_cache, singledispatch as _singledispatch


class CachedParse:
    def __init__(self, generator, initial_context):
        self.generator = iter(generator)
        self.initial_context = initial_context
        self.cache = []

    def run(self, context, cache_only=False):
        for output, modifications in self.cache:
            yield output, merge(context, modifications)
        if cache_only:
            return
        i = len(self.cache)
        for parse in self.generator:
            output, context = parse
            cache_entry = (output, diff(context, self.initial_context))
            self.cache.append(cache_entry)
            i += 1
            yield parse
        for output, modifications in self.cache[i:]:
            yield output, merge(context, modifications)


class HashDict(dict):
    def __hash__(self):
        return id(self)


def diff(new, initial):
    """Record updates and deletions between initial and new maps

    Args:
        new (HAMT): Map object
        initial (HAMT): Map object
    Returns:
        tuple: insertions (HAMT) and keys deleted (frozenset)"""
    deleted = frozenset(initial.keys()) - frozenset(new.keys())
    for key, value in new.items():
        try:
            eq = value == initial[key]
        except KeyError:
            continue
        if eq:
            new = new.delete(key)
    return new, deleted


def merge(context, modifications):
    """Merge updates and deletions between initial and new maps

    Args:
        context (HAMT): Map object
        modifications (tuple): insertions and keys deleted
    Returns:
        HAMT: context with specified insertions (HAMT) and deletions (frozenset)"""
    additions, deletions = modifications
    for deletion in deletions:
        context = context.delete(deletion)
    return context.update(additions)


def apply_mask(context, mask):
    """Apply mask."""
    keys = frozenset(context.keys())
    for key in keys - mask:
        context = context.delete(key)
    return context


def set_scoped(context, keys, value):
    """Create or modify an entry of nested HAMTs.

    Args:
        context: HAMT
        keys: iterable of nested keys
        value: leaf value to set at context[key[0]][key[1]]...

    Returns:
        HAMT"""
    head, *tail = keys
    if not tail:
        return context.set(head, value)
    node = context.get(head, root_context)
    return context.set(head, set_scoped(node, tail, value))


def get_scoped(context, keys):
    """Retrieve an entry from a nested HAMT.

    Args:
        context: HAMT
        keys: iterable of nested keys

    Returns:
        HAMT"""
    for key in keys:
        context = context[key]
    return context


class Anything:

    """Behaves like a context object that contains everything. Use as leaf node
    for masks."""

    __slots__ = ()

    def __repr__(self):
        return "Anything"

    def __or__(self, other):
        return self

    def __and__(self, other):
        return other

    def __rand__(self, other):
        return other


anything = Anything()
root_context = _Map()


class Transpiler:
    def __init__(self, *args, **kwargs):
        self.read_context = frozenset([""])
        self.kwargs = kwargs
        self.args = list(args)
        self.init_context = root_context

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return self.args == other.args and self.kwargs == other.kwargs

    @classmethod
    def new(cls, *args, **kwargs):
        """Like ``__new__`` but doesn't trigger ``__init__``.  Useful for
        bailing out of creating new instances when it wouldn't make sense to do
        so."""
        return cls(*args, **kwargs)

    def reset(self, write_context=frozenset([""])):
        write_context = frozenset(write_context)
        return Reset(self, write_context)

    def __hash__(self):
        return id(self)

    def copy(self, *new_args, **new_kwargs):
        """Recreat this object using the args and kwargs that generated it.

        Args:
            *new_args: New arguments with which to update the ones originally
                used to create this object.
            **new_kwargs: New keyword arguments with which to update the ones
                originally used to create this object.

        Returns:
            Copy of self with specified alterations"""
        args = new_args + tuple(self.args[len(new_args) :])  # noqa: E203
        kwargs = self.kwargs.copy()
        kwargs.update(new_kwargs)
        new = self.new(*args, **kwargs)
        new.init_context = self.init_context
        return new

    def set_init_context(self, init_context):
        """Override to change context object used for ``run``

        Args:
            init_context (dict-like): default context"""
        self.init_context = _Map(init_context)

    def get_init_context(self):
        return self.init_context

    def ref(self, name):
        return Named(self, name)

    def process(self, context):
        """Transpile input without caching

        Args:
            key: tuple with input string as first argument and input context as
            second arugment.

        Returns:
            Generator of tuples of the form (output string, (remaining input
            string, output context))
        """
        print(self)
        raise NotImplementedError

    def gen(self, context):
        return self.process(context)

    def run(self, text=None, context=None, return_context=False):
        """Transpile text, returning only output strings (optionally with final
            context) of complete parses.


        Args:
            text (string or None): input sting
            context: Context object or None for default context object of instance
            return_context (bool): Return final context in addition to ouput strings.

        Returns:
            Generator of output strings of complete parses. If
            ``return_context=True`` then generate tuples with output string and
            final context."""
        if context is None:
            context = self.get_init_context()
        else:
            context = _Map(context)
        context = context.set("", text)
        parses = self(context)
        if text is None:
            new = parses
        else:
            new = ((output, context) for output, context in parses if context[""] == "")
        if return_context:
            return new
        return (s for s, c in new)

    def complete(self):
        """Return only complete parses. Useful for composing otherwise
        independent transformations without passing incomplete transformations
        through."""
        return Completed(self)

    def __repr__(self):
        args = ", ".join(map(repr, self.args))
        kwargs = ", ".join(f"{key}={repr(value)}" for key, value in self.kwargs.items())
        if kwargs:
            args += ", " + kwargs
        return f"{self.__class__.__name__}({args})"

    def __call__(self, context):
        if context[""] is None:
            return self.gen(context)
        return self.process(context)

    def comp(self, other):
        """Feed output of this transpiler into input of another transpiler.
        Remember incomplete parses are fed through too!"""
        return Composed((self, other))

    def T(self, other, ldelim="{", rdelim="}", output="__output__"):
        """Construct a ``Template`` and compose this parser with it."""
        return Composed(
            (self, Template(other, ldelim=ldelim, rdelim=rdelim, output=""))
        )

    def inv(self):
        """Negative lookahead plus wildcard character"""
        return -self + wild

    def __or__(self, other):
        """Alteration"""
        if isinstance(other, str):
            other = Terminal(other)
        return Alteration.new((self, other))

    def __ror__(self, other):
        """Alteration"""
        if isinstance(other, str):
            other = Terminal(other)
        return Alteration.new((other, self))

    def __pos__(self):
        """Positive lookahead"""
        return --self

    def __add__(self, other):
        """Concatenation"""
        if isinstance(other, str):
            other = Terminal(other)
        return Concatenation.new((self, other))

    def __radd__(self, other):
        """Concatenation"""
        if isinstance(other, str):
            other = Terminal(other)
        return Concatenation.new((other, self))

    __mul__ = comp

    def __rmul__(self, other):
        return other.comp(self)

    def __invert__(self):
        """Optional"""
        return null | self

    def __neg__(self):
        """Negative lookahead"""
        return Not(self)

    def __truediv__(self, other):
        """PEG Alteration"""
        if isinstance(other, str):
            other = Terminal(other)
        return PEGAlteration.new((self, other))

    def __rtruediv__(self, other):
        """PEG Alteration"""
        if isinstance(other, str):
            other = Terminal(other)
        return PEGAlteration.new((other, self))

    def __getitem__(self, slice_key):
        """Repetition"""
        if slice_key.start is None:
            start_idx = 0
        else:
            start_idx = slice_key.start
        start = Concatenation.new((self,) * start_idx)
        if slice_key.step is None:
            step_idx = 1
        else:
            step_idx = slice_key.step
        step = Concatenation.new((self,) * step_idx)
        if slice_key.stop is None:
            new = Repetition(step)
            if start_idx:
                new = start + new
            return new
        else:
            new = start
            for _ in range((slice_key.stop - start_idx) // step_idx):
                new |= new + step
            return new

    def __abs__(self):
        """Only return one parse for each unique output string"""
        return Unique(self)

    def recurrence(self, identifier):
        """Create a copy and replace any ``Placeholder`` with identifier
        ``identifier`` with self reference. Return the modified copy"""
        return stitch({identifier: self})[identifier]

    def recur(self, f):
        """Build a new transpiler from the result of recursively applying a
        function to all the transpilers that comprise this one."""
        transformations = HashDict({})
        new = self._recur(f, transformations)
        update_links(transformations)
        reset(new)
        return new

    @_lru_cache(None)
    def _recur(self, f, transformations):
        """Build a new transpiler from the result of recursively applying a
        function to all the transpilers that comprise this one. Rather than
        fixing broken references, just track which transpilers the resulting
        transpilers were derived from in the dict argument. Subsequent passes
        in ``recur`` use this map to fix broken links."""

        new = f(self.copy())
        transformations[self] = new
        return new

    @_lru_cache(None)
    def visit(self, f):
        """Like recur but don't build anything new. Just apply the function to
        each transpiler that comprise this one"""
        f(self)


def stitch(lookup):
    """Stitch transpilers by reference, replacing Placeholders with Links.

    Args:
        lookup (dict): map from placeholder identifiers to parsers

    Returns:
        dict: map from placeholder identifiers to properly linked parsers"""
    link_lookup = {key: Link(value) for key, value in lookup.items()}
    transformations = HashDict({})
    # similar sequence to recur
    lookup = {
        key: value._recur(
            typed({Placeholder: lambda t: link_lookup.get(t.identifier, t)}),
            transformations,
        )
        for key, value in lookup.items()
    }
    update_links(transformations)
    # but link's parser needs to be reset
    # because of self reference
    for key, link in link_lookup.items():
        link.set_parser(lookup[key])
    # Now we can reinitialize
    for value in lookup.values():
        reset(value)
    return lookup


def update_links(transformations):
    for prev, new in transformations.items():
        if not isinstance(prev, Link):
            continue
        new.set_parser(transformations[prev.parser])


def clear_visit_cache(t):
    t.visit.cache_clear()


def reset(t):
    """Reinitialize all transpilers that comprise its argument until none of
    those transpilers' read and write contexts change."""
    inconsistent = True

    def reinit(t):
        nonlocal inconsistent
        read_context = t.read_context
        t.__init__(*t.args, **t.kwargs)
        inconsistent |= read_context != t.read_context

    while inconsistent:
        inconsistent = False
        t.visit(reinit)
        t.visit(clear_visit_cache)


def roundrobin(iterables):
    "roundrobin(('ABC', 'D', 'EF')) --> 'A' 'D' 'E' 'B' 'F' 'C'"
    iterators = _deque()
    generators = map(iter, iterables)
    while True:
        try:
            new = next(generators)
        except StopIteration:
            break
        try:
            yield next(new)
        except StopIteration:
            continue
        iterators.append(new)
    while iterators:
        try:
            while True:
                yield next(iterators[0])
                iterators.rotate(-1)
        except StopIteration:
            iterators.popleft()


def transpiler(read_context=frozenset([""])):
    """Decorator for quickly writing custom transpilers.

    Args:
        read_context (iterable): read_context of transpiler

    Returns:
        callable: Wrapper that returns a ``FromProcessor``"""
    read_context = frozenset(read_context)

    def wrapper(processor):
        return FromProcessor(processor, read_context)

    return wrapper


class FromProcessor(Transpiler):
    """Create a transpiler from a callable generator.

    Args:
        processor (generator): Callable parser taking context and returning
            tuple of output and context.
        read_context (frozenset): read_context of parser

    Returns:
        Transpiler instance"""

    def __init__(self, processor, read_context, *args, **kwargs):
        super().__init__(processor, read_context, *args, **kwargs)
        self._processor = processor
        self.read_context = read_context

    def process(self, context):
        return self._processor(context)


class Cached(Transpiler):

    """Base class for cached transpilers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}

    def __call__(self, context):
        """Parse, cache, yield, gaurd for infinite loops."""
        process = self.gen if context[""] is None else self.process
        cache_key = apply_mask(context, self.read_context)
        if cache_key not in self.cache:
            self.cache[cache_key] = CachedParse(process(context), context)
        return self.cache[cache_key].run(context)


class Template(Transpiler):

    """Template generated from concatenation of partitions (str) interleaved with the
    result of fetching caches from context using keys."""

    def __init__(self, text, *args, ldelim="{", rdelim="}", **kwargs):
        super().__init__(text, *args, ldelim=ldelim, rdelim=rdelim, **kwargs)
        if not text:
            self.partitions, self.keys = [text], []
            self.read_context = frozenset()
            return
        keys = []
        partitions = []
        left = text
        read_context = []
        while text:
            left, _, remaining = text.partition(ldelim)
            partitions.append(left)
            if not remaining:
                break
            key, _, text = remaining.partition(rdelim)
            read_context.append(key)
            keys.append(key)
        self.keys = keys
        self.partitions = partitions
        self.read_context = frozenset(read_context)

    def process(self, context):
        try:
            subs = tuple(context[key] for key in self.keys)
        except KeyError:
            return
        yield "".join(roundrobin((self.partitions, subs))), context.set("", "")


class Terminal(Transpiler):
    def __init__(self, text, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.n = len(text)
        self.text = text

    def gen(self, context):
        yield self.text, context

    def process(self, context):
        tokens = context[""]
        test = tokens[: self.n]
        if test == self.text:
            yield test, context.set("", tokens[self.n :])  # noqa: E203

    def __add__(self, other):
        if isinstance(other, str):
            other = Terminal(other)
        if isinstance(other, Terminal):
            return Terminal(self.text + other.text)
        return super().__add__(other)

    def __radd__(self, other):
        if isinstance(other, str):
            other = Terminal(other)
        if isinstance(other, Terminal):
            return Terminal(other.text + self.text)
        return super().__radd__(other)


@transpiler()
def identity(context):
    yield context[""], context.set("", "")


null = Terminal("")


class Ref(Transpiler):

    """Match the exact output of a transpiler referenced by name. Scoped
    references are specified with scopes separated by ``.``."""

    def __init__(self, key, *args, **kwargs):
        super().__init__(key, *args, **kwargs)
        self.key = key
        self.read_context |= frozenset([key])

    def process(self, context):
        try:
            cache = context[self.key]
        except KeyError:
            return ()
        return Terminal(cache)(context)


class Wrapper(Transpiler):
    def __init__(self, parser, *args, **kwargs):
        super().__init__(parser, *args, **kwargs)
        self.parser = parser
        self.read_context = parser.read_context

    def process(self, key):
        return self.parser(key)

    @_lru_cache(None)
    def _recur(self, f, transformations):
        new = f(self.copy(self.parser._recur(f, transformations)))
        transformations[self] = new
        return new

    @_lru_cache(None)
    def visit(self, f):
        self.parser.visit(f)
        f(self)


class Reset(Wrapper):
    """Surpress changes to context that effect keys outside of supplied
    ``write_context``"""

    def __init__(self, parser, write_context, *args, **kwargs):
        super().__init__(parser, write_context, *args, **kwargs)
        self.write_context = write_context

    def process(self, original_context):
        masked = apply_mask(original_context, self.write_context)
        for output, context in self.parser(original_context):
            pruned_modifications = diff(apply_mask(context, self.write_context), masked)
            yield output, merge(original_context, pruned_modifications)


class Named(Wrapper):
    """Cache the output of each parse under the specified key"""

    def __init__(self, parser, key, *args, **kwargs):
        super().__init__(parser, key, *args, **kwargs)
        self.key = key

    def process(self, context):
        for output, context in self.parser(context):
            yield output, context.set(self.key, output)


class Unique(Wrapper):
    """Discard results that share output tokens with a previous result."""

    def process(self, key):
        cache = set()
        for parse in self.parser(key):
            node, key = parse
            if node in cache:
                continue
            cache.add(node)
            yield parse


@transpiler()
def wild(context):
    """Wildcard character. Used to construct matches from positive/negative
    lookaheads."""

    try:
        tokens = context[""]
    except KeyError:
        return
    if len(tokens) < 1:
        return
    yield tokens[0], context.set("", tokens[1:])


class Not(Wrapper):
    """Negative lookahead"""

    def process(self, context):
        for _ in self.parser(context):
            return
        yield "", context


nope = -null


class Combinator(Cached):
    """Base class for combinators such as Alterations and Concatenations.
    Combinators ultimately only involve two transpilers (left and right), but
    binary trees can be built up in this manner."""

    nil = null

    @classmethod
    def new(cls, parsers, *args, **kwargs):
        if len(parsers) == 0:
            return cls.nil
        if len(parsers) == 1:
            return parsers[0]
        return cls(parsers, *args, **kwargs)

    def __init__(self, parsers, *args, **kwargs):
        super().__init__(parsers, *args, **kwargs)
        self.parsers = parsers
        if len(parsers) < 2:
            raise TypeError
        if len(parsers) == 2:
            self.left, self.right = parsers
        else:
            cls = type(self)
            if len(parsers) == 3:
                self.left = parsers[0]
                self.right = cls(parsers[1:], *args, **kwargs)
            else:
                N = len(parsers)
                L = N // 2
                self.left, self.right = cls(parsers[:L], *args, **kwargs), cls(
                    parsers[L:], *args, **kwargs
                )
        self.read_context = self.left.read_context | self.right.read_context

    @_lru_cache(None)
    def _recur(self, f, transformations):
        new = f(
            self.copy(
                (
                    self.left._recur(f, transformations),
                    self.right._recur(f, transformations),
                )
            )
        )
        transformations[self] = new
        return new

    @_lru_cache(None)
    def visit(self, f):
        self.left.visit(f)
        self.right.visit(f)
        f(self)


class Alteration(Combinator):

    nil = nope

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gaurd = set()

    def __call__(self, context):
        """Parse, cache, yield, gaurd for infinite loops."""
        cache_key = apply_mask(context, self.read_context)
        if cache_key not in self.cache:
            self.cache[cache_key] = CachedParse(self.process(context), context)
        if cache_key in self.gaurd and context[""] is not None:
            self.gaurd.discard(cache_key)
            yield from self.switch(context)
        else:
            self.gaurd.add(cache_key)
            try:
                yield from self.cache[cache_key].run(context)
            except ValueError:
                yield from self.switch(context)
            self.gaurd.discard(cache_key)

    def switch(self, context):
        yield from self.right(context)
        try:
            yield from self.left(context)
        except ValueError:
            pass

    def process(self, context):
        yield from self.left(context)
        yield from self.right(context)


class PEGAlteration(Combinator):

    nil = nope

    def gen(self, context):
        yield from self.left(context)
        yield from self.right(context)

    def process(self, context):
        found = False
        for parse in self.left(context):
            yield parse
            found = True
        if found:
            return
        yield from self.right(context)


def typed(m, default=lambda x: x):
    """Closure that applies single dispatch. Defautl

    Args:
        m (dict): hamt from classes to functions that should be applied to
            inputs of that type.
        default (callable): Function to be applied when input is not an
            instance of any keys of ``m``."""
    transform = _singledispatch(default)
    for t, f in m.items():
        transform.register(t)(f)
    return transform


class Sequential(Combinator):
    """Combinator that successively applies transpilers. This class combines
    ambiguous parses of sucessive transpilers in a breadth first manner."""

    def process(self, context):
        return roundrobin(_starmap(self.composition, self.left(context)))


class Concatenation(Sequential):
    def composition(self, output, context):
        for tail, context in self.right(context):
            yield output + tail, context


class Composed(Sequential):
    """Feeds the output of the first transpiler into the second. This output
    includes context."""

    def composition(self, output, context):
        tokens = context[""]
        for output, context in self.right(context.set("", output)):
            if not context[""]:
                yield output, context.set("", tokens)


class Completed(Wrapper):
    """Prune incomplete parses. Similar to ``run`` but as a full transpiler
    that returns the (empty) string of remaining characters as well"""

    def gen(self, context):
        return self.parser(context)

    def process(self, context):
        for parse in self.parser(context):
            output, context = parse
            if context[""] == "":
                yield parse


class Decache(Wrapper):
    @classmethod
    def new(cls, parser, *args, **kwargs):
        if isinstance(parser, Cached):
            return cls(parser, *args, **kwargs)
        return parser

    def process(self, context):
        return self.parser.process(context)


def decache(transpiler):
    """Remove any usage of caches from transpiler. Useful for stochastically
    generating elements of the transpiler's codomain"""
    return transpiler.recur(Decache.new)


class Placeholder(Transpiler):
    """Placeholder for transpiler that may not exist yet. Can be used to
    generate recursive transpilers with ``recurrence``."""

    def __init__(self, identifier, *args, **kwargs):
        super().__init__(identifier, *args, **kwargs)
        self.identifier = identifier


class Link(Wrapper):
    """Reference transpiler in a possibly recursive fashion. Analagous to a
    pointer in C or a link on a filesystem."""

    def set_parser(self, parser):
        self.parser = parser
        self.args[0] = parser

    @_lru_cache(None)
    def _recur(self, f, transformations):
        new = f(self.copy())
        transformations[self] = new
        return new

    @_lru_cache(None)
    def visit(self, f):
        f(self)

    def __repr__(self):
        return f"Link({self.parser.__class__.__name__})"


class Greedy(Wrapper, Cached):
    """Greedy repetition. Returns longest of zero or more consecutive matches.
    Non-recursive implementation. Consider decaching parser for maximum
    performance."""

    def process(self, context):
        globbed_parses = [("", context)]
        while True:
            new = []
            for output, context in globbed_parses:
                parses = self.parser(context)
                for new_output, new_context in parses:
                    new.append((output + new_output, new_context))
            if not new:
                return globbed_parses
            globbed_parses = new


class Repetition(Wrapper, Cached):
    """Returns zero or more consecutive matches. Non-recursive implementation.
    Consider decaching parser for maximum performance."""

    def process(self, context):
        globbed_parses = [("", context)]
        while True:
            new = []
            for output, context in globbed_parses:
                yield output, context
                parses = self.parser(context)
                for new_output, new_context in parses:
                    new.append((output + new_output, new_context))
            if not new:
                return
            globbed_parses = new


def repetition(parser):
    """Repetition of one or more consecutive matches. Recursive
    implementation."""
    ph = Placeholder(parser)
    new = parser + ~ph
    return new.recurrence(parser)


def greedy(parser):
    """Longest of one or more consecutive matches. Recursive implementation."""
    ph = Placeholder(parser)
    new = parser + ph / null
    return new.recurrence(parser)


def contextfree(parser):
    """Create a context free transpiler.

    Args:
        parser: Callable generator taking input string and generating tuples of
            output strings and new input strings.

    Returns:
        Transpiler"""

    @transpiler()
    def wrapper(context):
        for output, tokens in parser(context[""]):
            yield output, context.set("", tokens)

    return wrapper


def contextonly(read_context=frozenset([""])):
    """Create a transpiler that manipulates context while returning an empty
    output string.

    Args:
        parser: Callable generator taking and yielding a context object.

    Returns:
        Transpiler"""

    def wrapper(parser):
        @transpiler(read_context)
        def _(context):
            for context in parser(context):
                yield "", context

        return _

    return wrapper


def oneof(strings):
    """Match one string from a collection

    Args:
        strings (iterable): Iterable of strings

    Returns:
        PEGAlteration of supplied strings"""
    return PEGAlteration.new(tuple(map(Terminal, frozenset(strings))))


lower_case = oneof(_string.ascii_lowercase)
upper_case = oneof(_string.ascii_uppercase)
letter = lower_case / upper_case
digit = oneof(_string.digits)
alphanum = letter / digit


def within(needle, haystack, sep):
    common = (haystack + sep)[:] + haystack
    f = common + (sep + needle).T("")
    return f + ~(sep + common) | (needle + sep).T("") + common


def both_within(
    needle1, needle2, haystack, sep, template1, template2, commutative=True
):
    a = within(needle1, haystack, sep)
    b = within(needle2, haystack, sep)
    found = a + sep + b
    just_needles = needle1 + sep + needle2
    if commutative:
        found |= b + sep + a
        just_needles |= needle2 + sep + needle1
    return just_needles.T(template2) | found.T(template1)


def delimeted(transpiler, delimeter, greedy=True, cache=False):
    delimeter += transpiler
    if not cache:
        delimeter = decache(delimeter)
    if greedy:
        return transpiler + Greedy(delimeter)
    return transpiler + delimeter[:]


def test(transpiler, tests, context=None):
    """Convience function for running test cases.

    Args:
        transpiler (Transpiler): Transpiler instance to test.
        tests (dict): hamt from input string to list of expected output strings.
        context (hamt): Context to use as input. Defaults to ``None``,
            specifying the default initial context of the transpiler.

    Returns:
        ``None``"""

    for input_string, output_strings in tests.items():
        test_out = list(transpiler.run(input_string, context))
        try:
            assert test_out == output_strings
        except AssertionError:
            print("output", test_out)
            print("expected", output_strings)
            raise
