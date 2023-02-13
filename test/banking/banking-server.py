from rmi import LocateRegistry, UnicastRemoteObject
import sqlite3

# init database
conn = sqlite3.connect('banking.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS accounts
             (id int primary key, user text, balance real, CONSTRAINT balance_range check(balance >= 0))''')
# Insert a row of data
c.execute("INSERT OR IGNORE INTO accounts VALUES (1,'user1',10000)")
c.execute("INSERT OR IGNORE INTO accounts VALUES (2,'user2',20000)")
# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

class Account():
    def __init__(self):
        super().__init__()


    def get_balance(self, id):
        t = (id,)
        conn = sqlite3.connect('banking.db')
        c = conn.cursor()
        c.execute('SELECT balance FROM accounts WHERE id=?', t)
        return c.fetchone()
    

    def add_balance(self, id, amount):
        try:
            with sqlite3.connect('banking.db') as conn:
                t = (amount, id)
                conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', t)
                conn.commit()
        except sqlite3.Error as e:
            print(e)
        return conn.total_changes


    def transfer(self, sender_id, receiver_id, ammount):
        try:
            with sqlite3.connect('banking.db') as conn:
                conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (ammount, sender_id,))
                conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (ammount, receiver_id,))
                conn.commit()

        except sqlite3.Error as e:
            print(e)
        return conn.total_changes
        
        

if __name__ == "__main__":
    acc = Account()
    stub = UnicastRemoteObject.export_object(acc)
    registry = LocateRegistry.create_registry(1099)
    registry.rebind(stub, "account")
