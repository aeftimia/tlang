# Rewrite binary arithmetic expressions with Peano's axioms
import tlang

digits = tlang.oneof("01")
number = "1" + digits[:]
leading = number.ref("leading")
simple_even = leading + "0"
even = number + "0" | simple_even.compT("10 * {leading}").reset()
odd = number + "1" | (leading + "1").compT("({leading}0 + 1)").reset()
constants = "1" | even | odd  # | '0'

subexpr = "(" + tlang.Placeholder("expression").ref("content") + ")"
factor = constants | subexpr
simple_product = (factor + (" * " + factor)[:]).reset()
product = tlang.within(tlang.Terminal("1"), factor, " * ").reset()
product = simple_product
product |= simple_product.compT("{} * 1").reset()
# product |= tlang.within(tlang.Terminal('0'), factor, ' * ').compT('0')
product |= tlang.both_within(
    tlang.Terminal("10"),
    number.ref("const"),
    factor,
    " * ",
    "{const}0 * {}",
    "{const}0",
).reset()
# distributive
subbed = simple_product.compT("{common} * {}").reset()
sum_of_prod = (
    "(" + (subbed + (" + " + subbed)[:]) + ")").ref("distributed").reset()
distribute = tlang.within(factor.ref("common"), factor, " * ")
distribute *= sum_of_prod | tlang.within(sum_of_prod, factor, " * ").compT(
    "{} * {distributed}"
)
product |= distribute.reset()
simplify_sum = subexpr.compT("{content}").reset()
summand = product | simplify_sum
expression = summand + (" + " + summand)[:].reset()
# expression |= tlang.within(tlang.Terminal('0'), summand, ' + ')
# 1 + 1 = 10
expression |= tlang.both_within(
    tlang.Terminal("1"),
    tlang.Terminal("1"),
    summand,
    tlang.Terminal(" + "),
    "{} + 10",
    "10",
).reset()
expression |= tlang.both_within(
    tlang.Terminal("1"),
    simple_even.ref("even"),
    summand,
    tlang.Terminal(" + "),
    "{} + {even.leading}1",
    "{even.leading}1",
).reset()
# factor
search = tlang.within(factor.ref("match"), factor, " * ").ref("a")
match = tlang.within(tlang.Ref("match"), factor, " * ").ref("b")
factorize = tlang.both_within(
    search,
    match,
    summand,
    tlang.Terminal(" + "),
    "{} + {match} * ({a} + {b})",
    "{match} * ({a} + {b})",
    False,
)
expression |= factorize.reset()
expression = expression.reset()
expression = expression.recurrence("expression").complete()
exp = abs(expression)
simplify = exp
for i in range(2):
    simplify = abs(simplify * exp)


if __name__ == "__main__":
    print("made expression")
    for j, exp in enumerate(simplify.run("10 * 1 + 10 * 1")):
        if exp == "100":
            print("found")
            break
        assert eval(exp.replace("100", "4").replace("10", "2")) == 4, exp
        print(exp)
    print("n", j)
