import tlang
import sys
sys.setrecursionlimit(5000)

# * The MIT License (MIT)
# *
# * Copyright (c) 2014 by Bart Kiers
# *
# * Permission is hereby granted, free of charge, to any person
# * obtaining a copy of this software and associated documentation
# * files (the "Software"), to deal in the Software without
# * restriction, including without limitation the rights to use,
# * copy, modify, merge, publish, distribute, sublicense, and/or sell
# * copies of the Software, and to permit persons to whom the
# * Software is furnished to do so, subject to the following
# * conditions:
# *
# * The above copyright notice and this permission notice shall be
# * included in all copies or substantial portions of the Software.
# *
# * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# * OTHER DEALINGS IN THE SOFTWARE.
# *
# * Project      : sqlite-parser; an ANTLR4 grammar for SQLite
# *                https://github.com/bkiers/sqlite-parser
# * Developed by : Bart Kiers, bart@big-o.nl


parse = (tlang.pgreedy(( tlang.Placeholder("sql_stmt_list") // tlang.Placeholder("error") )) + tlang.Placeholder("EOF"))

error = tlang.Placeholder("UNEXPECTED_CHAR")

sql_stmt_list = (tlang.pgreedy(tlang.Terminal(';')) + tlang.Placeholder("sql_stmt") + tlang.pgreedy(( ((tlang.Terminal(';') + tlang.pgreedy(tlang.Terminal(';'))) + tlang.Placeholder("sql_stmt")) )) + tlang.pgreedy(tlang.Terminal(';')))

sql_stmt = (( (tlang.Placeholder("K_EXPLAIN") + ( (tlang.Placeholder("K_QUERY") + tlang.Placeholder("K_PLAN")) ) / tlang.null) ) / tlang.null + ( tlang.Placeholder("alter_table_stmt") // tlang.Placeholder("analyze_stmt") // tlang.Placeholder("attach_stmt") // tlang.Placeholder("begin_stmt") // tlang.Placeholder("commit_stmt") // tlang.Placeholder("compound_select_stmt") // tlang.Placeholder("create_index_stmt") // tlang.Placeholder("create_table_stmt") // tlang.Placeholder("create_trigger_stmt") // tlang.Placeholder("create_view_stmt") // tlang.Placeholder("create_virtual_table_stmt") // tlang.Placeholder("delete_stmt") // tlang.Placeholder("delete_stmt_limited") // tlang.Placeholder("detach_stmt") // tlang.Placeholder("drop_index_stmt") // tlang.Placeholder("drop_table_stmt") // tlang.Placeholder("drop_trigger_stmt") // tlang.Placeholder("drop_view_stmt") // tlang.Placeholder("factored_select_stmt") // tlang.Placeholder("insert_stmt") // tlang.Placeholder("pragma_stmt") // tlang.Placeholder("reindex_stmt") // tlang.Placeholder("release_stmt") // tlang.Placeholder("rollback_stmt") // tlang.Placeholder("savepoint_stmt") // tlang.Placeholder("simple_select_stmt") // tlang.Placeholder("select_stmt") // tlang.Placeholder("update_stmt") // tlang.Placeholder("update_stmt_limited") // tlang.Placeholder("vacuum_stmt") ))

alter_table_stmt = (tlang.Placeholder("K_ALTER") + tlang.Placeholder("K_TABLE") + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name") + ( (tlang.Placeholder("K_RENAME") + tlang.Placeholder("K_TO") + tlang.Placeholder("new_table_name")) // (tlang.Placeholder("K_ADD") + tlang.Placeholder("K_COLUMN") / tlang.null + tlang.Placeholder("column_def"))
   ))

analyze_stmt = (tlang.Placeholder("K_ANALYZE") + ( tlang.Placeholder("database_name") // tlang.Placeholder("table_or_index_name") // (tlang.Placeholder("database_name") + tlang.Terminal('.') + tlang.Placeholder("table_or_index_name")) ) / tlang.null)

attach_stmt = (tlang.Placeholder("K_ATTACH") + tlang.Placeholder("K_DATABASE") / tlang.null + tlang.Placeholder("expr") + tlang.Placeholder("K_AS") + tlang.Placeholder("database_name"))

begin_stmt = (tlang.Placeholder("K_BEGIN") + ( tlang.Placeholder("K_DEFERRED") // tlang.Placeholder("K_IMMEDIATE") // tlang.Placeholder("K_EXCLUSIVE") ) / tlang.null + ( (tlang.Placeholder("K_TRANSACTION") + tlang.Placeholder("transaction_name") / tlang.null) ) / tlang.null)

commit_stmt = (( tlang.Placeholder("K_COMMIT") // tlang.Placeholder("K_END") ) + ( (tlang.Placeholder("K_TRANSACTION") + tlang.Placeholder("transaction_name") / tlang.null) ) / tlang.null)

compound_select_stmt = (( (tlang.Placeholder("K_WITH") + tlang.Placeholder("K_RECURSIVE") / tlang.null + tlang.Placeholder("common_table_expression") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("common_table_expression")) ))) ) / tlang.null + tlang.Placeholder("select_core") + (( (( (tlang.Placeholder("K_UNION") + tlang.Placeholder("K_ALL") / tlang.null) // tlang.Placeholder("K_INTERSECT") // tlang.Placeholder("K_EXCEPT") ) + tlang.Placeholder("select_core")) ) + tlang.pgreedy(( (( (tlang.Placeholder("K_UNION") + tlang.Placeholder("K_ALL") / tlang.null) // tlang.Placeholder("K_INTERSECT") // tlang.Placeholder("K_EXCEPT") ) + tlang.Placeholder("select_core")) ))) + ( (tlang.Placeholder("K_ORDER") + tlang.Placeholder("K_BY") + tlang.Placeholder("ordering_term") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("ordering_term")) ))) ) / tlang.null + ( (tlang.Placeholder("K_LIMIT") + tlang.Placeholder("expr") + ( (( tlang.Placeholder("K_OFFSET") // tlang.Terminal(',') ) + tlang.Placeholder("expr")) ) / tlang.null) ) / tlang.null)

create_index_stmt = (tlang.Placeholder("K_CREATE") + tlang.Placeholder("K_UNIQUE") / tlang.null + tlang.Placeholder("K_INDEX") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_NOT") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("index_name") + tlang.Placeholder("K_ON") + tlang.Placeholder("table_name") + tlang.Terminal('(') + tlang.Placeholder("indexed_column") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("indexed_column")) )) + tlang.Terminal(')') + ( (tlang.Placeholder("K_WHERE") + tlang.Placeholder("expr")) ) / tlang.null)

create_table_stmt = (tlang.Placeholder("K_CREATE") + ( tlang.Placeholder("K_TEMP") // tlang.Placeholder("K_TEMPORARY") ) / tlang.null + tlang.Placeholder("K_TABLE") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_NOT") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name") + ( (tlang.Terminal('(') + tlang.Placeholder("column_def") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_def")) )) + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("table_constraint")) )) + tlang.Terminal(')') + ( (tlang.Placeholder("K_WITHOUT") + tlang.Placeholder("IDENTIFIER")) ) / tlang.null) // (tlang.Placeholder("K_AS") + tlang.Placeholder("select_stmt")) 
   ))

create_trigger_stmt = (tlang.Placeholder("K_CREATE") + ( tlang.Placeholder("K_TEMP") // tlang.Placeholder("K_TEMPORARY") ) / tlang.null + tlang.Placeholder("K_TRIGGER") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_NOT") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("trigger_name") + ( tlang.Placeholder("K_BEFORE") // tlang.Placeholder("K_AFTER") // (tlang.Placeholder("K_INSTEAD") + tlang.Placeholder("K_OF")) ) / tlang.null + ( tlang.Placeholder("K_DELETE") // tlang.Placeholder("K_INSERT") // (tlang.Placeholder("K_UPDATE") + ( (tlang.Placeholder("K_OF") + tlang.Placeholder("column_name") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name")) ))) ) / tlang.null) ) + tlang.Placeholder("K_ON") + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name") + ( (tlang.Placeholder("K_FOR") + tlang.Placeholder("K_EACH") + tlang.Placeholder("K_ROW")) ) / tlang.null + ( (tlang.Placeholder("K_WHEN") + tlang.Placeholder("expr")) ) / tlang.null + tlang.Placeholder("K_BEGIN") + (( (( tlang.Placeholder("update_stmt") // tlang.Placeholder("insert_stmt") // tlang.Placeholder("delete_stmt") // tlang.Placeholder("select_stmt") ) + tlang.Terminal(';')) ) + tlang.pgreedy(( (( tlang.Placeholder("update_stmt") // tlang.Placeholder("insert_stmt") // tlang.Placeholder("delete_stmt") // tlang.Placeholder("select_stmt") ) + tlang.Terminal(';')) ))) + tlang.Placeholder("K_END"))

create_view_stmt = (tlang.Placeholder("K_CREATE") + ( tlang.Placeholder("K_TEMP") // tlang.Placeholder("K_TEMPORARY") ) / tlang.null + tlang.Placeholder("K_VIEW") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_NOT") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("view_name") + tlang.Placeholder("K_AS") + tlang.Placeholder("select_stmt"))

create_virtual_table_stmt = (tlang.Placeholder("K_CREATE") + tlang.Placeholder("K_VIRTUAL") + tlang.Placeholder("K_TABLE") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_NOT") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name") + tlang.Placeholder("K_USING") + tlang.Placeholder("module_name") + ( (tlang.Terminal('(') + tlang.Placeholder("module_argument") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("module_argument")) )) + tlang.Terminal(')')) ) / tlang.null)

delete_stmt = (tlang.Placeholder("with_clause") / tlang.null + tlang.Placeholder("K_DELETE") + tlang.Placeholder("K_FROM") + tlang.Placeholder("qualified_table_name") + ( (tlang.Placeholder("K_WHERE") + tlang.Placeholder("expr")) ) / tlang.null)

delete_stmt_limited = (tlang.Placeholder("with_clause") / tlang.null + tlang.Placeholder("K_DELETE") + tlang.Placeholder("K_FROM") + tlang.Placeholder("qualified_table_name") + ( (tlang.Placeholder("K_WHERE") + tlang.Placeholder("expr")) ) / tlang.null + ( (( (tlang.Placeholder("K_ORDER") + tlang.Placeholder("K_BY") + tlang.Placeholder("ordering_term") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("ordering_term")) ))) ) / tlang.null + tlang.Placeholder("K_LIMIT") + tlang.Placeholder("expr") + ( (( tlang.Placeholder("K_OFFSET") // tlang.Terminal(',') ) + tlang.Placeholder("expr")) ) / tlang.null)
   ) / tlang.null)

detach_stmt = (tlang.Placeholder("K_DETACH") + tlang.Placeholder("K_DATABASE") / tlang.null + tlang.Placeholder("database_name"))

drop_index_stmt = (tlang.Placeholder("K_DROP") + tlang.Placeholder("K_INDEX") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("index_name"))

drop_table_stmt = (tlang.Placeholder("K_DROP") + tlang.Placeholder("K_TABLE") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name"))

drop_trigger_stmt = (tlang.Placeholder("K_DROP") + tlang.Placeholder("K_TRIGGER") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("trigger_name"))

drop_view_stmt = (tlang.Placeholder("K_DROP") + tlang.Placeholder("K_VIEW") + ( (tlang.Placeholder("K_IF") + tlang.Placeholder("K_EXISTS")) ) / tlang.null + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("view_name"))

factored_select_stmt = (( (tlang.Placeholder("K_WITH") + tlang.Placeholder("K_RECURSIVE") / tlang.null + tlang.Placeholder("common_table_expression") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("common_table_expression")) ))) ) / tlang.null + tlang.Placeholder("select_core") + tlang.pgreedy(( (tlang.Placeholder("compound_operator") + tlang.Placeholder("select_core")) )) + ( (tlang.Placeholder("K_ORDER") + tlang.Placeholder("K_BY") + tlang.Placeholder("ordering_term") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("ordering_term")) ))) ) / tlang.null + ( (tlang.Placeholder("K_LIMIT") + tlang.Placeholder("expr") + ( (( tlang.Placeholder("K_OFFSET") // tlang.Terminal(',') ) + tlang.Placeholder("expr")) ) / tlang.null) ) / tlang.null)

insert_stmt = (tlang.Placeholder("with_clause") / tlang.null + ( tlang.Placeholder("K_INSERT") // tlang.Placeholder("K_REPLACE") // (tlang.Placeholder("K_INSERT") + tlang.Placeholder("K_OR") + tlang.Placeholder("K_REPLACE")) // (tlang.Placeholder("K_INSERT") + tlang.Placeholder("K_OR") + tlang.Placeholder("K_ROLLBACK")) // (tlang.Placeholder("K_INSERT") + tlang.Placeholder("K_OR") + tlang.Placeholder("K_ABORT")) // (tlang.Placeholder("K_INSERT") + tlang.Placeholder("K_OR") + tlang.Placeholder("K_FAIL")) // (tlang.Placeholder("K_INSERT") + tlang.Placeholder("K_OR") + tlang.Placeholder("K_IGNORE")) ) + tlang.Placeholder("K_INTO") + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name") + ( (tlang.Terminal('(') + tlang.Placeholder("column_name") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name")) )) + tlang.Terminal(')')) ) / tlang.null + ( (tlang.Placeholder("K_VALUES") + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )) + tlang.Terminal(')') + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )) + tlang.Terminal(')')) ))) // tlang.Placeholder("select_stmt") // (tlang.Placeholder("K_DEFAULT") + tlang.Placeholder("K_VALUES"))
   ))

pragma_stmt = (tlang.Placeholder("K_PRAGMA") + ( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("pragma_name") + ( (tlang.Terminal('=') + tlang.Placeholder("pragma_value")) // (tlang.Terminal('(') + tlang.Placeholder("pragma_value") + tlang.Terminal(')')) ) / tlang.null)

reindex_stmt = (tlang.Placeholder("K_REINDEX") + ( tlang.Placeholder("collation_name") // (( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + ( tlang.Placeholder("table_name") // tlang.Placeholder("index_name") ))
             ) / tlang.null)

release_stmt = (tlang.Placeholder("K_RELEASE") + tlang.Placeholder("K_SAVEPOINT") / tlang.null + tlang.Placeholder("savepoint_name"))

rollback_stmt = (tlang.Placeholder("K_ROLLBACK") + ( (tlang.Placeholder("K_TRANSACTION") + tlang.Placeholder("transaction_name") / tlang.null) ) / tlang.null + ( (tlang.Placeholder("K_TO") + tlang.Placeholder("K_SAVEPOINT") / tlang.null + tlang.Placeholder("savepoint_name")) ) / tlang.null)

savepoint_stmt = (tlang.Placeholder("K_SAVEPOINT") + tlang.Placeholder("savepoint_name"))

simple_select_stmt = (( (tlang.Placeholder("K_WITH") + tlang.Placeholder("K_RECURSIVE") / tlang.null + tlang.Placeholder("common_table_expression") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("common_table_expression")) ))) ) / tlang.null + tlang.Placeholder("select_core") + ( (tlang.Placeholder("K_ORDER") + tlang.Placeholder("K_BY") + tlang.Placeholder("ordering_term") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("ordering_term")) ))) ) / tlang.null + ( (tlang.Placeholder("K_LIMIT") + tlang.Placeholder("expr") + ( (( tlang.Placeholder("K_OFFSET") // tlang.Terminal(',') ) + tlang.Placeholder("expr")) ) / tlang.null) ) / tlang.null)

select_stmt = (( (tlang.Placeholder("K_WITH") + tlang.Placeholder("K_RECURSIVE") / tlang.null + tlang.Placeholder("common_table_expression") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("common_table_expression")) ))) ) / tlang.null + tlang.Placeholder("select_or_values") + tlang.pgreedy(( (tlang.Placeholder("compound_operator") + tlang.Placeholder("select_or_values")) )) + ( (tlang.Placeholder("K_ORDER") + tlang.Placeholder("K_BY") + tlang.Placeholder("ordering_term") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("ordering_term")) ))) ) / tlang.null + ( (tlang.Placeholder("K_LIMIT") + tlang.Placeholder("expr") + ( (( tlang.Placeholder("K_OFFSET") // tlang.Terminal(',') ) + tlang.Placeholder("expr")) ) / tlang.null) ) / tlang.null)

select_or_values = (tlang.Placeholder("K_SELECT") + ( tlang.Placeholder("K_DISTINCT") // tlang.Placeholder("K_ALL") ) / tlang.null + tlang.Placeholder("result_column") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("result_column")) )) + ( (tlang.Placeholder("K_FROM") + ( (tlang.Placeholder("table_or_subquery") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("table_or_subquery")) ))) // tlang.Placeholder("join_clause") )) ) / tlang.null + ( (tlang.Placeholder("K_WHERE") + tlang.Placeholder("expr")) ) / tlang.null + ( (tlang.Placeholder("K_GROUP") + tlang.Placeholder("K_BY") + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )) + ( (tlang.Placeholder("K_HAVING") + tlang.Placeholder("expr")) ) / tlang.null) ) / tlang.null) // (tlang.Placeholder("K_VALUES") + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )) + tlang.Terminal(')') + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )) + tlang.Terminal(')')) )))

update_stmt = (tlang.Placeholder("with_clause") / tlang.null + tlang.Placeholder("K_UPDATE") + ( (tlang.Placeholder("K_OR") + tlang.Placeholder("K_ROLLBACK")) // (tlang.Placeholder("K_OR") + tlang.Placeholder("K_ABORT")) // (tlang.Placeholder("K_OR") + tlang.Placeholder("K_REPLACE")) // (tlang.Placeholder("K_OR") + tlang.Placeholder("K_FAIL")) // (tlang.Placeholder("K_OR") + tlang.Placeholder("K_IGNORE")) ) / tlang.null + tlang.Placeholder("qualified_table_name") + tlang.Placeholder("K_SET") + tlang.Placeholder("column_name") + tlang.Terminal('=') + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name") + tlang.Terminal('=') + tlang.Placeholder("expr")) )) + ( (tlang.Placeholder("K_WHERE") + tlang.Placeholder("expr")) ) / tlang.null)

update_stmt_limited = (tlang.Placeholder("with_clause") / tlang.null + tlang.Placeholder("K_UPDATE") + ( (tlang.Placeholder("K_OR") + tlang.Placeholder("K_ROLLBACK")) // (tlang.Placeholder("K_OR") + tlang.Placeholder("K_ABORT")) // (tlang.Placeholder("K_OR") + tlang.Placeholder("K_REPLACE")) // (tlang.Placeholder("K_OR") + tlang.Placeholder("K_FAIL")) // (tlang.Placeholder("K_OR") + tlang.Placeholder("K_IGNORE")) ) / tlang.null + tlang.Placeholder("qualified_table_name") + tlang.Placeholder("K_SET") + tlang.Placeholder("column_name") + tlang.Terminal('=') + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name") + tlang.Terminal('=') + tlang.Placeholder("expr")) )) + ( (tlang.Placeholder("K_WHERE") + tlang.Placeholder("expr")) ) / tlang.null + ( (( (tlang.Placeholder("K_ORDER") + tlang.Placeholder("K_BY") + tlang.Placeholder("ordering_term") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("ordering_term")) ))) ) / tlang.null + tlang.Placeholder("K_LIMIT") + tlang.Placeholder("expr") + ( (( tlang.Placeholder("K_OFFSET") // tlang.Terminal(',') ) + tlang.Placeholder("expr")) ) / tlang.null) 
   ) / tlang.null)

vacuum_stmt = tlang.Placeholder("K_VACUUM")

column_def = (tlang.Placeholder("column_name") + tlang.Placeholder("type_name") / tlang.null + tlang.pgreedy(tlang.Placeholder("column_constraint")))

type_name = ((tlang.Placeholder("name") + tlang.pgreedy(tlang.Placeholder("name"))) + ( (tlang.Terminal('(') + tlang.Placeholder("signed_number") + tlang.Terminal(')')) // (tlang.Terminal('(') + tlang.Placeholder("signed_number") + tlang.Terminal(',') + tlang.Placeholder("signed_number") + tlang.Terminal(')')) ) / tlang.null)

column_constraint = (( (tlang.Placeholder("K_CONSTRAINT") + tlang.Placeholder("name")) ) / tlang.null + ( (tlang.Placeholder("K_PRIMARY") + tlang.Placeholder("K_KEY") + ( tlang.Placeholder("K_ASC") // tlang.Placeholder("K_DESC") ) / tlang.null + tlang.Placeholder("conflict_clause") + tlang.Placeholder("K_AUTOINCREMENT") / tlang.null) // (tlang.Placeholder("K_NOT") / tlang.null + tlang.Placeholder("K_NULL") + tlang.Placeholder("conflict_clause")) // (tlang.Placeholder("K_UNIQUE") + tlang.Placeholder("conflict_clause")) // (tlang.Placeholder("K_CHECK") + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.Terminal(')')) // (tlang.Placeholder("K_DEFAULT") + (tlang.Placeholder("signed_number") // tlang.Placeholder("literal_value") // (tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.Terminal(')')))) // (tlang.Placeholder("K_COLLATE") + tlang.Placeholder("collation_name")) // tlang.Placeholder("foreign_key_clause")
   ))

conflict_clause = ( (tlang.Placeholder("K_ON") + tlang.Placeholder("K_CONFLICT") + ( tlang.Placeholder("K_ROLLBACK") // tlang.Placeholder("K_ABORT") // tlang.Placeholder("K_FAIL") // tlang.Placeholder("K_IGNORE") // tlang.Placeholder("K_REPLACE")
                     ))
   ) / tlang.null

# SQLite understands the following binary operators, in order from highest to
# lowest precedence:
# 
# ||
# *    /    %
# +    -
# <<   >>   &    |
# <    <=   >    >=
# =    ==   !=   <>   IS   IS NOT   IN   LIKE   GLOB   MATCH   REGEXP
# AND
# OR
expr = tlang.Placeholder("literal_value") // tlang.Placeholder("BIND_PARAMETER") // (( (( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("column_name")) // (tlang.Placeholder("unary_operator") + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + tlang.Terminal('||') + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + ( tlang.Terminal('*') // tlang.Terminal('/') // tlang.Terminal('%') ) + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + ( tlang.Terminal('+') // tlang.Terminal('-') ) + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + ( tlang.Terminal('<<') // tlang.Terminal('>>') // tlang.Terminal('&') // tlang.Terminal('|') ) + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + ( tlang.Terminal('<') // tlang.Terminal('<=') // tlang.Terminal('>') // tlang.Terminal('>=') ) + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + ( tlang.Terminal('=') // tlang.Terminal('==') // tlang.Terminal('!=') // tlang.Terminal('<>') // tlang.Placeholder("K_IS") // (tlang.Placeholder("K_IS") + tlang.Placeholder("K_NOT")) // tlang.Placeholder("K_IN") // tlang.Placeholder("K_LIKE") // tlang.Placeholder("K_GLOB") // tlang.Placeholder("K_MATCH") // tlang.Placeholder("K_REGEXP") ) + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + tlang.Placeholder("K_AND") + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + tlang.Placeholder("K_OR") + tlang.Placeholder("expr")) // (tlang.Placeholder("function_name") + tlang.Terminal('(') + ( (tlang.Placeholder("K_DISTINCT") / tlang.null + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) ))) // tlang.Terminal('*') ) / tlang.null + tlang.Terminal(')')) // (tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.Terminal(')')) // (tlang.Placeholder("K_CAST") + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.Placeholder("K_AS") + tlang.Placeholder("type_name") + tlang.Terminal(')')) // (tlang.Placeholder("expr") + tlang.Placeholder("K_COLLATE") + tlang.Placeholder("collation_name")) // (tlang.Placeholder("expr") + tlang.Placeholder("K_NOT") / tlang.null + ( tlang.Placeholder("K_LIKE") // tlang.Placeholder("K_GLOB") // tlang.Placeholder("K_REGEXP") // tlang.Placeholder("K_MATCH") ) + tlang.Placeholder("expr") + ( (tlang.Placeholder("K_ESCAPE") + tlang.Placeholder("expr")) ) / tlang.null) // (tlang.Placeholder("expr") + ( tlang.Placeholder("K_ISNULL") // tlang.Placeholder("K_NOTNULL") // (tlang.Placeholder("K_NOT") + tlang.Placeholder("K_NULL")) )) // (tlang.Placeholder("expr") + tlang.Placeholder("K_IS") + tlang.Placeholder("K_NOT") / tlang.null + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + tlang.Placeholder("K_NOT") / tlang.null + tlang.Placeholder("K_BETWEEN") + tlang.Placeholder("expr") + tlang.Placeholder("K_AND") + tlang.Placeholder("expr")) // (tlang.Placeholder("expr") + tlang.Placeholder("K_NOT") / tlang.null + tlang.Placeholder("K_IN") + ( (tlang.Terminal('(') + ( tlang.Placeholder("select_stmt") // (tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )))
                          ) / tlang.null + tlang.Terminal(')')) // (( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name")) )) // (( (( tlang.Placeholder("K_NOT") ) / tlang.null + tlang.Placeholder("K_EXISTS")) ) / tlang.null + tlang.Terminal('(') + tlang.Placeholder("select_stmt") + tlang.Terminal(')')) // (tlang.Placeholder("K_CASE") + tlang.Placeholder("expr") / tlang.null + (( (tlang.Placeholder("K_WHEN") + tlang.Placeholder("expr") + tlang.Placeholder("K_THEN") + tlang.Placeholder("expr")) ) + tlang.pgreedy(( (tlang.Placeholder("K_WHEN") + tlang.Placeholder("expr") + tlang.Placeholder("K_THEN") + tlang.Placeholder("expr")) ))) + ( (tlang.Placeholder("K_ELSE") + tlang.Placeholder("expr")) ) / tlang.null + tlang.Placeholder("K_END")) // tlang.Placeholder("raise_function")

foreign_key_clause = (tlang.Placeholder("K_REFERENCES") + tlang.Placeholder("foreign_table") + ( (tlang.Terminal('(') + tlang.Placeholder("column_name") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name")) )) + tlang.Terminal(')')) ) / tlang.null + tlang.pgreedy(( ( (tlang.Placeholder("K_ON") + ( tlang.Placeholder("K_DELETE") // tlang.Placeholder("K_UPDATE") ) + ( (tlang.Placeholder("K_SET") + tlang.Placeholder("K_NULL")) // (tlang.Placeholder("K_SET") + tlang.Placeholder("K_DEFAULT")) // tlang.Placeholder("K_CASCADE") // tlang.Placeholder("K_RESTRICT") // (tlang.Placeholder("K_NO") + tlang.Placeholder("K_ACTION")) )) // (tlang.Placeholder("K_MATCH") + tlang.Placeholder("name"))
     ) 
   )) + ( (tlang.Placeholder("K_NOT") / tlang.null + tlang.Placeholder("K_DEFERRABLE") + ( (tlang.Placeholder("K_INITIALLY") + tlang.Placeholder("K_DEFERRED")) // (tlang.Placeholder("K_INITIALLY") + tlang.Placeholder("K_IMMEDIATE")) ) / tlang.null) ) / tlang.null)

raise_function = (tlang.Placeholder("K_RAISE") + tlang.Terminal('(') + ( tlang.Placeholder("K_IGNORE") // (( tlang.Placeholder("K_ROLLBACK") // tlang.Placeholder("K_ABORT") // tlang.Placeholder("K_FAIL") ) + tlang.Terminal(',') + tlang.Placeholder("error_message")) ) + tlang.Terminal(')'))

indexed_column = (tlang.Placeholder("column_name") + ( (tlang.Placeholder("K_COLLATE") + tlang.Placeholder("collation_name")) ) / tlang.null + ( tlang.Placeholder("K_ASC") // tlang.Placeholder("K_DESC") ) / tlang.null)

table_constraint = (( (tlang.Placeholder("K_CONSTRAINT") + tlang.Placeholder("name")) ) / tlang.null + ( (( (tlang.Placeholder("K_PRIMARY") + tlang.Placeholder("K_KEY")) // tlang.Placeholder("K_UNIQUE") ) + tlang.Terminal('(') + tlang.Placeholder("indexed_column") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("indexed_column")) )) + tlang.Terminal(')') + tlang.Placeholder("conflict_clause")) // (tlang.Placeholder("K_CHECK") + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.Terminal(')')) // (tlang.Placeholder("K_FOREIGN") + tlang.Placeholder("K_KEY") + tlang.Terminal('(') + tlang.Placeholder("column_name") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name")) )) + tlang.Terminal(')') + tlang.Placeholder("foreign_key_clause"))
   ))

with_clause = (tlang.Placeholder("K_WITH") + tlang.Placeholder("K_RECURSIVE") / tlang.null + tlang.Placeholder("cte_table_name") + tlang.Placeholder("K_AS") + tlang.Terminal('(') + tlang.Placeholder("select_stmt") + tlang.Terminal(')') + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("cte_table_name") + tlang.Placeholder("K_AS") + tlang.Terminal('(') + tlang.Placeholder("select_stmt") + tlang.Terminal(')')) )))

qualified_table_name = (( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name") + ( (tlang.Placeholder("K_INDEXED") + tlang.Placeholder("K_BY") + tlang.Placeholder("index_name")) // (tlang.Placeholder("K_NOT") + tlang.Placeholder("K_INDEXED")) ) / tlang.null)

ordering_term = (tlang.Placeholder("expr") + ( (tlang.Placeholder("K_COLLATE") + tlang.Placeholder("collation_name")) ) / tlang.null + ( tlang.Placeholder("K_ASC") // tlang.Placeholder("K_DESC") ) / tlang.null)

pragma_value = tlang.Placeholder("signed_number") // tlang.Placeholder("name") // tlang.Placeholder("STRING_LITERAL")

common_table_expression = (tlang.Placeholder("table_name") + ( (tlang.Terminal('(') + tlang.Placeholder("column_name") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name")) )) + tlang.Terminal(')')) ) / tlang.null + tlang.Placeholder("K_AS") + tlang.Terminal('(') + tlang.Placeholder("select_stmt") + tlang.Terminal(')'))

result_column = tlang.Terminal('*') // (tlang.Placeholder("table_name") + tlang.Terminal('.') + tlang.Terminal('*')) // (tlang.Placeholder("expr") + ( (tlang.Placeholder("K_AS") / tlang.null + tlang.Placeholder("column_alias")) ) / tlang.null)

table_or_subquery = (( (tlang.Placeholder("database_name") + tlang.Terminal('.')) ) / tlang.null + tlang.Placeholder("table_name") + ( (tlang.Placeholder("K_AS") / tlang.null + tlang.Placeholder("table_alias")) ) / tlang.null + ( (tlang.Placeholder("K_INDEXED") + tlang.Placeholder("K_BY") + tlang.Placeholder("index_name")) // (tlang.Placeholder("K_NOT") + tlang.Placeholder("K_INDEXED")) ) / tlang.null) // (tlang.Terminal('(') + ( (tlang.Placeholder("table_or_subquery") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("table_or_subquery")) ))) // tlang.Placeholder("join_clause") ) + tlang.Terminal(')') + ( (tlang.Placeholder("K_AS") / tlang.null + tlang.Placeholder("table_alias")) ) / tlang.null) // (tlang.Terminal('(') + tlang.Placeholder("select_stmt") + tlang.Terminal(')') + ( (tlang.Placeholder("K_AS") / tlang.null + tlang.Placeholder("table_alias")) ) / tlang.null)

join_clause = (tlang.Placeholder("table_or_subquery") + tlang.pgreedy(( (tlang.Placeholder("join_operator") + tlang.Placeholder("table_or_subquery") + tlang.Placeholder("join_constraint")) )))

join_operator = tlang.Terminal(',') // (tlang.Placeholder("K_NATURAL") / tlang.null + ( (tlang.Placeholder("K_LEFT") + tlang.Placeholder("K_OUTER") / tlang.null) // tlang.Placeholder("K_INNER") // tlang.Placeholder("K_CROSS") ) / tlang.null + tlang.Placeholder("K_JOIN"))

join_constraint = ( (tlang.Placeholder("K_ON") + tlang.Placeholder("expr")) // (tlang.Placeholder("K_USING") + tlang.Terminal('(') + tlang.Placeholder("column_name") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name")) )) + tlang.Terminal(')')) ) / tlang.null

select_core = (tlang.Placeholder("K_SELECT") + ( tlang.Placeholder("K_DISTINCT") // tlang.Placeholder("K_ALL") ) / tlang.null + tlang.Placeholder("result_column") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("result_column")) )) + ( (tlang.Placeholder("K_FROM") + ( (tlang.Placeholder("table_or_subquery") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("table_or_subquery")) ))) // tlang.Placeholder("join_clause") )) ) / tlang.null + ( (tlang.Placeholder("K_WHERE") + tlang.Placeholder("expr")) ) / tlang.null + ( (tlang.Placeholder("K_GROUP") + tlang.Placeholder("K_BY") + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )) + ( (tlang.Placeholder("K_HAVING") + tlang.Placeholder("expr")) ) / tlang.null) ) / tlang.null) // (tlang.Placeholder("K_VALUES") + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )) + tlang.Terminal(')') + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Terminal('(') + tlang.Placeholder("expr") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("expr")) )) + tlang.Terminal(')')) )))

compound_operator = tlang.Placeholder("K_UNION") // (tlang.Placeholder("K_UNION") + tlang.Placeholder("K_ALL")) // tlang.Placeholder("K_INTERSECT") // tlang.Placeholder("K_EXCEPT")

cte_table_name = (tlang.Placeholder("table_name") + ( (tlang.Terminal('(') + tlang.Placeholder("column_name") + tlang.pgreedy(( (tlang.Terminal(',') + tlang.Placeholder("column_name")) )) + tlang.Terminal(')')) ) / tlang.null)

signed_number = (( tlang.Terminal('+') // tlang.Terminal('-') ) / tlang.null + tlang.Placeholder("NUMERIC_LITERAL"))

literal_value = tlang.Placeholder("NUMERIC_LITERAL") // tlang.Placeholder("STRING_LITERAL") // tlang.Placeholder("BLOB_LITERAL") // tlang.Placeholder("K_NULL") // tlang.Placeholder("K_CURRENT_TIME") // tlang.Placeholder("K_CURRENT_DATE") // tlang.Placeholder("K_CURRENT_TIMESTAMP")

unary_operator = tlang.Terminal('-') // tlang.Terminal('+') // tlang.Terminal('~') // tlang.Placeholder("K_NOT")

error_message = tlang.Placeholder("STRING_LITERAL")

module_argument = tlang.Placeholder("expr") // tlang.Placeholder("column_def")

column_alias = tlang.Placeholder("IDENTIFIER") // tlang.Placeholder("STRING_LITERAL")

keyword = tlang.Placeholder("K_ABORT") // tlang.Placeholder("K_ACTION") // tlang.Placeholder("K_ADD") // tlang.Placeholder("K_AFTER") // tlang.Placeholder("K_ALL") // tlang.Placeholder("K_ALTER") // tlang.Placeholder("K_ANALYZE") // tlang.Placeholder("K_AND") // tlang.Placeholder("K_AS") // tlang.Placeholder("K_ASC") // tlang.Placeholder("K_ATTACH") // tlang.Placeholder("K_AUTOINCREMENT") // tlang.Placeholder("K_BEFORE") // tlang.Placeholder("K_BEGIN") // tlang.Placeholder("K_BETWEEN") // tlang.Placeholder("K_BY") // tlang.Placeholder("K_CASCADE") // tlang.Placeholder("K_CASE") // tlang.Placeholder("K_CAST") // tlang.Placeholder("K_CHECK") // tlang.Placeholder("K_COLLATE") // tlang.Placeholder("K_COLUMN") // tlang.Placeholder("K_COMMIT") // tlang.Placeholder("K_CONFLICT") // tlang.Placeholder("K_CONSTRAINT") // tlang.Placeholder("K_CREATE") // tlang.Placeholder("K_CROSS") // tlang.Placeholder("K_CURRENT_DATE") // tlang.Placeholder("K_CURRENT_TIME") // tlang.Placeholder("K_CURRENT_TIMESTAMP") // tlang.Placeholder("K_DATABASE") // tlang.Placeholder("K_DEFAULT") // tlang.Placeholder("K_DEFERRABLE") // tlang.Placeholder("K_DEFERRED") // tlang.Placeholder("K_DELETE") // tlang.Placeholder("K_DESC") // tlang.Placeholder("K_DETACH") // tlang.Placeholder("K_DISTINCT") // tlang.Placeholder("K_DROP") // tlang.Placeholder("K_EACH") // tlang.Placeholder("K_ELSE") // tlang.Placeholder("K_END") // tlang.Placeholder("K_ESCAPE") // tlang.Placeholder("K_EXCEPT") // tlang.Placeholder("K_EXCLUSIVE") // tlang.Placeholder("K_EXISTS") // tlang.Placeholder("K_EXPLAIN") // tlang.Placeholder("K_FAIL") // tlang.Placeholder("K_FOR") // tlang.Placeholder("K_FOREIGN") // tlang.Placeholder("K_FROM") // tlang.Placeholder("K_FULL") // tlang.Placeholder("K_GLOB") // tlang.Placeholder("K_GROUP") // tlang.Placeholder("K_HAVING") // tlang.Placeholder("K_IF") // tlang.Placeholder("K_IGNORE") // tlang.Placeholder("K_IMMEDIATE") // tlang.Placeholder("K_IN") // tlang.Placeholder("K_INDEX") // tlang.Placeholder("K_INDEXED") // tlang.Placeholder("K_INITIALLY") // tlang.Placeholder("K_INNER") // tlang.Placeholder("K_INSERT") // tlang.Placeholder("K_INSTEAD") // tlang.Placeholder("K_INTERSECT") // tlang.Placeholder("K_INTO") // tlang.Placeholder("K_IS") // tlang.Placeholder("K_ISNULL") // tlang.Placeholder("K_JOIN") // tlang.Placeholder("K_KEY") // tlang.Placeholder("K_LEFT") // tlang.Placeholder("K_LIKE") // tlang.Placeholder("K_LIMIT") // tlang.Placeholder("K_MATCH") // tlang.Placeholder("K_NATURAL") // tlang.Placeholder("K_NO") // tlang.Placeholder("K_NOT") // tlang.Placeholder("K_NOTNULL") // tlang.Placeholder("K_NULL") // tlang.Placeholder("K_OF") // tlang.Placeholder("K_OFFSET") // tlang.Placeholder("K_ON") // tlang.Placeholder("K_OR") // tlang.Placeholder("K_ORDER") // tlang.Placeholder("K_OUTER") // tlang.Placeholder("K_PLAN") // tlang.Placeholder("K_PRAGMA") // tlang.Placeholder("K_PRIMARY") // tlang.Placeholder("K_QUERY") // tlang.Placeholder("K_RAISE") // tlang.Placeholder("K_RECURSIVE") // tlang.Placeholder("K_REFERENCES") // tlang.Placeholder("K_REGEXP") // tlang.Placeholder("K_REINDEX") // tlang.Placeholder("K_RELEASE") // tlang.Placeholder("K_RENAME") // tlang.Placeholder("K_REPLACE") // tlang.Placeholder("K_RESTRICT") // tlang.Placeholder("K_RIGHT") // tlang.Placeholder("K_ROLLBACK") // tlang.Placeholder("K_ROW") // tlang.Placeholder("K_SAVEPOINT") // tlang.Placeholder("K_SELECT") // tlang.Placeholder("K_SET") // tlang.Placeholder("K_TABLE") // tlang.Placeholder("K_TEMP") // tlang.Placeholder("K_TEMPORARY") // tlang.Placeholder("K_THEN") // tlang.Placeholder("K_TO") // tlang.Placeholder("K_TRANSACTION") // tlang.Placeholder("K_TRIGGER") // tlang.Placeholder("K_UNION") // tlang.Placeholder("K_UNIQUE") // tlang.Placeholder("K_UPDATE") // tlang.Placeholder("K_USING") // tlang.Placeholder("K_VACUUM") // tlang.Placeholder("K_VALUES") // tlang.Placeholder("K_VIEW") // tlang.Placeholder("K_VIRTUAL") // tlang.Placeholder("K_WHEN") // tlang.Placeholder("K_WHERE") // tlang.Placeholder("K_WITH") // tlang.Placeholder("K_WITHOUT")

# TODO check all names below

name = tlang.Placeholder("any_name")

function_name = tlang.Placeholder("any_name")

database_name = tlang.Placeholder("any_name")

table_name = tlang.Placeholder("any_name")

table_or_index_name = tlang.Placeholder("any_name")

new_table_name = tlang.Placeholder("any_name")

column_name = tlang.Placeholder("any_name")

collation_name = tlang.Placeholder("any_name")

foreign_table = tlang.Placeholder("any_name")

index_name = tlang.Placeholder("any_name")

trigger_name = tlang.Placeholder("any_name")

view_name = tlang.Placeholder("any_name")

module_name = tlang.Placeholder("any_name")

pragma_name = tlang.Placeholder("any_name")

savepoint_name = tlang.Placeholder("any_name")

table_alias = tlang.Placeholder("any_name")

transaction_name = tlang.Placeholder("any_name")

any_name = tlang.Placeholder("IDENTIFIER") // keyword // tlang.Placeholder("STRING_LITERAL") // (tlang.Terminal('(') + tlang.Placeholder("any_name") + tlang.Terminal(')'))

SCOL = tlang.Terminal(';')
DOT = tlang.Terminal('.')
OPEN_PAR = tlang.Terminal('(')
CLOSE_PAR = tlang.Terminal(')')
COMMA = tlang.Terminal(',')
ASSIGN = tlang.Terminal('=')
STAR = tlang.Terminal('*')
PLUS = tlang.Terminal('+')
MINUS = tlang.Terminal('-')
TILDE = tlang.Terminal('~')
PIPE2 = tlang.Terminal('||')
DIV = tlang.Terminal('/')
MOD = tlang.Terminal('%')
LT2 = tlang.Terminal('<<')
GT2 = tlang.Terminal('>>')
AMP = tlang.Terminal('&')
PIPE = tlang.Terminal('|')
LT = tlang.Terminal('<')
LT_EQ = tlang.Terminal('<=')
GT = tlang.Terminal('>')
GT_EQ = tlang.Terminal('>=')
EQ = tlang.Terminal('==')
NOT_EQ1 = tlang.Terminal('!=')
NOT_EQ2 = tlang.Terminal('<>')

# http://www.sqlite.org/lang_keywords.html
K_ABORT = (tlang.Placeholder("A") + tlang.Placeholder("B") + tlang.Placeholder("O") + tlang.Placeholder("R") + tlang.Placeholder("T"))
K_ACTION = (tlang.Placeholder("A") + tlang.Placeholder("C") + tlang.Placeholder("T") + tlang.Placeholder("I") + tlang.Placeholder("O") + tlang.Placeholder("N"))
K_ADD = (tlang.Placeholder("A") + tlang.Placeholder("D") + tlang.Placeholder("D"))
K_AFTER = (tlang.Placeholder("A") + tlang.Placeholder("F") + tlang.Placeholder("T") + tlang.Placeholder("E") + tlang.Placeholder("R"))
K_ALL = (tlang.Placeholder("A") + tlang.Placeholder("L") + tlang.Placeholder("L"))
K_ALTER = (tlang.Placeholder("A") + tlang.Placeholder("L") + tlang.Placeholder("T") + tlang.Placeholder("E") + tlang.Placeholder("R"))
K_ANALYZE = (tlang.Placeholder("A") + tlang.Placeholder("N") + tlang.Placeholder("A") + tlang.Placeholder("L") + tlang.Placeholder("Y") + tlang.Placeholder("Z") + tlang.Placeholder("E"))
K_AND = (tlang.Placeholder("A") + tlang.Placeholder("N") + tlang.Placeholder("D"))
K_AS = (tlang.Placeholder("A") + tlang.Placeholder("S"))
K_ASC = (tlang.Placeholder("A") + tlang.Placeholder("S") + tlang.Placeholder("C"))
K_ATTACH = (tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("T") + tlang.Placeholder("A") + tlang.Placeholder("C") + tlang.Placeholder("H"))
K_AUTOINCREMENT = (tlang.Placeholder("A") + tlang.Placeholder("U") + tlang.Placeholder("T") + tlang.Placeholder("O") + tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("C") + tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("M") + tlang.Placeholder("E") + tlang.Placeholder("N") + tlang.Placeholder("T"))
K_BEFORE = (tlang.Placeholder("B") + tlang.Placeholder("E") + tlang.Placeholder("F") + tlang.Placeholder("O") + tlang.Placeholder("R") + tlang.Placeholder("E"))
K_BEGIN = (tlang.Placeholder("B") + tlang.Placeholder("E") + tlang.Placeholder("G") + tlang.Placeholder("I") + tlang.Placeholder("N"))
K_BETWEEN = (tlang.Placeholder("B") + tlang.Placeholder("E") + tlang.Placeholder("T") + tlang.Placeholder("W") + tlang.Placeholder("E") + tlang.Placeholder("E") + tlang.Placeholder("N"))
K_BY = (tlang.Placeholder("B") + tlang.Placeholder("Y"))
K_CASCADE = (tlang.Placeholder("C") + tlang.Placeholder("A") + tlang.Placeholder("S") + tlang.Placeholder("C") + tlang.Placeholder("A") + tlang.Placeholder("D") + tlang.Placeholder("E"))
K_CASE = (tlang.Placeholder("C") + tlang.Placeholder("A") + tlang.Placeholder("S") + tlang.Placeholder("E"))
K_CAST = (tlang.Placeholder("C") + tlang.Placeholder("A") + tlang.Placeholder("S") + tlang.Placeholder("T"))
K_CHECK = (tlang.Placeholder("C") + tlang.Placeholder("H") + tlang.Placeholder("E") + tlang.Placeholder("C") + tlang.Placeholder("K"))
K_COLLATE = (tlang.Placeholder("C") + tlang.Placeholder("O") + tlang.Placeholder("L") + tlang.Placeholder("L") + tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("E"))
K_COLUMN = (tlang.Placeholder("C") + tlang.Placeholder("O") + tlang.Placeholder("L") + tlang.Placeholder("U") + tlang.Placeholder("M") + tlang.Placeholder("N"))
K_COMMIT = (tlang.Placeholder("C") + tlang.Placeholder("O") + tlang.Placeholder("M") + tlang.Placeholder("M") + tlang.Placeholder("I") + tlang.Placeholder("T"))
K_CONFLICT = (tlang.Placeholder("C") + tlang.Placeholder("O") + tlang.Placeholder("N") + tlang.Placeholder("F") + tlang.Placeholder("L") + tlang.Placeholder("I") + tlang.Placeholder("C") + tlang.Placeholder("T"))
K_CONSTRAINT = (tlang.Placeholder("C") + tlang.Placeholder("O") + tlang.Placeholder("N") + tlang.Placeholder("S") + tlang.Placeholder("T") + tlang.Placeholder("R") + tlang.Placeholder("A") + tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("T"))
K_CREATE = (tlang.Placeholder("C") + tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("E"))
K_CROSS = (tlang.Placeholder("C") + tlang.Placeholder("R") + tlang.Placeholder("O") + tlang.Placeholder("S") + tlang.Placeholder("S"))
K_CURRENT_DATE = (tlang.Placeholder("C") + tlang.Placeholder("U") + tlang.Placeholder("R") + tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("N") + tlang.Placeholder("T") + tlang.Terminal('_') + tlang.Placeholder("D") + tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("E"))
K_CURRENT_TIME = (tlang.Placeholder("C") + tlang.Placeholder("U") + tlang.Placeholder("R") + tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("N") + tlang.Placeholder("T") + tlang.Terminal('_') + tlang.Placeholder("T") + tlang.Placeholder("I") + tlang.Placeholder("M") + tlang.Placeholder("E"))
K_CURRENT_TIMESTAMP = (tlang.Placeholder("C") + tlang.Placeholder("U") + tlang.Placeholder("R") + tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("N") + tlang.Placeholder("T") + tlang.Terminal('_') + tlang.Placeholder("T") + tlang.Placeholder("I") + tlang.Placeholder("M") + tlang.Placeholder("E") + tlang.Placeholder("S") + tlang.Placeholder("T") + tlang.Placeholder("A") + tlang.Placeholder("M") + tlang.Placeholder("P"))
K_DATABASE = (tlang.Placeholder("D") + tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("A") + tlang.Placeholder("B") + tlang.Placeholder("A") + tlang.Placeholder("S") + tlang.Placeholder("E"))
K_DEFAULT = (tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("F") + tlang.Placeholder("A") + tlang.Placeholder("U") + tlang.Placeholder("L") + tlang.Placeholder("T"))
K_DEFERRABLE = (tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("F") + tlang.Placeholder("E") + tlang.Placeholder("R") + tlang.Placeholder("R") + tlang.Placeholder("A") + tlang.Placeholder("B") + tlang.Placeholder("L") + tlang.Placeholder("E"))
K_DEFERRED = (tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("F") + tlang.Placeholder("E") + tlang.Placeholder("R") + tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("D"))
K_DELETE = (tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("L") + tlang.Placeholder("E") + tlang.Placeholder("T") + tlang.Placeholder("E"))
K_DESC = (tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("S") + tlang.Placeholder("C"))
K_DETACH = (tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("T") + tlang.Placeholder("A") + tlang.Placeholder("C") + tlang.Placeholder("H"))
K_DISTINCT = (tlang.Placeholder("D") + tlang.Placeholder("I") + tlang.Placeholder("S") + tlang.Placeholder("T") + tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("C") + tlang.Placeholder("T"))
K_DROP = (tlang.Placeholder("D") + tlang.Placeholder("R") + tlang.Placeholder("O") + tlang.Placeholder("P"))
K_EACH = (tlang.Placeholder("E") + tlang.Placeholder("A") + tlang.Placeholder("C") + tlang.Placeholder("H"))
K_ELSE = (tlang.Placeholder("E") + tlang.Placeholder("L") + tlang.Placeholder("S") + tlang.Placeholder("E"))
K_END = (tlang.Placeholder("E") + tlang.Placeholder("N") + tlang.Placeholder("D"))
K_ESCAPE = (tlang.Placeholder("E") + tlang.Placeholder("S") + tlang.Placeholder("C") + tlang.Placeholder("A") + tlang.Placeholder("P") + tlang.Placeholder("E"))
K_EXCEPT = (tlang.Placeholder("E") + tlang.Placeholder("X") + tlang.Placeholder("C") + tlang.Placeholder("E") + tlang.Placeholder("P") + tlang.Placeholder("T"))
K_EXCLUSIVE = (tlang.Placeholder("E") + tlang.Placeholder("X") + tlang.Placeholder("C") + tlang.Placeholder("L") + tlang.Placeholder("U") + tlang.Placeholder("S") + tlang.Placeholder("I") + tlang.Placeholder("V") + tlang.Placeholder("E"))
K_EXISTS = (tlang.Placeholder("E") + tlang.Placeholder("X") + tlang.Placeholder("I") + tlang.Placeholder("S") + tlang.Placeholder("T") + tlang.Placeholder("S"))
K_EXPLAIN = (tlang.Placeholder("E") + tlang.Placeholder("X") + tlang.Placeholder("P") + tlang.Placeholder("L") + tlang.Placeholder("A") + tlang.Placeholder("I") + tlang.Placeholder("N"))
K_FAIL = (tlang.Placeholder("F") + tlang.Placeholder("A") + tlang.Placeholder("I") + tlang.Placeholder("L"))
K_FOR = (tlang.Placeholder("F") + tlang.Placeholder("O") + tlang.Placeholder("R"))
K_FOREIGN = (tlang.Placeholder("F") + tlang.Placeholder("O") + tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("I") + tlang.Placeholder("G") + tlang.Placeholder("N"))
K_FROM = (tlang.Placeholder("F") + tlang.Placeholder("R") + tlang.Placeholder("O") + tlang.Placeholder("M"))
K_FULL = (tlang.Placeholder("F") + tlang.Placeholder("U") + tlang.Placeholder("L") + tlang.Placeholder("L"))
K_GLOB = (tlang.Placeholder("G") + tlang.Placeholder("L") + tlang.Placeholder("O") + tlang.Placeholder("B"))
K_GROUP = (tlang.Placeholder("G") + tlang.Placeholder("R") + tlang.Placeholder("O") + tlang.Placeholder("U") + tlang.Placeholder("P"))
K_HAVING = (tlang.Placeholder("H") + tlang.Placeholder("A") + tlang.Placeholder("V") + tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("G"))
K_IF = (tlang.Placeholder("I") + tlang.Placeholder("F"))
K_IGNORE = (tlang.Placeholder("I") + tlang.Placeholder("G") + tlang.Placeholder("N") + tlang.Placeholder("O") + tlang.Placeholder("R") + tlang.Placeholder("E"))
K_IMMEDIATE = (tlang.Placeholder("I") + tlang.Placeholder("M") + tlang.Placeholder("M") + tlang.Placeholder("E") + tlang.Placeholder("D") + tlang.Placeholder("I") + tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("E"))
K_IN = (tlang.Placeholder("I") + tlang.Placeholder("N"))
K_INDEX = (tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("X"))
K_INDEXED = (tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("X") + tlang.Placeholder("E") + tlang.Placeholder("D"))
K_INITIALLY = (tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("I") + tlang.Placeholder("T") + tlang.Placeholder("I") + tlang.Placeholder("A") + tlang.Placeholder("L") + tlang.Placeholder("L") + tlang.Placeholder("Y"))
K_INNER = (tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("N") + tlang.Placeholder("E") + tlang.Placeholder("R"))
K_INSERT = (tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("S") + tlang.Placeholder("E") + tlang.Placeholder("R") + tlang.Placeholder("T"))
K_INSTEAD = (tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("S") + tlang.Placeholder("T") + tlang.Placeholder("E") + tlang.Placeholder("A") + tlang.Placeholder("D"))
K_INTERSECT = (tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("T") + tlang.Placeholder("E") + tlang.Placeholder("R") + tlang.Placeholder("S") + tlang.Placeholder("E") + tlang.Placeholder("C") + tlang.Placeholder("T"))
K_INTO = (tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("T") + tlang.Placeholder("O"))
K_IS = (tlang.Placeholder("I") + tlang.Placeholder("S"))
K_ISNULL = (tlang.Placeholder("I") + tlang.Placeholder("S") + tlang.Placeholder("N") + tlang.Placeholder("U") + tlang.Placeholder("L") + tlang.Placeholder("L"))
K_JOIN = (tlang.Placeholder("J") + tlang.Placeholder("O") + tlang.Placeholder("I") + tlang.Placeholder("N"))
K_KEY = (tlang.Placeholder("K") + tlang.Placeholder("E") + tlang.Placeholder("Y"))
K_LEFT = (tlang.Placeholder("L") + tlang.Placeholder("E") + tlang.Placeholder("F") + tlang.Placeholder("T"))
K_LIKE = (tlang.Placeholder("L") + tlang.Placeholder("I") + tlang.Placeholder("K") + tlang.Placeholder("E"))
K_LIMIT = (tlang.Placeholder("L") + tlang.Placeholder("I") + tlang.Placeholder("M") + tlang.Placeholder("I") + tlang.Placeholder("T"))
K_MATCH = (tlang.Placeholder("M") + tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("C") + tlang.Placeholder("H"))
K_NATURAL = (tlang.Placeholder("N") + tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("U") + tlang.Placeholder("R") + tlang.Placeholder("A") + tlang.Placeholder("L"))
K_NO = (tlang.Placeholder("N") + tlang.Placeholder("O"))
K_NOT = (tlang.Placeholder("N") + tlang.Placeholder("O") + tlang.Placeholder("T"))
K_NOTNULL = (tlang.Placeholder("N") + tlang.Placeholder("O") + tlang.Placeholder("T") + tlang.Placeholder("N") + tlang.Placeholder("U") + tlang.Placeholder("L") + tlang.Placeholder("L"))
K_NULL = (tlang.Placeholder("N") + tlang.Placeholder("U") + tlang.Placeholder("L") + tlang.Placeholder("L"))
K_OF = (tlang.Placeholder("O") + tlang.Placeholder("F"))
K_OFFSET = (tlang.Placeholder("O") + tlang.Placeholder("F") + tlang.Placeholder("F") + tlang.Placeholder("S") + tlang.Placeholder("E") + tlang.Placeholder("T"))
K_ON = (tlang.Placeholder("O") + tlang.Placeholder("N"))
K_OR = (tlang.Placeholder("O") + tlang.Placeholder("R"))
K_ORDER = (tlang.Placeholder("O") + tlang.Placeholder("R") + tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("R"))
K_OUTER = (tlang.Placeholder("O") + tlang.Placeholder("U") + tlang.Placeholder("T") + tlang.Placeholder("E") + tlang.Placeholder("R"))
K_PLAN = (tlang.Placeholder("P") + tlang.Placeholder("L") + tlang.Placeholder("A") + tlang.Placeholder("N"))
K_PRAGMA = (tlang.Placeholder("P") + tlang.Placeholder("R") + tlang.Placeholder("A") + tlang.Placeholder("G") + tlang.Placeholder("M") + tlang.Placeholder("A"))
K_PRIMARY = (tlang.Placeholder("P") + tlang.Placeholder("R") + tlang.Placeholder("I") + tlang.Placeholder("M") + tlang.Placeholder("A") + tlang.Placeholder("R") + tlang.Placeholder("Y"))
K_QUERY = (tlang.Placeholder("Q") + tlang.Placeholder("U") + tlang.Placeholder("E") + tlang.Placeholder("R") + tlang.Placeholder("Y"))
K_RAISE = (tlang.Placeholder("R") + tlang.Placeholder("A") + tlang.Placeholder("I") + tlang.Placeholder("S") + tlang.Placeholder("E"))
K_RECURSIVE = (tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("C") + tlang.Placeholder("U") + tlang.Placeholder("R") + tlang.Placeholder("S") + tlang.Placeholder("I") + tlang.Placeholder("V") + tlang.Placeholder("E"))
K_REFERENCES = (tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("F") + tlang.Placeholder("E") + tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("N") + tlang.Placeholder("C") + tlang.Placeholder("E") + tlang.Placeholder("S"))
K_REGEXP = (tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("G") + tlang.Placeholder("E") + tlang.Placeholder("X") + tlang.Placeholder("P"))
K_REINDEX = (tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("D") + tlang.Placeholder("E") + tlang.Placeholder("X"))
K_RELEASE = (tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("L") + tlang.Placeholder("E") + tlang.Placeholder("A") + tlang.Placeholder("S") + tlang.Placeholder("E"))
K_RENAME = (tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("N") + tlang.Placeholder("A") + tlang.Placeholder("M") + tlang.Placeholder("E"))
K_REPLACE = (tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("P") + tlang.Placeholder("L") + tlang.Placeholder("A") + tlang.Placeholder("C") + tlang.Placeholder("E"))
K_RESTRICT = (tlang.Placeholder("R") + tlang.Placeholder("E") + tlang.Placeholder("S") + tlang.Placeholder("T") + tlang.Placeholder("R") + tlang.Placeholder("I") + tlang.Placeholder("C") + tlang.Placeholder("T"))
K_RIGHT = (tlang.Placeholder("R") + tlang.Placeholder("I") + tlang.Placeholder("G") + tlang.Placeholder("H") + tlang.Placeholder("T"))
K_ROLLBACK = (tlang.Placeholder("R") + tlang.Placeholder("O") + tlang.Placeholder("L") + tlang.Placeholder("L") + tlang.Placeholder("B") + tlang.Placeholder("A") + tlang.Placeholder("C") + tlang.Placeholder("K"))
K_ROW = (tlang.Placeholder("R") + tlang.Placeholder("O") + tlang.Placeholder("W"))
K_SAVEPOINT = (tlang.Placeholder("S") + tlang.Placeholder("A") + tlang.Placeholder("V") + tlang.Placeholder("E") + tlang.Placeholder("P") + tlang.Placeholder("O") + tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("T"))
K_SELECT = (tlang.Placeholder("S") + tlang.Placeholder("E") + tlang.Placeholder("L") + tlang.Placeholder("E") + tlang.Placeholder("C") + tlang.Placeholder("T"))
K_SET = (tlang.Placeholder("S") + tlang.Placeholder("E") + tlang.Placeholder("T"))
K_TABLE = (tlang.Placeholder("T") + tlang.Placeholder("A") + tlang.Placeholder("B") + tlang.Placeholder("L") + tlang.Placeholder("E"))
K_TEMP = (tlang.Placeholder("T") + tlang.Placeholder("E") + tlang.Placeholder("M") + tlang.Placeholder("P"))
K_TEMPORARY = (tlang.Placeholder("T") + tlang.Placeholder("E") + tlang.Placeholder("M") + tlang.Placeholder("P") + tlang.Placeholder("O") + tlang.Placeholder("R") + tlang.Placeholder("A") + tlang.Placeholder("R") + tlang.Placeholder("Y"))
K_THEN = (tlang.Placeholder("T") + tlang.Placeholder("H") + tlang.Placeholder("E") + tlang.Placeholder("N"))
K_TO = (tlang.Placeholder("T") + tlang.Placeholder("O"))
K_TRANSACTION = (tlang.Placeholder("T") + tlang.Placeholder("R") + tlang.Placeholder("A") + tlang.Placeholder("N") + tlang.Placeholder("S") + tlang.Placeholder("A") + tlang.Placeholder("C") + tlang.Placeholder("T") + tlang.Placeholder("I") + tlang.Placeholder("O") + tlang.Placeholder("N"))
K_TRIGGER = (tlang.Placeholder("T") + tlang.Placeholder("R") + tlang.Placeholder("I") + tlang.Placeholder("G") + tlang.Placeholder("G") + tlang.Placeholder("E") + tlang.Placeholder("R"))
K_UNION = (tlang.Placeholder("U") + tlang.Placeholder("N") + tlang.Placeholder("I") + tlang.Placeholder("O") + tlang.Placeholder("N"))
K_UNIQUE = (tlang.Placeholder("U") + tlang.Placeholder("N") + tlang.Placeholder("I") + tlang.Placeholder("Q") + tlang.Placeholder("U") + tlang.Placeholder("E"))
K_UPDATE = (tlang.Placeholder("U") + tlang.Placeholder("P") + tlang.Placeholder("D") + tlang.Placeholder("A") + tlang.Placeholder("T") + tlang.Placeholder("E"))
K_USING = (tlang.Placeholder("U") + tlang.Placeholder("S") + tlang.Placeholder("I") + tlang.Placeholder("N") + tlang.Placeholder("G"))
K_VACUUM = (tlang.Placeholder("V") + tlang.Placeholder("A") + tlang.Placeholder("C") + tlang.Placeholder("U") + tlang.Placeholder("U") + tlang.Placeholder("M"))
K_VALUES = (tlang.Placeholder("V") + tlang.Placeholder("A") + tlang.Placeholder("L") + tlang.Placeholder("U") + tlang.Placeholder("E") + tlang.Placeholder("S"))
K_VIEW = (tlang.Placeholder("V") + tlang.Placeholder("I") + tlang.Placeholder("E") + tlang.Placeholder("W"))
K_VIRTUAL = (tlang.Placeholder("V") + tlang.Placeholder("I") + tlang.Placeholder("R") + tlang.Placeholder("T") + tlang.Placeholder("U") + tlang.Placeholder("A") + tlang.Placeholder("L"))
K_WHEN = (tlang.Placeholder("W") + tlang.Placeholder("H") + tlang.Placeholder("E") + tlang.Placeholder("N"))
K_WHERE = (tlang.Placeholder("W") + tlang.Placeholder("H") + tlang.Placeholder("E") + tlang.Placeholder("R") + tlang.Placeholder("E"))
K_WITH = (tlang.Placeholder("W") + tlang.Placeholder("I") + tlang.Placeholder("T") + tlang.Placeholder("H"))
K_WITHOUT = (tlang.Placeholder("W") + tlang.Placeholder("I") + tlang.Placeholder("T") + tlang.Placeholder("H") + tlang.Placeholder("O") + tlang.Placeholder("U") + tlang.Placeholder("T"))

IDENTIFIER = (tlang.Terminal('"') + tlang.pgreedy((( tlang.Terminal('+') // tlang.Terminal('-') ).inv() // tlang.Terminal('""'))) + tlang.Terminal('"')) // (tlang.Terminal('`') + tlang.pgreedy(((( tlang.Terminal('+') // tlang.Terminal('-') ).inv() // tlang.Terminal('""')).inv() // tlang.Terminal('``'))) + tlang.Terminal('`')) // (tlang.Terminal('[') + tlang.Terminal(']').inv() + tlang.Terminal(']')) // (tlang.oneof(("abcdefghijklmnopqrstuvwxyz")) / tlang.oneof(("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) / tlang.Terminal("_") + tlang.pgreedy(tlang.oneof(("abcdefghijklmnopqrstuvwxyz")) / tlang.oneof(("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) / tlang.Terminal("_") / tlang.oneof(("0123456789"))))

NUMERIC_LITERAL = ((tlang.Placeholder("DIGIT") + tlang.pgreedy(tlang.Placeholder("DIGIT"))) + ( (tlang.Terminal('.') + tlang.pgreedy(tlang.Placeholder("DIGIT"))) ) / tlang.null + ( (tlang.Placeholder("E") + tlang.Terminal("-") / tlang.Terminal("+") / tlang.null + (tlang.Placeholder("DIGIT") + tlang.pgreedy(tlang.Placeholder("DIGIT")))) ) / tlang.null) // (tlang.Terminal('.') + (tlang.Placeholder("DIGIT") + tlang.pgreedy(tlang.Placeholder("DIGIT"))) + ( (tlang.Placeholder("E") + tlang.Terminal("-") / tlang.Terminal("+") / tlang.null + (tlang.Placeholder("DIGIT") + tlang.pgreedy(tlang.Placeholder("DIGIT")))) ) / tlang.null)

BIND_PARAMETER = (tlang.Terminal('?') + tlang.pgreedy(tlang.Placeholder("DIGIT"))) // (tlang.Terminal(":") / tlang.Terminal("@") / tlang.Terminal("$") + tlang.Placeholder("IDENTIFIER"))

STRING_LITERAL = (tlang.Terminal('\'') + tlang.pgreedy(( tlang.Placeholder("DIGIT").inv() // tlang.Terminal('\'\'') )) + tlang.Terminal('\''))

BLOB_LITERAL = (tlang.Placeholder("X") + tlang.Placeholder("STRING_LITERAL"))

SINGLE_LINE_COMMENT = (tlang.Terminal('--') + tlang.Terminal("\r") / tlang.Terminal("\n").inv())

MULTILINE_COMMENT = (tlang.Terminal('/*') + tlang.pgreedy(tlang.wild) / tlang.null + ( tlang.Terminal('*/') // tlang.Placeholder("EOF") ))

SPACES = tlang.Terminal(" ") / tlang.Terminal("\u000B") / tlang.Terminal("\t") / tlang.Terminal("\r") / tlang.Terminal("\n")

UNEXPECTED_CHAR = tlang.wild

DIGIT = tlang.oneof(("0123456789"))

A = tlang.Terminal("a") / tlang.Terminal("A")
B = tlang.Terminal("b") / tlang.Terminal("B")
C = tlang.Terminal("c") / tlang.Terminal("C")
D = tlang.Terminal("d") / tlang.Terminal("D")
E = tlang.Terminal("e") / tlang.Terminal("E")
F = tlang.Terminal("f") / tlang.Terminal("F")
G = tlang.Terminal("g") / tlang.Terminal("G")
H = tlang.Terminal("h") / tlang.Terminal("H")
I = tlang.Terminal("i") / tlang.Terminal("I")
J = tlang.Terminal("j") / tlang.Terminal("J")
K = tlang.Terminal("k") / tlang.Terminal("K")
L = tlang.Terminal("l") / tlang.Terminal("L")
M = tlang.Terminal("m") / tlang.Terminal("M")
N = tlang.Terminal("n") / tlang.Terminal("N")
O = tlang.Terminal("o") / tlang.Terminal("O")
P = tlang.Terminal("p") / tlang.Terminal("P")
Q = tlang.Terminal("q") / tlang.Terminal("Q")
R = tlang.Terminal("r") / tlang.Terminal("R")
S = tlang.Terminal("s") / tlang.Terminal("S")
T = tlang.Terminal("t") / tlang.Terminal("T")
U = tlang.Terminal("u") / tlang.Terminal("U")
V = tlang.Terminal("v") / tlang.Terminal("V")
W = tlang.Terminal("w") / tlang.Terminal("W")
X = tlang.Terminal("x") / tlang.Terminal("X")
Y = tlang.Terminal("y") / tlang.Terminal("Y")
Z = tlang.Terminal("z") / tlang.Terminal("Z")

@tlang.contextfree
def EOF(text):
    if text == "":
        yield "", text

skip = tlang.pgreedy(SPACES / MULTILINE_COMMENT / SINGLE_LINE_COMMENT)

lookup = {
    "transaction_name": skip + transaction_name,
    "K_GROUP": skip + K_GROUP,
    "K_RAISE": skip + K_RAISE,
    "any_name": skip + any_name,
    "K_OFFSET": skip + K_OFFSET,
    "K_EXCLUSIVE": skip + K_EXCLUSIVE,
    "module_name": skip + module_name,
    "expr": skip + expr,
    "SCOL": skip + SCOL,
    "STAR": skip + STAR,
    "K_EXCEPT": skip + K_EXCEPT,
    "UNEXPECTED_CHAR": skip + UNEXPECTED_CHAR,
    "with_clause": skip + with_clause,
    "K_TEMPORARY": skip + K_TEMPORARY,
    "K_DEFERRABLE": skip + K_DEFERRABLE,
    "K_NOTNULL": skip + K_NOTNULL,
    "BLOB_LITERAL": skip + BLOB_LITERAL,
    "new_table_name": skip + new_table_name,
    "create_view_stmt": skip + create_view_stmt,
    "K_NATURAL": skip + K_NATURAL,
    "K_ORDER": skip + K_ORDER,
    "J": J,
    "PIPE2": skip + PIPE2,
    "K_INSERT": skip + K_INSERT,
    "K_FOR": skip + K_FOR,
    "CLOSE_PAR": skip + CLOSE_PAR,
    "K_PRIMARY": skip + K_PRIMARY,
    "K_VACUUM": skip + K_VACUUM,
    "K_OF": skip + K_OF,
    "literal_value": skip + literal_value,
    "K_FAIL": skip + K_FAIL,
    "K_DROP": skip + K_DROP,
    "K_SELECT": skip + K_SELECT,
    "GT_EQ": skip + GT_EQ,
    "K_ABORT": skip + K_ABORT,
    "GT2": skip + GT2,
    "K_INTO": skip + K_INTO,
    "drop_table_stmt": skip + drop_table_stmt,
    "K_ELSE": skip + K_ELSE,
    "name": skip + name,
    "Q": Q,
    "K_ASC": skip + K_ASC,
    "O": O,
    "K_SAVEPOINT": skip + K_SAVEPOINT,
    "PIPE": skip + PIPE,
    "K_WITHOUT": skip + K_WITHOUT,
    "K_REGEXP": skip + K_REGEXP,
    "detach_stmt": skip + detach_stmt,
    "K_UPDATE": skip + K_UPDATE,
    "K_FOREIGN": skip + K_FOREIGN,
    "table_or_subquery": skip + table_or_subquery,
    "DIGIT": DIGIT,
    "K_HAVING": skip + K_HAVING,
    "MOD": skip + MOD,
    "I": I,
    "common_table_expression": skip + common_table_expression,
    "K_CROSS": skip + K_CROSS,
    "type_name": skip + type_name,
    "V": V,
    "SPACES": skip + SPACES,
    "delete_stmt_limited": skip + delete_stmt_limited,
    "K_CONFLICT": skip + K_CONFLICT,
    "insert_stmt": skip + insert_stmt,
    "K_COLLATE": skip + K_COLLATE,
    "column_name": skip + column_name,
    "K_SET": skip + K_SET,
    "pragma_name": skip + pragma_name,
    "DOT": skip + DOT,
    "K_ON": skip + K_ON,
    "qualified_table_name": skip + qualified_table_name,
    "ordering_term": skip + ordering_term,
    "MINUS": skip + MINUS,
    "K_LIKE": skip + K_LIKE,
    "signed_number": skip + signed_number,
    "select_core": skip + select_core,
    "AMP": skip + AMP,
    "Y": Y,
    "alter_table_stmt": skip + alter_table_stmt,
    "keyword": skip + keyword,
    "S": S,
    "F": F,
    "DIV": skip + DIV,
    "compound_select_stmt": skip + compound_select_stmt,
    "K_END": skip + K_END,
    "P": P,
    "K_KEY": skip + K_KEY,
    "K_EXPLAIN": skip + K_EXPLAIN,
    "K_REPLACE": skip + K_REPLACE,
    "conflict_clause": skip + conflict_clause,
    "table_constraint": skip + table_constraint,
    "K_CREATE": skip + K_CREATE,
    "K_RENAME": skip + K_RENAME,
    "E": E,
    "K_VIEW": skip + K_VIEW,
    "reindex_stmt": skip + reindex_stmt,
    "K_TO": skip + K_TO,
    "join_clause": skip + join_clause,
    "table_name": skip + table_name,
    "K_AND": skip + K_AND,
    "K_INTERSECT": skip + K_INTERSECT,
    "trigger_name": skip + trigger_name,
    "select_or_values": skip + select_or_values,
    "K_QUERY": skip + K_QUERY,
    "collation_name": skip + collation_name,
    "K_RESTRICT": skip + K_RESTRICT,
    "parse": skip + parse,
    "BIND_PARAMETER": skip + BIND_PARAMETER,
    "K_ROLLBACK": skip + K_ROLLBACK,
    "K_CASCADE": skip + K_CASCADE,
    "join_operator": skip + join_operator,
    "K_DEFAULT": skip + K_DEFAULT,
    "N": N,
    "compound_operator": skip + compound_operator,
    "begin_stmt": skip + begin_stmt,
    "LT": skip + LT,
    "commit_stmt": skip + commit_stmt,
    "K_FULL": skip + K_FULL,
    "STRING_LITERAL": skip + STRING_LITERAL,
    "K_OR": skip + K_OR,
    "K_AFTER": skip + K_AFTER,
    "database_name": skip + database_name,
    "K_DEFERRED": skip + K_DEFERRED,
    "K_WITH": skip + K_WITH,
    "sql_stmt_list": skip + sql_stmt_list,
    "K_BEFORE": skip + K_BEFORE,
    "K_CURRENT_TIME": skip + K_CURRENT_TIME,
    "rollback_stmt": skip + rollback_stmt,
    "K_NULL": skip + K_NULL,
    "EQ": skip + EQ,
    "K_ANALYZE": skip + K_ANALYZE,
    "delete_stmt": skip + delete_stmt,
    "PLUS": skip + PLUS,
    "K_TRIGGER": skip + K_TRIGGER,
    "K_DESC": skip + K_DESC,
    "ASSIGN": skip + ASSIGN,
    "Z": Z,
    "LT2": skip + LT2,
    "K_IN": skip + K_IN,
    "K_ADD": skip + K_ADD,
    "NOT_EQ2": skip + NOT_EQ2,
    "W": W,
    "K_OUTER": skip + K_OUTER,
    "MULTILINE_COMMENT": skip + MULTILINE_COMMENT,
    "K_ACTION": skip + K_ACTION,
    "K_EACH": skip + K_EACH,
    "K_MATCH": skip + K_MATCH,
    "K_REINDEX": skip + K_REINDEX,
    "K_BEGIN": skip + K_BEGIN,
    "X": X,
    "K_INSTEAD": skip + K_INSTEAD,
    "K_INDEX": skip + K_INDEX,
    "K_COMMIT": skip + K_COMMIT,
    "C": C,
    "A": A,
    "K_TEMP": skip + K_TEMP,
    "K_IS": skip + K_IS,
    "K_DETACH": skip + K_DETACH,
    "K_BY": skip + K_BY,
    "attach_stmt": skip + attach_stmt,
    "column_def": skip + column_def,
    "K_ALL": skip + K_ALL,
    "join_constraint": skip + join_constraint,
    "K_AS": skip + K_AS,
    "K_INITIALLY": skip + K_INITIALLY,
    "K_PRAGMA": skip + K_PRAGMA,
    "K_NOT": skip + K_NOT,
    "NUMERIC_LITERAL": skip + NUMERIC_LITERAL,
    "K_ATTACH": skip + K_ATTACH,
    "column_constraint": skip + column_constraint,
    "cte_table_name": skip + cte_table_name,
    "K_RELEASE": skip + K_RELEASE,
    "error_message": skip + error_message,
    "create_trigger_stmt": skip + create_trigger_stmt,
    "index_name": skip + index_name,
    "foreign_table": skip + foreign_table,
    "K_TABLE": skip + K_TABLE,
    "TILDE": skip + TILDE,
    "drop_trigger_stmt": skip + drop_trigger_stmt,
    "K_ROW": skip + K_ROW,
    "L": L,
    "G": G,
    "K_PLAN": skip + K_PLAN,
    "drop_index_stmt": skip + drop_index_stmt,
    "K_RIGHT": skip + K_RIGHT,
    "K_JOIN": skip + K_JOIN,
    "GT": skip + GT,
    "OPEN_PAR": skip + OPEN_PAR,
    "pragma_stmt": skip + pragma_stmt,
    "K_INNER": skip + K_INNER,
    "release_stmt": skip + release_stmt,
    "sql_stmt": skip + sql_stmt,
    "LT_EQ": skip + LT_EQ,
    "vacuum_stmt": skip + vacuum_stmt,
    "K_ESCAPE": skip + K_ESCAPE,
    "savepoint_stmt": skip + savepoint_stmt,
    "unary_operator": skip + unary_operator,
    "K_CURRENT_DATE": skip + K_CURRENT_DATE,
    "K_CHECK": skip + K_CHECK,
    "update_stmt": skip + update_stmt,
    "K_AUTOINCREMENT": skip + K_AUTOINCREMENT,
    "K_NO": skip + K_NO,
    "K_THEN": skip + K_THEN,
    "simple_select_stmt": skip + simple_select_stmt,
    "K_IMMEDIATE": skip + K_IMMEDIATE,
    "K_EXISTS": skip + K_EXISTS,
    "K_DISTINCT": skip + K_DISTINCT,
    "D": D,
    "IDENTIFIER": skip + IDENTIFIER,
    "K_CONSTRAINT": skip + K_CONSTRAINT,
    "M": M,
    "K_INDEXED": skip + K_INDEXED,
    "K_USING": skip + K_USING,
    "K": K,
    "H": H,
    "K_LEFT": skip + K_LEFT,
    "K_WHEN": skip + K_WHEN,
    "column_alias": skip + column_alias,
    "function_name": skip + function_name,
    "K_RECURSIVE": skip + K_RECURSIVE,
    "K_TRANSACTION": skip + K_TRANSACTION,
    "K_WHERE": skip + K_WHERE,
    "K_ALTER": skip + K_ALTER,
    "raise_function": skip + raise_function,
    "R": R,
    "K_VIRTUAL": skip + K_VIRTUAL,
    "U": U,
    "error": skip + error,
    "K_BETWEEN": skip + K_BETWEEN,
    "table_alias": skip + table_alias,
    "K_LIMIT": skip + K_LIMIT,
    "create_index_stmt": skip + create_index_stmt,
    "pragma_value": skip + pragma_value,
    "K_VALUES": skip + K_VALUES,
    "B": B,
    "foreign_key_clause": skip + foreign_key_clause,
    "K_GLOB": skip + K_GLOB,
    "module_argument": skip + module_argument,
    "K_CURRENT_TIMESTAMP": skip + K_CURRENT_TIMESTAMP,
    "SINGLE_LINE_COMMENT": skip + SINGLE_LINE_COMMENT,
    "K_UNION": skip + K_UNION,
    "NOT_EQ1": skip + NOT_EQ1,
    "K_FROM": skip + K_FROM,
    "factored_select_stmt": skip + factored_select_stmt,
    "K_UNIQUE": skip + K_UNIQUE,
    "create_table_stmt": skip + create_table_stmt,
    "analyze_stmt": skip + analyze_stmt,
    "K_IF": skip + K_IF,
    "select_stmt": skip + select_stmt,
    "savepoint_name": skip + savepoint_name,
    "K_DELETE": skip + K_DELETE,
    "update_stmt_limited": skip + update_stmt_limited,
    "view_name": skip + view_name,
    "COMMA": skip + COMMA,
    "K_CAST": skip + K_CAST,
    "T": T,
    "K_COLUMN": skip + K_COLUMN,
    "K_IGNORE": skip + K_IGNORE,
    "create_virtual_table_stmt": skip + create_virtual_table_stmt,
    "drop_view_stmt": skip + drop_view_stmt,
    "K_CASE": skip + K_CASE,
    "K_ISNULL": skip + K_ISNULL,
    "result_column": skip + result_column,
    "K_REFERENCES": skip + K_REFERENCES,
    "table_or_index_name": skip + table_or_index_name,
    "K_DATABASE": skip + K_DATABASE,
    "indexed_column": skip + indexed_column,
    "EOF": EOF
}
lookup["UNEXPECTED_CHAR"] = tlang.nope

globals().update(tlang.stitch(lookup))
assert list(parse.run("select * from schema.table;")) == [
    "select * from schema.table;"
]
