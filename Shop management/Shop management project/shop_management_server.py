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
        self.conn_inventory = sqlite3.connect("inventory.db", check_same_thread=False)
        self.cursor_inventory = self.conn_inventory.cursor()
        self.create_inventory_table()
        self.conn_employees = sqlite3.connect("employees.db", check_same_thread=False)
        self.cursor_employees = self.conn_employees.cursor()
        self.create_employees_table()
        self.lock_inventory = threading.Lock()
        self.lock_employees = threading.Lock()

    def create_inventory_table(self):
        self.cursor_inventory.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            quantity INTEGER,
            user_role TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
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
        default_employee = ("maskiiw", "132446", "12310098", "Manager")
        self.cursor_employees.execute(
            "SELECT * FROM employees WHERE name = ? AND password = ? AND employee_code = ? AND label = ?",
            default_employee)
        existing_employee = self.cursor_employees.fetchone()
        if not existing_employee:
            self.cursor_employees.execute(
                "INSERT INTO employees (name, password, employee_code, label) VALUES (?, ?, ?, ?)", default_employee)
            self.conn_employees.commit()
            print("Default employee added successfully.")
        else:
            print("Default employee already exists.")

    def add_product_to_inventory(self, product_name, quantity):
        try:
            with self.conn_inventory:
                self.cursor_inventory.execute("INSERT INTO inventory (product_name, quantity) VALUES (?, ?)", (product_name, quantity))
            print(f"Product {product_name} added successfully.")
        except Exception as e:
            print(f"Error adding product: {e}")

    def view_inventory(self, client_socket_rev):
        with self.conn_inventory:
            self.cursor_inventory.execute('SELECT * FROM inventory')
            inventory_list = self.cursor_inventory.fetchall()
            inventory_str = "\n".join(
                [f"{item[1]}: {item[2]} units (Modified by {item[3]} at {item[4]})" for item in inventory_list])
            client_socket_rev.sendall(inventory_str.encode())

    def generate_invoice(self, client_socket_rev):
        invoice_content = ""
        while True:
            data = client_socket_rev.recv(1024).decode()
            if not data:
                break
            if data == "0":
                break
            invoice_content += data
        invoice_lines = invoice_content.split('\n')
        for line in invoice_lines:
            if line:
                product_name, quantity = line.split(": ")
                with self.conn_inventory:
                    self.cursor_inventory.execute("UPDATE inventory SET quantity = quantity - ? WHERE product_name = ?", (quantity, product_name))
        response = "Invoice processed successfully."
        client_socket_rev.send(response.encode())

    def add_employee_to_database(self, name, password, employee_code, label):
        try:
            if label == "Manager":
                with self.conn_employees:
                    self.cursor_employees.execute(
                        "SELECT COUNT(*) FROM employees WHERE label = 'Manager'")
                    manager_count = self.cursor_employees.fetchone()[0]
                    manager_count = int(manager_count)
                    if manager_count > 1:
                        msg = "you got full limit of Manager."
                        return msg
                    else:
                        with self.conn_employees:
                            self.cursor_employees.execute(
                                "INSERT INTO employees (name, password, employee_code, label) VALUES (?, ?, ?, ?)",
                                (name, password, employee_code, label))
                        msg = f"Employee {name} added successfully."
                        return msg
            else:
                with self.conn_employees:
                    self.cursor_employees.execute(
                        "INSERT INTO employees (name, password, employee_code, label) VALUES (?, ?, ?, ?)",
                        (name, password, employee_code, label))
                msg = f"Employee {name} added successfully."
                return msg
        except Exception as e:
            print(f"Error adding employee: {e}")

    def view_employees(self, client_socket_rev):
        with self.conn_employees:
            self.cursor_employees.execute("SELECT * FROM employees")
            employees_list = self.cursor_employees.fetchall()
            employees_str = "\n".join(
                [f"{item[1]} - {item[3]} - {item[4]}" for item in employees_list])
            client_socket_rev.sendall(employees_str.encode())

    def check_credentials(self, username, password):
        with self.conn_employees:
            self.cursor_employees.execute("SELECT label FROM employees WHERE name = ? AND password = ?", (username, password))
            result = self.cursor_employees.fetchone()
            if result:
                return result[0]
            else:
                return "Invalid credentials"

    def handle_client(self, client_socket_rev):
        counter = 0
        while True:
            try:
                data = client_socket_rev.recv(1024).decode()
                if not data:
                    print("Connection closed by client.")
                    return
                print(data.split(","))
                action, *params = data.split(",")

                if action == "login":
                    username, password = params
                    label = self.check_credentials(username, password)
                    client_socket_rev.send(label.encode())
                elif action == "add_product":
                    with self.lock_inventory:
                        self.add_product_to_inventory(*params)
                    client_socket_rev.send("Product added successfully.".encode())
                elif action == "view_inventory":
                    with self.lock_inventory:
                        self.view_inventory(client_socket_rev)
                elif action == "generate_invoice":
                    with self.lock_inventory:
                        self.generate_invoice(client_socket_rev)
                elif action == "add_employee":
                    with self.lock_employees:
                        result = self.add_employee_to_database(*params)
                    client_socket_rev.send(result.encode())
                elif action == "view_employees":
                    with self.lock_employees:
                        self.view_employees(client_socket_rev)
                elif action == "exit":
                    print("User requested to exit. Closing connection.")
                    break
                else:
                    print("Invalid action")

            except socket.timeout:
                print("Socket timed out. Connection closed.")
                break
            except Exception as e:
                print(traceback.format_exc())
                print(f"Error: {e}")
                counter += 1
                if counter >= 30:
                    break
        client_socket_rev.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.settimeout(1000)
    server_socket.bind(("localhost", 12345))
    server_socket.listen(1)
    print("Server is listening for incoming connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from", client_address)
        server = Server()
        threading.Thread(target=server.handle_client, args=(client_socket,)).start()
# ----------------------------------------------------------------------------------
