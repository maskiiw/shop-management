"""----------------------------------------------------------------------------------------------------
well come, this is maskiiw, this is a simple project about socket programing.
       this file is the clint side of this project.
----------------------------------------------------------------------------------------------------"""
# import what we need:
import socket  # https://docs.python.org/3/library/socket.html
from PIL import Image, ImageDraw, ImageFont  # https://pillow.readthedocs.io/en/stable/
# -------------------------------------------------------------------------------------


class MessageDealer:

    @staticmethod
    def send_msg(self, msg):
        self.client_socket.send(msg.encode())

    @staticmethod
    def receive_msg(self):
        response_from_server = self.client_socket.recv(1024).decode()
        print(response_from_server)
        return response_from_server


class Manager:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 12345))
        self.keep_connection = True

    def display_menu(self):
        print("\nMenu:")
        print("1. View Products")
        print("2. add product")
        print("3. Generate Invoice")
        print("4. view Employees")
        print("5. Add Employee")
        print("6. Exit")

    def choice(self):
        while self.keep_connection:
            self.display_menu()
            choice = input("Enter your choice (1, 2, 3, 4, 5 or 6): ")
            if choice == "1":
                Manager.view_products(self)
            elif choice == "2":
                Manager.add_product_to_inventory_request(self)
            elif choice == "3":
                Manager.generate_invoice(self)
            elif choice == "4":
                Manager.view_employees(self)
            elif choice == "5":
                Manager.add_employee(self)
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5 or 6.")

    @staticmethod
    def view_products(self):
        msg = "view_inventory"
        MessageDealer.send_msg(self, msg)
        return MessageDealer.receive_msg(self)

    @staticmethod
    def add_product_to_inventory_request(self):
        product_name = input("Enter the product name (or 'go back' to go back to the menu): ").lower()
        if product_name == "go back":
            return
        quantity = int(input('Enter the quantity: '))
        msg = f"add_product,{product_name},{quantity}"
        MessageDealer.send_msg(self, msg)
        return MessageDealer.receive_msg(self)

    @staticmethod
    def generate_invoice(self):
        print("\nAvailable Products: ")
        Manager.view_products(self)
        selected_products = []
        while True:
            product_name = input("Enter product name to add to the invoice (or 'done' to finish and 'go back' to go back to the menu): ")
            if product_name == "go back":
                return
            elif product_name == "done":
                msg = "generate_invoice,0"
                MessageDealer.send_msg(self, msg)
                break
            quantity = int(input("Enter quantity: "))
            selected_products.append((product_name, quantity))
        invoice_content = "\n".join([f"{item[0]}: {item[1]}" for item in selected_products])
        msg = f"\n{invoice_content}"
        MessageDealer.send_msg(self, msg)
        data_for_plot = selected_products
        image = Image.open("invoice.png")
        image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        text_color = (100, 100, 100)
        text_position = (25, 263)
        for item in data_for_plot:
            plot_data = f"{item[0]} {item[1]}"
            draw.text(text_position, plot_data, font=font, fill=text_color)
            text_position = (text_position[0], text_position[1] + 22)
        image.save("customer-invoice.jpeg")
        print('Invoice generated successfully:')

    @staticmethod
    def view_employees(self):
        msg = "view_employees"
        MessageDealer.send_msg(self, msg)
        return MessageDealer.receive_msg(self)

    @staticmethod
    def add_employee(self):
        employee_name = input('Enter employee name: ')
        if employee_name == "go back":
            return
        employee_password = input('Enter employee password: ')
        employee_code = input('Enter employee code: ')
        employee_label = input('Enter employee label: ')
        msg = f'add_employee,{employee_name},{employee_password},{employee_code},{employee_label}'
        MessageDealer.send_msg(self, msg)
        return MessageDealer.receive_msg(self)


class Salesperson:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 12345))
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
            choice = input("Enter your choice (1, 2 or 3): ")
            if choice == "1":
                Manager.view_products(self)
            elif choice == "2":
                Manager.generate_invoice(self)
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please enter (1, 2 or 3): ")


class Storekeeper:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 12345))
        self.keep_connection = True

    @staticmethod
    def display_menu():
        print("\nMenu:")
        print("1. view Product")
        print("2. Add Product")
        print("3. Exit")

    def choice(self):
        while self.keep_connection:
            self.display_menu()
            choice = input("Enter your choice (1, 2 or 3): ")
            if choice == "1":
                Manager.view_products(self)
            elif choice == "2":
                Manager.add_product_to_inventory_request(self)
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please enter (1, 2 or 3): ")


class Login:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 12345))
        self.keep_connection = True

    def login_and_get_label(self):
        user_name = input("Enter your username: ")
        password = input("Enter your password: ")
        msg = f"login,{user_name},{password}"
        MessageDealer.send_msg(self, msg)
        return MessageDealer.receive_msg(self)


app = Login()
response = app.login_and_get_label()
if response == "Manager":
    process = Manager()
    process.choice()
elif response == "Salesperson":
    process = Salesperson()
    process.choice()
elif response == "Storekeeper":
    process = Storekeeper()
    process.choice()
else:
    print("invalid name or password")
    exit()
# --------
