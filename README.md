[![CircleCI](https://circleci.com/gh/aeftimia/tlang/tree/main.svg?style=svg)]

# Introduction

Tlang is a DSL designed to quickly build readable and maintainable transpilers.
Experimentation is appreciated.

Tlang is designed to have have an easy learning curve and the minimal
functionality necessary to be able to parse and transpile just about anything
with minimal boilerplate and acceptable speed.

Here's an example of a script that will
change ``lambda`` s to ``def`` s (multiple args, no keyward arguments, no
escaping newlines) while formatting whitespace.

```python
import tlang

whitespace = tlang.Greedy(tlang.Terminal(" "))
trim_whitespace = whitespace.T(" ")
delete_whitespace = whitespace.T("")
variable = tlang.letter + (tlang.alphanum | "_")[:]
definition = variable.ref("name") + whitespace + "=" + whitespace
args = tlang.delimeted(variable, delete_whitespace + "," + trim_whitespace)
definition += "lambda" + whitespace + args.ref("args")
content = tlang.Terminal("\n").inv()[1:]
definition += whitespace + ":" + whitespace + content.ref("content")
definition *= tlang.Template("def {name}({args}):\n  return {content}")
print(list(definition.run("add  =   lambda   x ,  y :     x + y")))
```
