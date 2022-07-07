import tlang
import sys
import random
import jax

sys.path.append(".")


class SampledAlteration(tlang.Combinator):
    def __init__(self, parsers, model):
        super().__init__(parsers, model)
        self.model = model

    def process(self, context):
        i, context = self.model(context)
        if i:
            parsers = (self.left, self.right)
        else:
            parsers = (self.right, self.left)
        return tlang.Alteration(parsers)(context)


def resample(sampler):
    while True:
        yield next(sampler.run())


def sample(model, alterations={tlang.Alteration, tlang.PEGAlteration}):
    def alt_to_model(transpiler):
        return tlang.decache(
            transpiler.recur(
                tlang.typed(
                    {
                        alt: lambda x: SampledAlteration((x.left, x.right), model())
                        for alt in alterations
                    }
                )
            )
        )

    return alt_to_model


def make_random_model(threshold=0.25):
    def random_model(context):
        i = random.uniform(0, 1) > threshold
        return i, context

    return random_model


class IntelligentModel:
    def __init__(self):
        self.history = [set(), set()]

    def __call__(self, context):
        meta = context[self.__class__]
        states, p = self.nn(meta["state"])
        if meta["train"]:
            i = meta["target"].pop()
        else:
            i = random.uniform(0, 1) < p
        state = states[i]
        context = tlang.set_scoped(context, (self.__class__, "state"), state)
        loss = i * p + (1 - i) * (1 - p)
        loss = jax.numpy.log(loss)
        loss += tlang.get_scoped(context, (self.__class__, "loss"))
        context = tlang.set_scoped(context, (self.__class__, "loss"), loss)
        depth = tlang.get_scoped(context, (self.__class__, "depth"))
        context = tlang.set_scoped(context, (self.__class__, "depth"), depth + 1)
        return i, context


random.seed(0)

digits = "0" | "1" + tlang.greedy(tlang.oneof("01"))
expression = digits | "(" + tlang.Placeholder("expression") + ")"
expression |= expression + " * " + expression
expression |= expression + " + " + expression
expression = expression.recurrence("expression")

samples = resample(sample(make_random_model)(expression))
for _ in range(40):
    print(next(samples))
