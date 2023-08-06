from .array_operation import array_operation
from .dataframe_operation import dataframe_operation
from .datetime_operation import datetime_operation
from .dict_operation import dict_operation
from .faker_ops import faker_ops
from .file_operation import file_operation
from .fmus_ops import fmus_ops
from .gui_operation import gui_operation
from .number_operation import float_operation, int_operation
from .orm_operation import orm_operation
from .react_operation import react_operation
from .redis_operation import redis_operation
from .set_operation import set_operation
from .stdout_operation import stdout_operation
from .string_operation import string_operation
from .tuple_operation import pair_operation, tuple_operation

dataops_statement = f"""
// yg mengambil operation ini bisa dari 'instance'
// tgl:d, tgl<penanda><operation>
// jadi penanda ini menentukan adanya pemanggilan dataops
// pengennya spt ini:
// parse waktu dari string: mystr~s/strp()
// read file monyong.txt dan simpan content di mymonkey: myfd~F/read/mymonkey
// grpc: construct message xxx dan service xxx, lalu listen for conn
// tcp ... http ... dst.
// selain itu ada: option/config, misal rest request dg axios/fetch/...

// sebaiknya: operasi kita masukkan ke file text saja
// biar bisa berubah2 dan menghindari kompleksitas grammar

penanda: "?"

// identifier?A/operation.../config1,config2...(param)
// mymodel?O/create(id=1,name='usef')
// mymodel?O/create/opt1=x, opt2=y, opt3=z/(id=1,name='usef')
// config hrs berisi: nama var/identifier utk digunakan, nama operasi yg dipilih

// sementara: tanpa config dan call param ()
//dataops_statement: data_operation operation_config? function_call_param?
dataops_statement: data_operation

operation_config: "/" operation_config_items "/"
operation_config_items: operation_config_item ("," operation_config_item)*
operation_config_item: "c"

{stdout_operation}

{faker_ops}

{fmus_ops}

data_operation: array_operation     // ?A
  | dict_operation                  // ?D
  | pair_operation                  // ?P
  | set_operation                   // ?S
  | tuple_operation                 // ?L
  | string_operation                // ?s
  | bool_operation                  // ?b
  | char_operation                  // ?b
  | datetime_operation              // ?d
  | float_operation                 // ?f
  | int_operation                   // ?i
  | void_operation                  // ?v

  | dataframe_operation             // ?#  
  | directory_operation             // ?I
  | file_operation                  // ?F
  | gui_operation                   // ?u
  | network_operation               // ?N
  | orm_operation                   // ?O
  | react_operation                 // ?@
  | stdin_operation                 // ?-
  | stream_operation                // ?st
  | test_operation                  // ?t
// gui operation, react operation, ...

{array_operation}

// all crud utk array
// map, filter, reduce, fold, foldMap, ...

{dataframe_operation}

{dict_operation}

directory_operation:    penanda "I" directory_operation_choice
directory_operation_choice: "h" -> hello

{file_operation}

network_operation:      penanda "N" network_operation_choice
network_operation_choice: "h" -> hello

{orm_operation}

{redis_operation}

{set_operation}

stdin_operation:        penanda "-" stdin_operation_choice
stdin_operation_choice: expression_item -> input // data?-<masukkan data>

stream_operation:         penanda "R" stream_operation_choice
stream_operation_choice: "h" -> hello

test_operation:         penanda "t" test_operation_choice
// utk tdd
test_operation_choice: "h" -> hello

{pair_operation}

{tuple_operation}

{string_operation}

// primitive non-string
// b2i, b2s
bool_operation:         penanda "b" bool_operation_choice
bool_operation_choice: "h" -> hello

// c2s
char_operation:         penanda "c" char_operation_choice
char_operation_choice: "h" -> hello

{datetime_operation}

{float_operation}

{int_operation}

void_operation:         penanda "v" void_operation_choice
// tmsk utk object dan any, null, undefined
void_operation_choice: "h" -> hello

{gui_operation}

{react_operation}
"""
