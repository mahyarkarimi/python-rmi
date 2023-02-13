from rmi import LocateRegistry, UnicastRemoteObject
import time

class Test():
    def add(self, a, b):
        return a + b

    def sum(self, *num):
        time.sleep(5)
        return sum(num)

    def sub(self, a, b):
        return a - b


if __name__ == '__main__':
    registry = LocateRegistry.create_registry(port=1099)
    test_stub = UnicastRemoteObject.export_object(Test())
    registry.rebind(test_stub, "test")
    print('list:', registry.list())
