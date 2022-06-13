import tlang
import sys
import random

sys.path.append(".")
import arithmetic  # noqa: E402


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
                    {alt: lambda x: SampledAlteration((x.left, x.right), model())
                     for alt in alterations})))
    return alt_to_model

def make_random_model(threshold=0.25):
    def random_model(context):
        i = random.uniform(0, 1) > threshold
        return i, context
    return random_model

random.seed(0)

digits = "0" | "1" + tlang.repetition(tlang.oneof("01"))
expression = digits | "(" + tlang.Placeholder("expression") + ")"
expression |= expression + " * " + expression
expression |= expression + " + " + expression
expression = expression.recurrence("expression")

samples = resample(sample(make_random_model)(expression))
for _ in range(40):
    print(next(samples))

