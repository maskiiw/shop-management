"""----------------------------------------------------------------------------------------------------
well come, this is maskiiw, this is a simple project about socket programing.
       this file is the clint side of this project.
----------------------------------------------------------------------------------------------------"""
# import what we need:
import socket
from PIL import Image, ImageDraw, ImageFont
# -----------


class Login:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        self.keep_connection = True

    def login_and_get_label(self):
        username = input('Enter your username: ')
        password = input('Enter your password: ')
        message = f'login,{username},{password}'
        self.client_socket.send(message.encode())
        response = self.client_socket.recv(1024).decode()
        print('Server response:', response)
        return response


class Client:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        self.keep_connection = True

    @staticmethod
    def add_product_to_inventory_request(self):
        product_name = input('Enter the product name (or 0 to go back to the menu): ')
        if product_name == '0':
            return
        quantity = input('Enter the quantity: ')
        message = f'add_product,{product_name},{quantity}'
        self.client_socket.send(message.encode())
        response = self.client_socket.recv(1024).decode()
        print('Server response:', response)

    @staticmethod
    def view_products(self):
        self.client_socket.send('view_inventory'.encode())
        response = self.client_socket.recv(1024).decode()
        print('Inventory List:\n', response)
        return response

    @staticmethod
    def generate_invoice(self):
        print("\nAvailable Products:")
        self.client_socket.send(f'view_inventory'.encode())
        response = self.client_socket.recv(1024).decode()
        print('Inventory List:\n', response)
        selected_products = []
        while True:
            product_name = input("Enter product name to add to the invoice (or '0' to finish): ")
            if product_name == '0':
                self.client_socket.send('generate_invoice,0'.encode())
                break
            quantity = int(input("Enter quantity: "))
            print(product_name, quantity)
            selected_products.append((product_name, quantity))
        invoice_content = "\n".join([f"{item[0]}: {item[1]}" for item in selected_products])
        self.client_socket.send(f'\n{invoice_content}'.encode())
        data = selected_products
        im = Image.open("invoice.png")
        im = im.convert('RGB')
        draw = ImageDraw.Draw(im)
        font = ImageFont.load_default()
        text_color = (100, 100, 100)
        text_position = (25, 263)
        for item in data:
            send_data = f"{item[0]} {item[1]}"
            draw.text(text_position, send_data, font=font, fill=text_color)
            text_position = (text_position[0], text_position[1] + 22)
        im.save("customer-invoice.jpeg")

        print('Invoice generated successfully:')

    @staticmethod
    def add_employee(self):
        name = input('Enter employee name: ')
        password = input('Enter employee password: ')
        employee_code = input('Enter employee code: ')
        label = input('Enter employee label: ')
        message = f'add_employee,{name},{password},{employee_code},{label}'
        self.client_socket.send(message.encode())
        response = self.client_socket.recv(1024).decode()
        print('Server response:', response)

    @staticmethod
    def view_employees(self):
        self.client_socket.send('view_employees'.encode())
        response = self.client_socket.recv(1024).decode()
        print('Employees List:\n', response)
        return response


class Manager:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        self.keep_connection = True

    @staticmethod
    def display_menu():
        print("\nMenu:")
        print("1. Add Product")
        print("2. View Products")
        print("3. Generate Invoice")
        print("4. Add Employee")
        print("5. View Employees")
        print("6. Exit")

    def choice(self):
        while self.keep_connection:
            self.display_menu()
            choice = input('Enter your choice (1, 2, 3, 4, 5 or 6): ')
            if choice == '1':
                Client.add_product_to_inventory_request(self)
            elif choice == '2':
                Client.view_products(self)
            elif choice == '3':
                Client.generate_invoice(self)
            elif choice == '4':
                Client.add_employee(self)
            elif choice == '5':
                Client.view_employees(self)
            elif choice == '6':
                break
            else:
                print('Invalid choice. Please enter 1, 2, 3, 4, 5 or 6.')


class Salesperson:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        self.keep_connection = True

    @staticmethod
    def display_menu():
        print("\nMenu:")
        print("1. View Products")
        print("2. Generate Invoice")
        print("3. Exit")

    def choice(self):
        while self.keep_connection:
            self.display_menu()
            choice = input('Enter your choice (1, 2 or 3): ')
            if choice == '1':
                Client.view_products(self)
            elif choice == '2':
                Client.generate_invoice(self)
            elif choice == '3':
                break
            else:
                print('Invalid choice. Please enter (1, 2 or 3): ')


class Storekeeper:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        self.keep_connection = True

    @staticmethod
    def display_menu():
        print("\nMenu:")
        print("1. Add Product")
        print("2. View Products")
        print("3. Exit")

    def choice(self):
        while self.keep_connection:
            self.display_menu()
            choice = input('Enter your choice (1, 2 or 3): ')
            if choice == '1':
                Client.add_product_to_inventory_request(self)
            elif choice == '2':
                Client.view_products(self)
            elif choice == '3':
                break
            else:
                print('Invalid choice. Please enter (1, 2 or 3): ')


app = Login()
response = app.login_and_get_label()
if response == "Manager":
    prosess = Manager()
    prosess.choice()
elif response == "Salesperson":
    prosess = Salesperson()
    prosess.choice()
elif response == "Storekeeper":
    prosess = Storekeeper()
    prosess.choice()
else:
    print("invalid name or password")
    exit()
# --------
