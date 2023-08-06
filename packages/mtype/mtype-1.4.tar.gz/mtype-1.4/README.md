# MType
## _The easiest way to check the type of something in python_


[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://pypi.org/project/mtype/)

How to Install:
``` pip install mtype ```

How to use:
``` 
>>> from mtype import match
>>> match("Hello World", str)
True 
>>> match("Hello World", str, True)
example.py: ERROR: 'Hello World' is String: True
True 
>>> match("Hello World", int)
False
>>> match("Hello World", int, True)
example.py: ERROR: 'Hello World' is Integer: False
False
```

Parameter:
- Value
- Data Type
- Debug Output