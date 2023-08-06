# X:(App)
# X:conf1,conf2/(App)
export_item = """
export_item: keyword_export export_config? export_content

// export src/calc.dart, src/music.dart
// export "src/calc.dart"; newline export "src/music.dart"

export_config: exportconfiglist "/"
exportconfiglist: export_config_item+
export_config_item: "d" -> export_default
  | "m" -> export_module    // module.exports = .., correspondingly utk import const .. = require(..)
  | "o" -> export_objectify // export {bla1, bla2, bla3};
export_content: "(" exportcontentlist ")"
exportcontentlist: exportcontent ("," exportcontent)*
exportcontent: HURUF_EXPORT
"""
