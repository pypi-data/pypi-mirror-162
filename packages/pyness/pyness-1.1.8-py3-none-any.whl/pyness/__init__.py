import time
import random

global Number,Characters,symbol,small_Characters
Number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
Characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H' 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
symbol = ['@', '#', '$', '%', '&', '!']
small_Characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def key(size,Number=Number,Characters=Characters,symbol=symbol,small_Characters=small_Characters):
    key_ = gen(size, Number,Characters,symbol,small_Characters)
    while True:
        if key_ == False:
            key_ = gen(size, Number,Characters,symbol,small_Characters)
        else:
            break
    return key_

def fps():
    start_time = time.time()
    time.sleep(0.01)
    fps = f"{1.0 / (time.time() - start_time)}"
    return fps

#-------------------------------------------------------------------------------------------------------------------

def gen(size, Number,Characters,symbol,small_Characters):
    The_key = []
    key = ''
    check = size
    inting = False
    string = False
    small_str = False
    symbols = False
    if size >= 4:
        if size >= 100:
            for i in range(0,size):
                shuff = [random.choice(Characters), random.choice(Number), random.choice(small_Characters), random.choice(symbol)]
                random.shuffle(shuff)
                c = random.choice(shuff)
                The_key.append(c)
            key=''.join([str(x) for x in The_key])
            return key
        else:
            for i in range(0,size):
                shuff = [random.choice(Characters), random.choice(Number), random.choice(small_Characters), random.choice(symbol)]
                random.shuffle(shuff)
                c = random.choice(shuff)
                The_key.append(c)
            for k in range(0,size):
                check = check - 1
                if The_key[check] in Number:
                    inting = True
                if The_key[check] in Characters:
                    string = True
                if The_key[check] in small_Characters:
                    small_str = True
                if The_key[check] in symbol:
                    symbols = True
            condition = [inting, string, small_str, symbols]
            checking = all(condition)
            if checking == True:
                key=''.join([str(x) for x in The_key])
                return key
            if checking == False:
                return False
    else:
        shuff = [random.choice(Characters), random.choice(Number), random.choice(small_Characters), random.choice(symbol)]
        random.shuffle(shuff)
        for i in range(0,size):
            check = check - 1
            The_key.append(shuff[check])
        random.shuffle(The_key)
        key=''.join([str(x) for x in The_key])
        return key