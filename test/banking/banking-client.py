from rmi import LocateRegistry

if __name__ == "__main__":
    registry = LocateRegistry.get_registry("10.0.75.1", 1099)
    account = registry.lookup('account')
    print(account.get_balance(1))
    print(account.get_balance(2))
    # print(account.add_balance(1, 500))
    # time.sleep(1)
    # print(account.get_balance(1))
    print(account.transfer(2, 1, 1000))
    print(account.get_balance(1))
    print(account.get_balance(2))