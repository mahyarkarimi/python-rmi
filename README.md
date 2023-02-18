# Simple implementation of RMI api of Java in Python

This project is a simple copy of remote method invocation api of Java programming language written in python. it mimics the basic functionality of creating remote registry of objects at server to obtain on client.

## Basic usage

### Server

```python
from rmi import LocateRegistry, UnicastRemoteObject
import time

class MyMath():
    def sum(self, *num):
        return sum(num)


if __name__ == '__main__':
    registry = LocateRegistry.create_registry(port=1099)
    my_math_stub = UnicastRemoteObject.export_object(MyMath())
    registry.rebind(my_math_stub, "math")
    print('list of remote object names in registry:', registry.list())
```

### Client

```python
from rmi import LocateRegistry

if __name__ == "__main__":
    registry = LocateRegistry.get_registry("10.0.75.1", 1099)
    my_math = registry.lookup("math")
    print('sum of [1,2,3] is ', my_math.sum(1, 2, 3))
```
