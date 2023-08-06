
# Pyness

A simple module that will cover some necessary work of your project/work.

# Update log
- A Bit slower than before (New)
- keys function has been removed
- key can do the same work as keys

## Install

```bash
  pip install pyness
```


## Deployment

How to get a key :

```python
import pyness
def x():
    x = pyness.key(8) # Put The Number for how many character you want.
    print(x)
def y():
    y = pyness.key(5,number=2,upper=3) # means in your key there will be 2 number and 3 upper character.
    print(y)
def z():
    z = pyness.key(5,upper=2,lower=False,symbol=False,number=True) # means in your key there will be 2 upper character and 3 number
    print(z)

```

Get FPS:
```python
import pyness
def(x):
    while True:
        fps = pyness.FPS()
        # Do something
        print(fps)
```
## Features
- key
- FPS
- Coming Soon

## Next Update:
- freedom to use upper="OUIEW" something like this in your key
- strong key parameter
- split key parameter
- update log parameter
- Bar customizing and making
- github page will be added with code