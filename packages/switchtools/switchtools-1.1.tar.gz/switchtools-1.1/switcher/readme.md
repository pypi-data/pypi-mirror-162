SwitchTools - Library for switch-case on python
-----------------------------------------------
Using Switch And Case
```python
from switchtools import *
Switch("Value",[
	Case("CaseValue",lambda:print("test"))
])
```
Using Switch And Case with lambda args
```python
from switchtools import *
Switch("Value",[
	Case("CaseValue",lambda x:print(f"test {x}"),[10])
])
```
Using Switch And Case with default
```python
from switchtools import *
Switch("Value",[
	Case("CaseValue",lambda x:print(f"test {x}"),[10]),
	Case("default",lambda:print(f"default"))
])
```
And Switch And Case can working with class
