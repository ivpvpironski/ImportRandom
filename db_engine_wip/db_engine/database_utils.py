import re
import os
from datetime import datetime
from db_engine import database_select
from db_engine import database_core


def insert(database: database_core.Database, values: list, id_num=None):
    if id_num is None:
        id_num = database.entry_count
    errors = list(check_lengths(database, values))
    if not len(errors) == 0:
        return errors
    else:
        database.db_file.seek(
            database.get_entry_position(id_num)
        )
        values.insert(0, str(id_num).zfill(database_core.id_digits))
        database.db_file.write(
            generate_line_str(database, values)
        )
        if id_num == database.entry_count:
            database.entry_count += 1
        database.db_file.flush()
        os.fsync(database.db_file.fileno())


def check_lengths(database: database_core.Database, input_list: list):
    if not len(input_list) == len(database.colons_types) - 1:
        yield 'Wrong number of arguments!'
    else:
        for colon, value in zip(list(database.colons_types.keys())[1:], input_list):
            length_or_type = database.colons_types.get(colon)
            if length_or_type not in database_core.types_length:
                if len(value) > length_or_type:
                    yield f'Value at {colon} is too long!'
            else:
                if length_or_type == 'date':
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        yield ValueError(f'Incorrect data format at \'{colon}\', should be YYYY-MM-DD')
                elif length_or_type == 'gender':
                    if not re.fullmatch(r'[mfn]', value):
                        yield f'Incorrect value at \'{colon}\', should be m/f/n'
                elif length_or_type == 'course_number':
                    if not re.fullmatch(r'[0-9]{5}', value):
                        yield f'Incorrect value at \'{colon}\', course number should be exactly 5 digits long'


def generate_line_str(database: database_core.Database, values: list):
    line = ''
    for value, length in zip(values, database.colons_types.values()):
        if type(length) is int:
            line += f'{value:~<{length}}'
        else:
            line += value
    return line


def update(database: database_core.Database, updates: dict, id_num: int):
    current = database_select.get_dict(database,
                                       database_select.read_entry(database, id_num))
    current.pop('id')
    current.update(updates)
    insert(database, list(current.values()), id_num)


def delete(database: database_core.Database, id_num):
    update(database, {'is_active': '0'}, id_num)
