from rmi import LocateRegistry, UnicastRemoteObject

# class Test(UnicastRemoteObject):
#     def add(self, a, b):
#         return a + b

#     def sub(self, a, b):
#         return a - b

from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed

if __name__ == "__main__":
    registry = LocateRegistry.get_registry("10.0.75.1", 1099)
    test = registry.lookup("test")
    e = ThreadPoolExecutor(8)
    test.sum(1, 2, 3)
    futures = []
    futures.append(e.submit(test.sum, *[1,2,3,4,5,6,7,8,9,10]))
    futures.append(e.submit(test.sum, *[1,2,3,4,5,6,7,8,9,10]))
    futures.append(e.submit(test.sum, *[1,2,3,4,5,6,7,8,9,10]))
    futures.append(e.submit(test.sum, *[1,2,3,4,5,6,7,8,9,10]))
    futures.append(e.submit(test.sum, *[1,2,3,4,5,6,7,8,9,10]))
    futures.append(e.submit(test.sum, *[1,2,3,4,5,6,7,8,9,10]))
    futures.append(e.submit(test.sum, *[1,2,3,4,5,6,7,8,9,10]))
    futures.append(e.submit(test.sum, *[1,2,3,4,5,6,7,8,9,10]))
    for f in as_completed(futures):
        print(f.result())
    
