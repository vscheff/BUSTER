from random import choice, randint
from randfacts import get_fact
from datetime import datetime, timedelta
from pickle import load, dump


def roll_dice(dice):
    try:
        quantity, size = dice.lower().split('d')
        quantity, size = int(quantity), int(size)
    except ValueError:
        return ['Please format your dice in the classic "xDy" style. For example, 1d20 rolls one 20-sided die.']
    if quantity < 1 or size < 1:
        return ['Please use only positive integers for dice quantity and number of sides']
    ret_list = []
    total = 0
    for i in range(quantity):
        roll = randint(1, size)
        total += roll
        ret_list.append(f'Roll #{i+1}: {roll}')
    ret_list.append(f'Total: {total}')
    return ret_list


def rand_choice(elements):
    choices = [i.strip(' <>') for i in elements.split(',') if i]
    return choice(choices)


def rand_num(lower, upper):
    if upper is None:
        lower, upper = 1, lower
    return randint(lower, upper)


def flip():
    return choice(('heads', 'tails'))


def execute(code):
    try:
        compiled = compile(code, '<string>', 'eval')
        return build_string(eval(compiled))
    except SyntaxError as e:
        return f'Bad Syntax: Error occurred at Index [{e.offset-1}], Character ({e.text[e.offset-1]})'
    except Exception as e:
        return str(e)


def build_string(obj):
    if isinstance(obj, (int, float)):
        obj = str(obj)
    elif isinstance(obj, (list, set, tuple)):
        obj = ', '.join([str(i) for i in obj])
    ret_list = []
    while len(obj) >= 2000:
        ret_list.append(obj[:2000])
        obj = obj[2000:]
    ret_list.append(obj)
    return ret_list
