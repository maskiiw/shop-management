"""----------------------------------------------------------------------------------------------------
well come, this is maskiiw, this is a simple project about socket programing.
       this file is the clint side of this project.
----------------------------------------------------------------------------------------------------"""
# import what we need:
import socket  # https://docs.python.org/3/library/socket.html
import sqlite3  # https://docs.python.org/3/library/sqlite3.html
import threading  # https://docs.python.org/3/library/threading.html
import traceback  # https://docs.python.org/3/library/traceback.html
# -------------------------------------------------------------------


class Server:

    def __init__(self):
        self.conn_inventory = sqlite3.connect('inventory.db', check_same_thread=False)
        self.cursor_inventory = self.conn_inventory.cursor()
        self.create_inventory_table()

        self.conn_employees = sqlite3.connect('employees.db', check_same_thread=False)
        self.cursor_employees = self.conn_employees.cursor()
        self.create_employees_table()

        self.lock = threading.Lock()

    def create_inventory_table(self):
        self.cursor_inventory.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            quantity INTEGER,
            user_role TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn_inventory.commit()

    def create_employees_table(self):
        self.cursor_employees.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            password TEXT,
            employee_code TEXT,
            label TEXT
        )''')
        self.conn_employees.commit()
        default_employee = ('maskiiw', '132446', '12310098', 'Manager')
        self.cursor_employees.execute(
            'INSERT INTO employees (name, password, employee_code, label) VALUES (?, ?, ?, ?)', default_employee)
        self.conn_employees.commit()

    def handle_client(self, client_socket):
        counter = 0
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    print('Connection closed by client.')
                    return
                print(data.split(','))
                action, *params = data.split(',')
                self.lock.acquire()

                if action == 'login':
                    username, password = params
                    label = self.check_credentials(username, password)
                    client_socket.send(label.encode())
                elif action == 'add_product':
                    self.add_product_to_inventory(*params)
                    client_socket.send('Product added successfully.'.encode())
                elif action == 'view_inventory':
                    self.view_inventory(client_socket)
                elif action == 'generate_invoice':
                    self.generate_invoice(client_socket)
                elif action == 'get_products':
                    self.get_products(client_socket)
                elif action == 'add_employee':
                    self.add_employee_to_database(*params)
                    client_socket.send('Employee added successfully.'.encode())
                elif action == 'view_employees':
                    self.view_employees(client_socket)
                elif action == 'exit':
                    print('User requested to exit. Closing connection.')
                    break
                else:
                    print('Invalid action.')
                self.lock.release()

            except socket.timeout:
                print('Socket timed out. Connection closed.')
                break
            except Exception as e:
                print(traceback.format_exc())
                print(f'Error: {e}')
                counter += 1
                if counter >= 30:
                    break
        client_socket.close()

    def add_product_to_inventory(self, product_name, quantity):
        try:
            quantity = int(quantity)
            self.cursor_inventory.execute('INSERT INTO inventory (product_name, quantity) VALUES (?, ?)',
                                          (product_name, quantity))
            self.conn_inventory.commit()
            print(f'Product {product_name} added successfully.')
        except Exception as e:
            print(f'Error adding product: {e}')

    def view_inventory(self, client_socket):
        self.cursor_inventory.execute('SELECT * FROM inventory')
        inventory_list = self.cursor_inventory.fetchall()
        inventory_str = "\n".join(
            [f"{item[1]}: {item[2]} units (Modified by {item[3]} at {item[4]})" for item in inventory_list])
        client_socket.sendall(inventory_str.encode())

    def generate_invoice(self, client_socket):
        invoice_content = ''
        while True:
            data = client_socket.recv(1024).decode()
            print(data)
            if not data:
                break
            if data == '0':
                break
            invoice_content += data
        invoice_lines = invoice_content.split('\n')
        for line in invoice_lines:
            if line:
                product_name, quantity = line.split(': ')
                self.cursor_inventory.execute('UPDATE inventory SET quantity = quantity - ? WHERE product_name = ?',
                                              (quantity, product_name))
                self.conn_inventory.commit()
        response = 'Invoice processed successfully.'
        client_socket.send(response.encode())

    def get_products(self, client_socket):
        self.cursor_inventory.execute('SELECT product_name, quantity FROM inventory')
        products_list = self.cursor_inventory.fetchall()
        products_str = "\n".join([f"{item[0]}: {item[1]} units" for item in products_list])
        client_socket.sendall(products_str.encode())

    def add_employee_to_database(self, name, password, employee_code, label):
        try:
            self.cursor_employees.execute(
                'INSERT INTO employees (name, password, employee_code, label) VALUES (?, ?, ?, ?)',
                (name, password, employee_code, label))
            self.conn_employees.commit()
            print(f'Employee {name} added successfully.')
        except Exception as e:
            print(f'Error adding employee: {e}')

    def view_employees(self, client_socket):
        self.cursor_employees.execute('SELECT * FROM employees')
        employees_list = self.cursor_employees.fetchall()
        employees_str = "\n".join(
            [f"{item[1]} - {item[3]} - {item[4]}" for item in employees_list])
        client_socket.sendall(employees_str.encode())

    def check_credentials(self, username, password):
        self.cursor_employees.execute('SELECT label FROM employees WHERE name = ? AND password = ?',
                                      (username, password))
        result = self.cursor_employees.fetchone()
        if result:
            return result[0]
        else:
            return 'Invalid credentials'


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.settimeout(1000)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    print('Server is listening for incoming connections...')

    while True:
        client_socket, client_address = server_socket.accept()
        print('Accepted connection from', client_address)
        server = Server()
        threading.Thread(target=server.handle_client, args=(client_socket,)).start()
# ----------------------------------------------------------------------------------
