import tlang
import sys

sys.path.append(".")
import sqlite  # noqa: E402

print("imported")
alias = sqlite.K_AS / tlang.null + sqlite.table_alias
new = sqlite.table_or_subquery.replace({alias: alias.T("")})
transpiler = sqlite.parse.replace({sqlite.table_or_subquery: new})
res = list(transpiler.run("select * from table as t;"))
print(res)
assert res == ["select * from table;"]
