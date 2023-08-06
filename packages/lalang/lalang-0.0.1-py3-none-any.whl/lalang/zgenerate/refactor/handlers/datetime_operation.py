from app.treeutils import (anak, beranak, chdata, child, child1, child2,
                           child3, child4, chtoken, data, ispohon, istoken,
                           jumlahanak, sebanyak, token)


def datetime_operation(tree, identifier, language="py"):
    kembali = ""

    for item in anak(tree):
        if data(item) == "datetime_operation_config":
            pass
        elif data(item) == "now_datetime":
            """
            ?dn
            ?dndd-mm-yyyy hh:nn:ss
            ?dnyyyy-mm-dd hh:nn:ss
            """
            if beranak(item):
                setter = child1(item)
                date_fields = []
                time_fields = []
                if data(setter) == "set_datetime":
                    for setx in anak(setter):
                        if data(setx) == "set_date":
                            for cucu in anak(setx):
                                # print('set_date', cucu, 'bertipe:', type(cucu))
                                if istoken(cucu):
                                    cucu = str(cucu)
                                    date_fields.append(cucu)
                        elif data(setx) == "set_time":
                            for cucu in anak(setx):
                                # print('set_time', cucu, 'bertipe:', type(cucu))
                                if istoken(cucu):
                                    cucu = str(cucu)
                                    time_fields.append(cucu)
                datetime_string, date_string, time_string = "", "", ""
                if date_fields:
                    year_first = True
                    if len(date_fields[0]) == 4:
                        year_first = True
                    if len(date_fields[2]) == 4:
                        year_first = False
                    if year_first:
                        date_string = (
                            f"{date_fields[0]}-{date_fields[1]}-{date_fields[2]}"
                        )
                    else:
                        date_string = (
                            f"{date_fields[2]}-{date_fields[1]}-{date_fields[0]}"
                        )
                    datetime_string = date_string
                if time_fields:
                    time_string = f"{time_fields[0]}:{time_fields[1]}:{time_fields[2]}"
                    datetime_string += " " + time_string
                kembali += f'const {identifier} = new Date("{datetime_string}")'
            else:
                kembali += f"const {identifier} = new Date()"
        elif data(item) == "now_date":
            pass
        elif data(item) == "now_time":
            pass
        elif data(item) == "day_of_week":
            kembali += f"{identifier}.getDay()"  # 0 = sunday
        elif data(item) == "day_of_year":
            pass
        elif data(item) == "week_of_year":
            pass
        elif data(item) == "yyyy_year":
            kembali += f"{identifier}.getFullYear()"
        elif data(item) == "yy_year":
            pass
        elif data(item) == "mm_month":
            pass
        elif data(item) == "m_month":
            kembali += f"{identifier}.getMonth()"
        elif data(item) == "dd_day":
            pass
        elif data(item) == "d_day":
            kembali += f"{identifier}.getDate()"
        elif data(item) == "hh_hour_24":
            pass
        elif data(item) == "hh_hour_12":
            pass
        elif data(item) == "h_hour_24":
            kembali += f"{identifier}.getHours()"
        elif data(item) == "h_hour_12":
            pass
        elif data(item) == "tt_minute":
            kembali += (
                f"{identifier}.getMinutes().padStart({identifier}.getMinutes(), 0)"
            )
        elif data(item) == "t_minute":
            kembali += f"{identifier}.getMinutes()"
        elif data(item) == "ss_second":
            kembali += (
                f"{identifier}.getSeconds().padStart({identifier}.getSeconds(), 0)"
            )
        elif data(item) == "s_second":
            kembali += f"{identifier}.getSeconds()"
        elif data(item) == "epoch_second":
            kembali += f"{identifier}.getTime() / 1000"
        elif data(item) == "epoch_millisecond":
            kembali += f"{identifier}.getTime()"
        elif data(item) == "epoch_microsecond":
            kembali += f"{identifier}.getTime() * 1000"
        elif data(item) == "to_iso":
            # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString
            kembali += f"{identifier}.toISOString()"
        elif data(item) == "to_string":
            kembali += f"{identifier}.toString()"
        elif data(item) == "from_string":
            """
            | "4s" set_date -> from_string // parse, ?d4s2021-08-24
            """
            date_fields = []
            year_first = False
            for putih in anak(item):
                if data(putih) == "set_date":
                    for merah in anak(putih):
                        if istoken(merah):
                            merah = str(merah)
                            date_fields.append(merah)
                    year_first = len(date_fields[0]) == 4
            if year_first:
                year, month, date = date_fields
            else:
                date, month, year = date_fields
            from app.datetimeutils import month3

            month = month3[int(month) - 1]  # 3 = March
            datetime_string = f"{month} {date}, {year}"
            kembali += f'const {identifier} = Date.parse("{datetime_string}")'
        elif data(item) == "add_year":
            nilai = token(item)
            kembali += f"{identifier}.setYear({identifier}.getYear() + {nilai});"
        elif data(item) == "add_month":
            nilai = token(item)
            kembali += f"{identifier}.setMonth({identifier}.getMonth() + {nilai});"
        elif data(item) == "add_day":
            # d.setDate(d.getDate() + 50);
            nilai = token(item)
            kembali += f"{identifier}.setDate({identifier}.getDate() + {nilai});"
        elif data(item) == "add_hour":
            nilai = token(item)
            kembali += f"{identifier}.setHours({identifier}.getHours() + {nilai});"
        elif data(item) == "add_minute":
            nilai = token(item)
            kembali += f"{identifier}.setMinutes({identifier}.getMinutes() + {nilai});"
        elif data(item) == "add_second":
            kembali += f"{identifier}.setSeconds({identifier}.getSeconds() + {nilai});"
        elif data(item) == "add_millisecond":
            kembali += f"{identifier}.setMilliseconds({identifier}.getMilliseconds() + {nilai});"
        elif data(item) == "set_year":
            """
            tgl?d=y/1978/08/24 => tgl.setFullYear(1978, 08, 24);
            """
            nilai = token(item)
            if jumlahanak(item) == 3:
                nilai += f", {token(item, 1)}, {token(item, 2)}"
            kembali += f"{identifier}.setFullYear({nilai})"
        elif data(item) == "set_month":
            nilai = token(item)
            kembali += f"{identifier}.setMonth({nilai})"
        elif data(item) == "set_day":
            # d.setDate(d.getDate() + 50);
            nilai = token(item)
            kembali += f"{identifier}.setDate({nilai})"
        elif data(item) == "set_hour":
            nilai = token(item)
            kembali += f"{identifier}.setHours({nilai})"
        elif data(item) == "set_minute":
            nilai = token(item)
            kembali += f"{identifier}.setMinutes({nilai})"
        elif data(item) == "set_second":
            nilai = token(item)
            kembali += f"{identifier}.setSeconds({nilai})"
        elif data(item) == "set_millisecond":
            nilai = token(item)
            kembali += f"{identifier}.setMilliseconds({nilai})"

    if language == "py":
        pass
    elif language == "ts":
        pass
    elif language == "rs":
        pass
    elif language == "java":
        pass
    elif language == "kt":
        pass
    elif language == "go":
        pass
    elif language == "rb":
        pass
    elif language == "v":
        pass
    elif language == "dart":
        pass
    elif language == "cpp":
        pass
    elif language == "cs":
        pass
    elif language == "hs":
        pass
    elif language == "clj":
        pass
    elif language == "scala":
        pass
    elif language == "php":
        pass
    elif language == "swift":
        pass
    elif language == "elixir":
        pass
    elif language == "erlang":
        pass
    return kembali
