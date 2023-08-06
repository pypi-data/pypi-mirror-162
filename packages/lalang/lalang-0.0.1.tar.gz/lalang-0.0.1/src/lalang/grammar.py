from langutils.langs import base_grammar
from .huruf import huruf
from .item_block import (class_item, exception_item, function_item,
                        interface_item, scope_item)
from .item_export import export_item
from .item_import import import_item
from .item_package import package_item
from .item_statement import statement_item
from .keywords import keywords

from .searchable import searchable
from .zops.dataops import dataops_statement

# from zops.fmus_ops import fmus_ops

# sekarang masih lang
# nanti dukung: library, framework, package manager, docker/kubernetes/cloud/terraform
# juga hrs dukung: name alias = symtab, type alias
bahasa = f"""
program: program_configuration? item_line+

//program_configuration: "/" program_configuration_items "/"
program_configuration: program_configuration_items "/"
program_configuration_items: program_configuration_item ("," program_configuration_item)*
program_configuration_item: language_context
  | library_context
  | framework_context
  | tools_context

language_context: "py" -> py
  | "clj"     -> clj
  | "cpp"     -> cpp
  | "cs"      -> cs
  | "dart"    -> dart
  | "elixir"  -> elixir
  | "erlang"  -> erlang
  | "go"      -> go
  | "hs"      -> hs
  | "java"    -> java  
  | "js"      -> js
  | "kt"      -> kt
  | "php"     -> php
  | "pl"      -> pl
  | "rb"      -> rb
  | "rs"      -> rs
  | "scala"   -> scala
  | "swift"   -> swift
  | "ts"      -> ts
  | "v"       -> v

library_context: "L:" library_items
library_items: library_item ("," library_item)*
library_item: HURUF_DIGIT

framework_context: "F:" framework_items
framework_items: framework_item ("," framework_item)*
framework_item: HURUF_DIGIT

tools_context: "T:" tools_items
tools_items: tools_item ("," tools_item)*
tools_item: HURUF_DIGIT

item_line: item_starter? item item_separator?
item_separator: ";"
  | item_separator_newline+
  |
field_method_separator: "|"
statement_separator: ";"
param_separator: ","

item_starter: item_tab+
item_tab: "\\\\t"
item_separator_newline: "\\\\n"

item: package_item
  | import_item
  | export_item
  | block_item
  | statement_item
  | expression_item
  | declarative_item

{package_item}

{import_item}

{export_item}

block_item: scope_item
  | class_item
  | function_item
  | exception_item
  | interface_item

{scope_item}
{class_item}
{function_item}
{exception_item}
{interface_item}

{dataops_statement}

// statement_item dahului block_item
// agar for()body jadi for_statement bukan fungsi for
{statement_item}

{keywords}

declarative_item: "D"

named_values: named_value ("," named_value)*
named_value: nama_identifier tipe_identifier? "=" nilai_identifier
nilai_identifier: expression_item

// ini bisa expression: pemanggilan fungsi (berarti bisa ada dot dong)
nama_tanpa_dot: HURUF_DIGIT_ONLY
nama_identifier: HURUF_DIGIT
nama_identifier_or_literal: literal
  | nama_identifier

// utk bedakan dg nama_identifier, tipe dibikin wajib di sini
// lihat juga: nama_identifier_with_typeparams
nama_jenis_identifier: nama_identifier tipe_identifier
nama_jenis_identifier_optional: nama_identifier tipe_identifier?

// kita hrs punya bentuk: (satu:i, dua?:f)
nama_jenis_identifier_nullable: nama_identifier "?" tipe_identifier

// string, int, float, bool, char, any/object, void
// tipe_data_collection mendahului tipe_data_buatan spy gak kemakan
tipe_identifier: ":" tipe_data_config? tipe_data_builtin 
  | ":" tipe_data_config? tipe_data_collection
  | ":" tipe_data_config? tipe_data_buatan
  | ":" tipe_data_fungsi
  | ":" type_intersection
  | ":" type_union

// sementara hanya built in?
type_intersection: tipe_data_builtin ("&" tipe_data_builtin)+
type_union: tipe_data_builtin ("|" tipe_data_builtin)+

tipe_data_config: "[" tipe_data_config_items "]"
tipe_data_config_items: tipe_data_config_item ("," tipe_data_config_item)*
// dibungkus dg Promise, Option, Result, dll
// gunakan versi boxing: Integer, String, dll
// extend another type?
// juga utk gunakan subtype, i -> long, f -> double, s -> max length if applicable
tipe_data_config_item: "tdci"

tipe_data_builtin: "s" -> string
  | "i" -> integer    // i32
  | "f" -> float
  | "a" -> any        // kita bikin default: undefined
  | "b" -> boolean
  | "c" -> char
  | "dd" -> double
  | "dt" -> datetime
  | "h" -> short      // i16
  | "l" -> long       // i64
  | "y" -> byte       // ~ i8
  | "v" -> void       // any dan object masuk sini, kita bikin default: null
tipe_data_buatan: nama_identifier

tipe_data_semua: tipe_data_builtin
  | tipe_data_collection
  | tipe_data_fungsi
  | tipe_data_buatan
  | object_type

// name: ^&*[nama_identifier:type/type]
// [nama:s/s], ^[nama:s/s], &[nama:s/s], *[nama:s/s]
//tipe_data_fungsi: tipe_data_fungsi_config? "[" nama_identifier ":" tipe_data_semua "/" tipe_data_semua "]"
// apa perlu condition_body? utk statement list?
// const last = (arr:Array<number) => ...condition body... = return arr[arr.length-1]
// %last=[]...condition body...
tipe_data_fungsi: tipe_data_fungsi_config? type_parameters? "[" paramlist* "/" tipe_data_kembali? "]" condition_body?
tipe_data_kembali: tipe_data_semua
tipe_data_fungsi_config: "^" -> function_type_expression // default
  | "&" -> call_signature
  | "*" -> construct_signature

// (nama_identifier: real_type) => real_type
// function_type_expression: 

// hrs bs specify array of what...
// default = array of any/object
// A, D, DF, I, F, N, O, P, S, L
tipe_data_collection: "A" item_type?  -> array      // As
  | "D" (key_type "," value_type)?    -> dict       // Di,s
  | "DF" row_type "," column_type     -> dataframe  // DFs,s
  | "I"                               -> directory  // I
  | "F" file_type?                    -> file       // Fj
  | "N" network_type?                 -> network    // Ngrpc
  | "O" orm_type?                     -> orm        // Osqal
  | "P" (key_type "," value_type)?    -> pair       // Pi,s
  | "S" item_type?                    -> set        // Ss
  | "L" (item_type ("," item_type)*)? -> tuple      // Li,s,f
  | "O" some_type "," none_type          -> optional
  | "R" ok_type "," err_type             -> result
  | "P" value_type                    -> promise

// T, U, V suka digunakan utk generic, jadi tuple = L

// sementara baru tipe data primitif...
item_type: tipe_data_builtin
  | "/" tipe_data_buatan
key_type: tipe_data_builtin
value_type: tipe_data_builtin
  | "/" tipe_data_buatan
row_type: tipe_data_builtin
column_type: tipe_data_builtin
some_type: tipe_data_builtin
none_type: tipe_data_builtin
ok_type: tipe_data_builtin
err_type: tipe_data_builtin

file_type: "t"    -> file_text
  | "c"           -> file_csv
  | "doc"         -> file_doc
  | "h"           -> file_html
  | "j"           -> file_json
  | "rss"         -> file_rss
  | "xls"         -> file_xls
  | "xml"         -> file_xml
  | "y"           -> file_yaml

network_type: "R" -> network_rest
  | "d"           -> network_database
  | "gql"         -> network_graphql
  | "grpc"        -> network_grpc
  | "h"           -> network_http
  | "k"           -> network_kafka  
  | "m"           -> network_mqtt
  | "rmq"         -> network_rabbitmq
  | "s"           -> network_spark
  | "t"           -> network_tcp
  | "u"           -> network_udp
  | "w"           -> network_websocket

orm_type: "dj"    -> orm_django
  | "p"           -> orm_prisma
  | "sqal"        -> orm_sqlalchemy
  | "torm"        -> orm_typeorm

type_parameters: "<" type_parameter_list ">"
type_parameter_list: type_parameter ("," type_parameter)*
type_parameter: nama_identifier constraint?
  | type_parameters

// tipe data collection sementara diskip di sini
constraint: ":" tipe_data_buatan // <satu:dua> => <satu extends dua>
  | ":" tipe_data_builtin
  | ":" tipe_data_fungsi
  | ":" object_type

object_type: "{{" object_contents* "}}"
object_contents: object_content (statement_separator object_content)*
object_content: nama_identifier tipe_identifier

// aslinya "extends" union/intersection/primary-type | functype | ctortype | typegeneric | stringliteral
// class myclass<T:[name:s/s]>
// class myclass<T:{{length:number}}>
nama_identifier_with_typeparams: nama_identifier type_parameters?

{searchable}

{huruf}

number_literal: DEC_NUMBER | HEX_NUMBER | BIN_NUMBER | OCT_NUMBER | FLOAT_NUMBER | IMAG_NUMBER
//string_literal: STRING | LONG_STRING
// Import terminals from standard library (grammars/python.lark)
//%import python (NAME, COMMENT, STRING, LONG_STRING)
%import python (DEC_NUMBER, HEX_NUMBER, OCT_NUMBER, BIN_NUMBER, FLOAT_NUMBER, IMAG_NUMBER)

{base_grammar}
"""
