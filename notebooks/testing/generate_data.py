# Binary(len)    3031303130313031303131  31(ASCII for '1')  30 (ASCII for '0')   4
# Boolean   TRUE FALSE  4
# Date   2022-03-01  1
# DateTime  2022-06-02 10:25:25.0000000  1
# Decimal(prec, scale)   12345.6789 4
# DecimalFloat  12345.6789   4
# Double   12345.6789  4
# hana.BINARY(len)  3031303130313031303131  4
# hana.REAL   20.4   4
# hana.SMALLDECIMAL  10.5   4
# hana.SMALLINT  10   4
# hana.ST_GEOMETRY(srid) LINESTRING(7.0 5.0, 9.0 7.0)  4   POLYGON((6.0 7.0, 10.0 3.0, 10.0 10.0, 6.0 7.0))  4
# hana.ST_POINT(srid)  POINT(10 20) 4
# hana.TINYINT  10     4
# Integer  6    4
# Integer64   128   4
# LargeBinary  3031303130313031303131    4
# LargeString  ABCD1234abcd5671234891011   4
# String(len)  ABCD1234abc   
# Time   10:00:00  1
# Timestamp  2024-03-07 10:00:00.0000000  1
# UUID   12345678-9abc-def0-1234-56789abcdf00   1


import pandas as pd
import string
import random
import uuid
import json

from polygenerator import random_polygon

from datetime import date, timedelta, datetime

def _generate_bin(lower_l=10, upper_l=20):
    return ''.join([str(_) for _ in random.choices([30, 31], k=random.randint(lower_l, upper_l))])


def _generate_str(lower_l=3, upper_l=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(lower_l, upper_l)))

def _generate_decimal(scale=2):
    return round(random.uniform(1, 500), scale)

def _generate_int(lower_l=0, upper_l=100):
    return random.randint(lower_l, upper_l)

def generate_bin(ind):
    """Binary(len)"""
    return _generate_bin(random.randint(6,12), random.randint(15, 20))

def generate_bool(ind):
    """Boolean"""
    return random.choice([True, False])

def generate_date(ind):
    """Date"""
    init_date = date(2015,1,1)
    return str(init_date + timedelta(days=random.randint(1, 2000)))

def generate_date_time(ind):
    """DateTime"""
    init_date = datetime.now()
    return str(init_date - timedelta(days=random.randint(1, 2000), 
                                     hours=random.randint(1, 2000),
                                     minutes=random.randint(1, 2000),
                                     seconds=random.randint(1, 2000)))

def generate_decimal(ind):
    """Decimal(prec, scale)"""
    return _generate_decimal(random.randint(2,5))

def generate_decimal_float(ind):
    """DecimalFloat"""
    return _generate_decimal(random.randint(4,8))

def generate_double(ind):
    """Double"""
    return _generate_decimal(random.randint(8,16))

def generate_hana_bin(ind):
    """hana.BINARY(len)"""
    return _generate_bin(random.randint(6,12), random.randint(15, 20))

def generate_hana_real(ind):
    """hana.REAL"""
    return _generate_decimal(1)

def generate_hana_small_decimal(ind):
    """hana.SMALLDECIMAL"""
    return _generate_decimal(1)

def generate_hana_smallint(ind):
    """hana.SMALLINT"""
    return _generate_int()

def generate_lingstring(ind):
    """hana.ST_GEOMETRY(srid) LINESTRING"""
    x1 = random.randint(-1000, 1000)
    y1 = random.randint(-1000, 1000)
    x2 = random.randint(-1000, 1000)
    y2 = random.randint(-1000, 1000)
    return f"LINESTRING({x1} {y1}, {x2} {y2})"

def generate_polygon(ind):
    """hana.ST_GEOMETRY(srid) POLYGON"""
    polygon = random_polygon(5)
    points_list = []
    for point in polygon:
        points_list.append(f"{point[0]} {point[1]}")
    points_str = ", ".join(points_list)
    return f"POLYGON(({points_str}))"

def generate_hana_st_point(ind):
    """hana.ST_POINT"""
    x = random.randint(-1000, 1000)
    y = random.randint(-1000, 1000)
    return f"POINT({x} {y})"

def generate_tinyint(ind):
    """hana.TINYINT"""
    return _generate_int(0,10)

def generate_interger(ind):
    """Integer"""
    return _generate_int(10,50)

def generate_interger64(ind):
    """Integer64"""
    return _generate_int(128,1024)

def generate_large_bin(ind):
    """LargeBinary"""
    return _generate_bin(random.randint(32, 48), random.randint(48, 128))

def generate_large_str(ind):
    """LargeString"""
    return _generate_str(64, 128)

def generate_str(ind):
    """String(len)"""
    return _generate_str(3, 32)

def generate_time(ind):
    """Time"""
    init_date = datetime.now()
    o_date = init_date - timedelta(days=random.randint(1, 2000), 
                                     hours=random.randint(1, 2000),
                                     minutes=random.randint(1, 2000),
                                     seconds=random.randint(1, 2000))
    return str(o_date.strftime("%H:%M:%S"))

def generate_timestamp(ind):
    """Timestamp"""
    return generate_date_time(ind)

def generate_uuid(ind):
    """UUID"""
    return uuid.uuid4()

def generate_self_increment(ind):
    """index"""
    return ind


def main(column_type_map, columns, total_rows=10):

    data = [{col: column_type_map[col](ind) for col in columns} for ind in range(total_rows)]

    df = pd.DataFrame(data)

    df.to_csv('data.csv', index=False)



if __name__ == '__main__':

    columns = [f"Column_{i}" for i in range(1, 1001)]
    TOTAL_NUM_ROWS = 2500

    repeats_map = [[generate_self_increment],
                   [generate_bin] * 4,
                   [generate_bool] * 4,
                   [generate_date],
                   [generate_date_time],
                   [generate_decimal] * 4,
                   [generate_decimal_float] * 4,
                   [generate_double] * 4,
                   [generate_hana_bin] * 4,
                   [generate_hana_real] * 4,
                   [generate_hana_small_decimal] * 4,
                   [generate_hana_smallint] * 4,
                   [generate_lingstring] * 4,
                   [generate_polygon] * 4,
                   [generate_hana_st_point] * 4,
                   [generate_tinyint] * 4,
                   [generate_interger] * 4,
                   [generate_interger64] * 4,
                   [generate_large_bin] * 4,
                   [generate_large_str] * 4,
                   [generate_time],
                   [generate_timestamp],
                   [generate_uuid]]

    column_type_map_defined = {}
    for ind, fn in enumerate(sum(repeats_map, [])):
        column_type_map_defined[f"Column_{ind+1}"] = fn


    column_type_map_undefined = {col: generate_str for col in columns if col not in column_type_map_defined}

    column_type_map = {**column_type_map_defined, **column_type_map_undefined}
    column_type_desc = {col: fn.__doc__ for col, fn in column_type_map.items()}

    main(column_type_map, columns, total_rows=TOTAL_NUM_ROWS)
    with open("column_type_desc.json", "w+") as fout:
        json.dump(column_type_desc, fout)
