# import dart:math as math;
import_item = """
import_item: keyword_import import_config? import_container? import_things
  | keyword_import import_config? searchable

import_config: "/" importconfiglist "]=/"
importconfiglist: importconfig ("," importconfig)*
importconfig: "d" -> import_default // import { ... as default }
  | "m" -> import_module            // const ... = require(..)

// import sys
// from tree_sitter import Language, Parser

// Itempat|(item)
// Itempat|item,item,/item,/item
import_container: HURUF_DIGIT_DOT "|"

import_things: import_thing ("," import_thing)*
  | "(" import_things ")" -> import_things_enclose_all
import_thing: HURUF_EXPORT -> import_thing_default
  | "/" import_thing -> import_thing_enclose
"""
