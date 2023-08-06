# ?d//
# yyyy mm dd HH MM SS
datetime_operation = """
datetime_operation:     penanda "d" datetime_operation_config? datetime_operation_choice

datetime_operation_config: "/" datetime_configs "/"
datetime_configs: datetime_config ("," datetime_config)*
datetime_config: "l" -> locale
  | "u" -> utc

// 24-08-78,04:00:00, misal: mydt?dn24-08-78,04:00:00
set_datetime: set_date (pisah_tanggal_waktu set_time)?
set_date: HURUF_DIGIT pisah_tanggal HURUF_DIGIT pisah_tanggal HURUF_DIGIT
set_time: HURUF_DIGIT pisah_waktu HURUF_DIGIT pisah_waktu HURUF_DIGIT

pisah_tanggal_waktu: ","
pisah_tanggal: "-"
pisah_waktu: ":"

datetime_operation_choice: "n" set_datetime? -> now_datetime
  | "n1" set_date? -> now_date // time menjadi 00:00:00
  | "n2" set_time? -> now_time // date menjadi today
  | "dow" -> day_of_week
  | "doy" -> day_of_year
  | "woy" -> week_of_year
  | "y" -> yyyy_year
  | "y1" -> yy_year
  | "m" -> mm_month
  | "m1" -> m_month
  | "d" -> dd_day
  | "d1" -> d_day
  | "h" -> hh_hour_24
  | "h1" -> hh_hour_12
  | "h2" -> h_hour_24
  | "h3" -> h_hour_12
  | "t" -> tt_minute
  | "t1" -> t_minute
  | "s" -> ss_second
  | "s1" -> s_second
  | "es" -> epoch_second
  | "em" -> epoch_millisecond
  | "eu" -> epoch_microsecond
  | "2i" -> to_iso
  | "2s" own_datetime_format? -> to_string // format
  | "4s" set_date -> from_string // parse, ?d4s2021-08-24
  | "+y/" BILBUL -> add_year
  | "+m/" BILBUL -> add_month
  | "+d/" BILBUL -> add_day
  | "+h/" BILBUL -> add_hour
  | "+t/" BILBUL -> add_minute
  | "+s/" BILBUL -> add_second
  | "+z/" BILBUL -> add_millisecond
  | "=y/" BILBUL ("/" BILBUL ("/" BILBUL)?)? -> set_year
  | "=m/" BILBUL -> set_month
  | "=d/" BILBUL -> set_day
  | "=h/" BILBUL -> set_hour
  | "=t/" BILBUL -> set_minute
  | "=s/" BILBUL -> set_second
  | "=z/" BILBUL -> set_millisecond

// | "f=" own_datetime_format
// biar sebebas kita, bisa iso format etc.
own_datetime_format: HURUF_DIGIT
// hrs namai manual: J, Jan, January dan M, Mon, Monday -> m1, m2, m3, d1, d2, d3
"""
