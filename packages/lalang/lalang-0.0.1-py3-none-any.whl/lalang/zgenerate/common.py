import datetime
import decimal
import enum
import json


class MyJsonify(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, decimal.Decimal):
            # return str(o)
            return float(obj)
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        # elif isinstance(obj, datetime.datetime):
        #     return obj.strftime("%Y-%m-%d %H:%M:%S")
        # elif isinstance(obj, datetime.date):
        #     return obj.strftime("%Y-%m-%d")
        # elif isinstance(obj, numpy.int64):
        #   return int(obj)
        # elif isinstance(obj, numpy.integer):
        #   return int(obj)
        # elif isinstance(obj, numpy.floating):
        #   return float(obj)
        # elif isinstance(obj, numpy.ndarray):
        #   return obj.tolist()
        elif isinstance(obj, enum.Enum):
            return obj.value
        # elif isinstance(obj, bson.objectid.ObjectId):
        #   return str(obj)

        # return super(MyJsonify, self).default(obj)
        return json.JSONEncoder.default(self, obj)


python_enum_info = """
"""

typescript_enum_info = """
"""

go_enum_info = """
https://stackoverflow.com/questions/64178176/how-to-create-an-enum-and-iterate-over-it
https://play.golang.org/p/x4FJFXWPyDT

type Dir int

const (
  NORTH Dir = iota
  NORTHEAST
  EAST
  SOUTHEAST
  SOUTH
  SOUTHWEST
  WEST
  NORTHWEST
)
func (d Dir) Exists() bool {
  switch d {
  case NORTH,
    NORTHEAST,
    EAST,
    SOUTHEAST,
    SOUTH,
    SOUTHWEST,
    WEST,
    NORTHWEST:
    return true
  }
  return false
}

Exists() returns true if the value is presented in enum. 
It allows to iterate over enum in the following way:

for dir := Dir(0); dir.Exists(); dir++ {
  fmt.Println(dir)
}

"""

dart_enum_info = """
print(Status.values); 
[__DAFTAR_NILAI]

Status.values.forEach((v) => print('value: $v, index: ${v.index}'));
__VALUE_INDEX

print('item kedua: ${Status.__KEDUA}, ${Status.__KEDUA.index}'); 
item kedua: Status.__KEDUA, 1 

print('values kedua: ${Status.values[1]}'); 
values kedua: Status.__KEDUA 
"""


def create_dart_enum_info(name, content):
    tpl = dart_enum_info.replace("Status", name)
    tpl = tpl.replace("__KEDUA", content[1])
    daftar_nilai = ", ".join([f"{name}.{item}" for item in content])
    tpl = tpl.replace("__DAFTAR_NILAI", daftar_nilai)
    value_index = "\n".join(
        [f"value: {name}.{item}, index: {index}" for index, item in enumerate(content)]
    )
    tpl = tpl.replace("__VALUE_INDEX", value_index)
    tpl = ["// " + item for item in tpl.splitlines()]
    tpl = "\n".join(tpl) + "\n"
    return tpl


ruby_enum_info = """// array enum
enum status: [
  :available,
  :discontinued,
  :pending
]
// hash enum
enum status: [
  available: 0,
  discontinued: 10,
  pending: 20
]
"""

java_enum_info = """Level myVar = Level.MEDIUM;
switch(myVar) {
  case LOW    : ..
  case MEDIUM : ..
  case HIGH : ..

for (Level myVar : Level.values()) {
  System.out.println(myVar);
}
"""

kotlin_enum_info = """enum class CardType {
  SILVER, GOLD, PLATINUM
}

enum class CardType(val color: String) {
  SILVER("gray"),
  GOLD("yellow"),
  PLATINUM("black")
}
val color = CardType.SILVER.color

val cardType = CardType.valueOf(name.toUpperCase())
for (cardType in CardType.values()) {
  println(cardType.color)
}
companion object {
  fun getCardTypeByName(name: String) = valueOf(name.toUpperCase())
}
val cardType = CardType.getCardTypeByName("SILVER")
"""

rust_struct_template = """
impl Default for __structname {
  fn default() -> __structname {
    __structname {
      __fieldname: __nilai,
    }
  }
}
"""

go_struct_template = """
func new__structname^(__fieldname __fieldtype) *__structname {
  p := __structname{__fieldname: __nilai}
  // p.__fieldname = __nilai
  return &p
}
"""

ruby_struct_template = """
def initialize(__PARAMLIST__)
__FIELDS_INITIALIZER__
end
"""
