# ini utk anonymous block dll
# ini cocok utk static block di ts: https://www.typescriptlang.org/docs/handbook/2/classes.html
# static {} dalam class
scope_item = """
// ||//{}

scope_item: keyword_scope scope_config? condition_body
//scope_item: keyword_scope scope_config? scope_content
//scope_content: "{" condition_body "}"

scope_config: "/" scopeconfiglist "/"
scopeconfiglist: scopeconfig ("," scopeconfig)*
scopeconfig: "sc" -> dummy_scope_config

//scope_content: "{" scopecontentlist "}"
//scopecontentlist: scopecontent ("," scopecontent)*
//scopecontent: "s"
//  |
"""
