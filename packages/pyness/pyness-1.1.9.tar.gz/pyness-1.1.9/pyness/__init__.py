import time
import random
from colored import fg,bg,attr

def key(size,number=True,upper=True,symbol=True,lower=True):
    key = gen(size, number,upper,symbol,lower)
    print(key)
    return key

def fps():
    start_time = time.time()
    time.sleep(0.0001)
    fps = f"{1.0 / (time.time() - start_time)}"[:2]
    return fps

#-------------------------------------------------------------------------------------------------------------------
def convert_str_in_list(string):
    list1=[]
    list1[:0]=string
    return list1
def math(size, number,upper,symbol,lower):

    if number == True or False:
        a = 0
    else:
        a = number
    if upper == True or False:
        b = 0
    else:
        b = upper
    if symbol == True or False:
        c = 0
    else:
        c = symbol
    if lower == True or False:
        d = 0
    else:
        d = lower

    count = size - a - b - c - d
    return count

def __gen__(size, number,upper,symbol,lower):
    The_key = []
    TYPE = [type(size),type(number),type(upper),type(symbol),type(lower)]

    A_1       =     [int, list,bool,bool,bool]
    A_2       =     [int, bool,list,bool,bool]
    A_3       =     [int, bool,bool,list,bool]
    A_4       =     [int, bool,bool,bool,list]
    A_1_2     =     [int, list,list,bool,bool]
    A_1_3     =     [int, list,bool,list,bool]
    A_1_4     =     [int, list,bool,bool,list]
    A_2_3     =     [int, bool,list,list,bool]
    A_2_4     =     [int, bool,list,bool,list]
    A_3_4     =     [int, bool,bool,list,list]
    A_1_2_3   =     [int,list,list,list,bool]
    A_1_3_4   =     [int,list,bool,list,list]
    A_2_3_4   =     [int, bool,list,list,list]
    A_1_2_4   =     [int, list,list,bool,list]
    A_1_2_3_4 =     [int,list,list,list,list]
    A         =     [int, bool,bool,bool,bool]

    if A == TYPE:
        c = []
        return c
    if A_1_3_4 == TYPE:
        for i in range(0,size):
            shuff = [random.choice(number),random.choice(symbol),random.choice(lower)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_1_2_3 == TYPE:
        for i in range(0,size):
            shuff = [random.choice(number),random.choice(upper),random.choice(symbol)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_2_3_4 == TYPE:
        for i in range(0,size):
            shuff = [random.choice(symbol),random.choice(upper),random.choice(lower)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_1_2_4 == TYPE:
        for i in range(0,size):
            shuff = [random.choice(number), random.choice(upper),random.choice(lower)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_1_2_3_4 == TYPE:
        for i in range(0, size):
            shuff = [random.choice(number), random.choice(upper), random.choice(symbol), random.choice(lower)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_1_2 == TYPE:
        for i in range(0, size):
            shuff = [random.choice(number), random.choice(upper)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_1_3 == TYPE:
        for i in range(0, size):
            shuff = [random.choice(number), random.choice(symbol)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_1_4 == TYPE:
        for i in range(0, size):
            shuff = [random.choice(number), random.choice(lower)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_2_3 == TYPE:
        for i in range(0, size):
            shuff = [random.choice(upper), random.choice(symbol)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_2_4 == TYPE:
        for i in range(0, size):
            shuff = [random.choice(upper), random.choice(lower)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_3_4 == TYPE:
        for i in range(0, size):
            shuff = [random.choice(symbol), random.choice(lower)]
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_1 == TYPE:
        for i in range(0, size):
            shuff = random.choice(number)
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_2 == TYPE:
        for i in range(0, size):
            shuff = random.choice(upper)
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_3 == TYPE:
        for i in range(0, size):
            shuff = random.choice(symbol)
            c = random.choice(shuff)
            The_key.append(c)
        return The_key
    if A_4 == TYPE:
        for i in range(0, size):
            shuff = random.choice(lower)
            c = random.choice(shuff)
            The_key.append(c)
        return The_key


def gen(size, number,upper,symbol,lower,strong=False,split=(5,"-"),update=False):
    if update == True:
        print ('%s%s[]-In next update there will be new parameters call strong and split%s' % (fg('black'), bg('white'), attr('reset')))
    size = math(size, number,upper,symbol,lower)
    if size < 0:
        raise ValueError("can not be negative number")
    _number_ = []
    _upper_ =  []
    _symbol_ = []
    _lower_ =  []
    if type(number) == int:
        if number == 1:
            number = 2
            raise ValueError("Can not be 1 or -1")
        numbers = '1234567890'
        _number_ = random.choices(numbers, k = number)
        number = False
    if type(upper) == int:
        if upper == 1:
            upper = 2
            raise ValueError("Can not be 1 or -1")
        uppers = 'QWERTYUIOPASDFGHJKLZXCVBNM'
        _upper_ = random.choices(uppers, k = upper)
        upper = False
    if type(symbol) == int:
        if symbol == 1:
            symbol = 2
            raise ValueError("Can not be 1 or -1")
        symbols = '@#$%&!'
        _symbol_ = random.choices(symbols, k = symbol)
        symbol = False
    if type(lower) == int:
        if lower == 1:
            lower = 2
            raise ValueError("Can not be 1 or -1")
        lowers = 'qwertyuiopasdfghjklzxcvbnm'
        _lower_ = random.choices(lowers, k = lower)
        lower = False

    if number == True:
        number = '1234567890'
        number = convert_str_in_list(number)
    if upper == True:
        upper = 'QWERTYUIOPASDFGHJKLZXCVBNM'
        upper = convert_str_in_list(upper)
    if symbol == True:
        symbol = '@#$%&!'
        symbol = convert_str_in_list(symbol)
    if lower == True:
        lower = 'qwertyuiopasdfghjklzxcvbnm'
        lower = convert_str_in_list(lower)

    key = __gen__(size,number,upper,symbol,lower)
    key = key + _upper_ + _number_ + _symbol_ + _lower_
    random.shuffle(key)
    key=''.join([str(x) for x in key])
    return key