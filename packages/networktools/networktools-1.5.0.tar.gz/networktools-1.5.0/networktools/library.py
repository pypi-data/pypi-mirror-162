import shlex
import ujson as json # type: ignore # pylint: disable=import-error
import datetime
import random
from typing import Dict, Any, List, Callable
from rich import print # type: ignore # pylint: disable=import-error
from itertools import product
from pydantic import validate_arguments, Field
from pydantic.typing import Annotated # type: ignore # pylint: disable=import-error


def all_variants(word: str) -> set:
    word_set = {''.join(x) for x in product(
        *[{c.upper(), c.lower()} for c in word])}
    return word_set


StringChar = Annotated[str, Field(max_length=1)]
StringHex =  Annotated[str, Field(regex="^[0-9a-fA-F]+$")]


@validate_arguments
def random_char() -> StringChar:
    """
    Alphabetic uppercase and number 0 to 9 on a random
    selection
    """
    #symbols = list(range(91,96))+ list(range(123,126))
    nums = list(range(48, 58))
    alfab = list(range(65, 91))
    chars = nums + alfab
    char_num = random.choice(chars)
    return chr(char_num)


@validate_arguments
def my_random_string(string_length: int=10) -> str:
    """Returns a random string of length string_length.

    :param string_length: a positive int value to define the random length
    :return:
    """
    a = 3
    assert string_length >= a, "No es un valor positivo sobre " + str(a)
    rand_list = [random_char() for i in range(string_length)]
    randstr = "".join(rand_list)
    return randstr


@validate_arguments
def set_id(lista: List[str], uin: int=5) -> str:
    """
    Defines a new id for stations, check if exists
    """
    while (ids:=my_random_string(uin)):
        if ids not in lista:
            lista.append(ids)
            break
    return ids

@validate_arguments
def complete_nro(val:str, character: StringChar='0', n: int=3):
    """
    Complete with 0 a number until n chars
    """
    s_val = str(val).upper()
    ln = len(s_val)
    delta = n - ln
    s_out = ''
    for _ in range(delta):
        s_out += character
    s_out += s_val
    return s_out


@validate_arguments
def hextring(value: int) -> StringHex:
    """
    Parse a int to hexadecimal and transfor to string without x part
    """
    return str(hex(value)).split('x')[1]


@validate_arguments
def hextring2int(value: StringHex) -> int:
    """
    The inverse as before, parse a string that is hexadecimal, to int

    """
    return int("0x" + value, 16)



@validate_arguments
def check_type(value:Any, tipo='boolean') -> Any:
    """
    Check if some value is on trues or falses, so
    if the value is in a set, give us the correct boolean

    """
    trues = {'true', 't', 'T',
             'True', 'verdadero',
             '1', 's', 'S', 'Si', 'si', 1, True}
    falses = {'falso', 'false', 'False',
              'f', '0', 'n', 'N', 'No', 'no', '', 0, False, None}
    if tipo == 'int' and tipo.isdigit():
        value = int(value)
    elif tipo == 'boolean':
        if value in trues:
            value = True
        elif value in falses:
            value = False
        else:
            value = False
    elif tipo in {'double', 'float', 'real'}:
        value = float(value)
    return value


@validate_arguments
def reverse_dict(commands:Dict[str, Callable]) -> Dict[str, str]:
    reverse_commands = {give_name(value): key
                        for key, value in commands.items()}
    return reverse_commands


@validate_arguments
def choice_input(choices_dict,
                 type_opt_lambda=lambda x: True,
                 xprint=print):
    """
    For command line, you give a dictionary with options
    and ask to you what of these options you
    need to run, so you can write the keys or the values

    """
    commands = choices_dict
    reverse_commands = reverse_dict(commands)
    options = [f"{key} -> {give_name(value)}"
               for key, value in commands.items()]
    key = ""
    msg_type = type_opt_lambda(None)
    option_nr = 0
    while key not in commands:
        _ = [xprint(option) for option in options]
        option = ''
        try:
            option = input("Choose an option: \n")
        except EOFError as error:
            raise error
        command, key, option_nr = get_command(
            commands,
            reverse_commands,
            option)
    msg_type = type_opt_lambda(option_nr)
    return command, option, msg_type


@validate_arguments
def choice_action(choices_dict,
                  choice,
                  type_opt_lambda=lambda x: True):
    """
    For command line, you give a dictionary with
    options and ask to you what of these options you
    need to run, so you can write the keys or the values

    """
    option = choice
    commands = choices_dict
    reverse_commands = reverse_dict(commands)
    msg_type = type_opt_lambda(None)
    option_nr = 0
    command, _, option_nr = get_command(
        commands,
        reverse_commands,
        option)
    msg_type = type_opt_lambda(option_nr)
    return command, option, msg_type


def get_command(commands, reverse_commands, option):
    """
    Obtain a command from a dict of commands

    """
    option_nr = 0
    if not option:
        option = ""
    if option.isdigit():
        option = int(option)
        if option in commands:
            command = commands.get(option)
            option_nr = option
        else:
            command = 'PRINT'
            option_nr = option
    else:
        # command is the value
        result_k, key, command = multikey(commands, option)
        result_v = False
        if result_k:
            option = key
        else:
            # command is the key
            result_v, key = multivalue(
                reverse_commands, option)
            command = commands.get(key)
            if result_v:
                option = key
        if result_k or result_v:
            option_nr = reverse_commands.get(command)
    return command, option, option_nr


def multikey(commands, key):
    """
    Given an string key, look for the value in commands, if key
    has upper or lower case, consider that.
    """
    result = False
    final_key = key
    command = None
    if key in commands:
        command = commands.get(key)
        result = True
    elif key.lower() in commands:
        final_key = key.lower()
        command = commands.get(final_key)
        result = True
    elif key.upper() in commands:
        final_key = key.upper()
        command = commands.get(final_key)
        result = True
    # here command is the value of the key
    return result, final_key, command


def multivalue(reverse_commands, value):
    """
    Given an string value, look for the key in commands, if value
    has upper or lower case, consider that.
    """
    result = False
    final_value = value
    key = None
    if value in reverse_commands:
        key = reverse_commands.get(value)
        result = True
    elif value.lower() in reverse_commands:
        final_value = value.lower()
        key = reverse_commands.get(final_value)
        result = True
    elif value.upper() in reverse_commands:
        final_value = value.upper()
        key = reverse_commands.get(final_value)
        result = True
    # here command is the key
    return result, key


def give_name(value:Callable) -> str:
    """
    Give the name of the object, if is callable
    (funcion, generator, coroutine, etc) returns name, else
    the string method on the object

    """
    if callable(value):
        return value.__name__
    return str(value)


def fill_pattern(var_list, pattern):
    """
    Replace values in pattern
    var_list has to have 'pattern' and 'value' keys
    pattern is a string with some keys inside
    """
    code = pattern
    for lista in var_list:
        keys = lista.keys()
        # print(lista)
        assert 'pattern' in keys and 'value' \
            in keys, "Lista incorrecta en " + str(lista)
        code = code.replace(lista['pattern'], lista['value'])
    # print(code)
    return code


def pattern_value(pattern_str, val):
    "Return a specific dictionary with keys pattern and value"
    return dict(pattern=pattern_str, value=val)


def key_on_dict(key, diccionario):
    return key in diccionario.keys()

def check_gsof(mydict):
    return key_on_dict('ECEF', mydict) and key_on_dict('POSITION_VCV', mydict)


def gns_dumps(string, char='#'):
    a = json.dumps(string)
    b = a.replace('\"', char)
    q = 3*char
    c = b.replace('\\#', f'${q}')
    return c


def gns_loads(string, char='#'):
    q = 3*char
    a = string.replace(f'${q}', '\\#')
    b = a.replace(char, '\"')
    c = json.loads(b)
    return c


def context_split(value, separator='|'):
    """
    Split and take care of \"\"
    """
    try:
        q = shlex.shlex(value, posix=True)
        q.whitespace += separator
        q.whitespace_split = True
        q.quotes = '\"'
        q_list = list(q)
        return q_list
    except Exception as e:
        print(f"Error en separación de contexto {e}")
        raise e


def geojson2angularjson(content):
    """
    content is a GeoJson object must be
    converted to a Angular Chart JSON object....
    """

    dt = datetime.utcfromtimestamp(int(content['properties']['time'])/1000)


    delta_min = lambda a, b: a-b
    delta_max = lambda a, b: a+b

    dgc_i = lambda e: content['features'][0]['geometry']['coordinates'][e]
    pee = content['properties']['NError']

    new_value = dict(
        source="DataWork",
        station_name=content['properties']['station'],
        timestamp=dt,
        data={
            'N': {
                'value': dgc_i(0),
                'error': pee,
                'min': delta_min(dgc_i(0), pee),
                'max': delta_max(dgc_i(0), pee)
            },
            'E': {
                'value': dgc_i(1),
                'error': pee,
                'min': delta_min(dgc_i(1), pee),
                'max': delta_max(dgc_i(1), pee),

            },
            'U': {
                'value': dgc_i(2),
                'error': pee,
                'min': delta_min(dgc_i(2), pee),
                'max': delta_max(dgc_i(1), pee)
            },
        }
        # last_update=datetime.utcnow()
    )
    return new_value


def geojson2json(content, destiny="plot"):
    """
    content is a GeoJson object must be
    converted to a RethinkDB JSON object....
    """

    try:
        if destiny == 'plot':
            dt_gen = content['properties']['dt_gen'].isoformat()
        else:
            dt_gen = content['properties']['dt_gen']
    except Exception as ex:
        print(f"Error en calcular fecha tiempo {ex}")
        raise ex

    time = content['properties']['time']
    delta_min = lambda a, b: a-b
    delta_max = lambda a, b: a+b

    dgc_i = lambda e: content['features'][0]['geometry']['coordinates'][e]
    pee = content['properties']['NError']

    new_value = dict(
        source="DataWork",
        station=content['properties']['station'],
        dt_gen=dt_gen,
        timestamp=time,
        data={
            'N': {
                'value': dgc_i(0),
                'error': pee,
                'min': delta_min(dgc_i(0), pee),
                'max': delta_max(dgc_i(0), pee)
            },
            'E': {
                'value': dgc_i(1),
                'error': pee,
                'min': delta_min(dgc_i(1), pee),
                'max': delta_max(dgc_i(1), pee),

            },
            'U': {
                'value': dgc_i(2),
                'error': pee,
                'min': delta_min(dgc_i(2), pee),
                'max': delta_max(dgc_i(1), pee)
            },
        }
        # last_update=datetime.utcnow()
    )

    return new_value


def geojson2row(data):
    # fieldnames = ['timestamp', 'E', 'N', 'U',
    #              'EE', 'EN', 'EU', 'NN', 'NU', 'UU']
    result = [
        data.get('timestamp'),
        data.get('data').get('E').get('value'),
        data.get('data').get('N').get('value'),
        data.get('data').get('U').get('value'),
    ]
    return result
