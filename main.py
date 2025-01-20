import tkinter as tk
import mysql.connector
from log import logger
import re

App = None

class RegexPattern:
    @staticmethod
    def check_number(number: str) -> bool:
        if not isinstance(number, str):
            return False
        regex_pattern = re.compile(r"^\+7[0-9]{10}$")
        return regex_pattern.match(number) is not None

    @staticmethod
    def check_int(raw_int: str) -> int | None:
        if not isinstance(raw_int, str):
            return None
        try:
            value = int(raw_int)
            if 0 <= value <= 4294967296:
                return value
            else:
                return None
        except ValueError:
            logger.error("Error checking id")
            return None

class MySQLConnector:
    def __init__(self, connection = None):
        self._admin_number = '+000'
        self._usernames = ('admin', 'user')

        if connection is not None and isinstance(connection, MySQLConnector):
            self._connection = connection._connection
            self._cursor = connection._cursor
            self._current_user = connection._current_user
        else:
            self._connection = self._cursor = self._current_user = None

    def to_connect(self, number: str) -> bool:
        if self._connection is not None:
            logger.error("Connection already is set up")
            return False
        try:
            if number == self._admin_number:
                self._connection = mysql.connector.connect(
                    host='localhost',
                    user=self._usernames[0],
                    password='',
                    database='Transportations'
                )
                self._current_user = self._usernames[0]
            else:
                self._connection = mysql.connector.connect(
                    host='localhost',
                    user=self._usernames[1],
                    password='',
                    database='Transportations'
                )
                self._current_user = self._usernames[1]
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        else:
            logger.info(f"Connected to MySQL by {self._current_user}")
            self._cursor = self._connection.cursor()
            # self.get_all_from_test_table()
            return True

    def check_connection(self):
        return self._connection is not None

    def get_current_user(self):
        return self._current_user

    def drop_connection(self):
        self._connection = self._cursor = self._current_user = None

    @staticmethod
    def add_order_by_user(data: tuple[int, int, int, int, int], connect_obj) -> bool:
        try:
            insert_query = """INSERT INTO Orders (id_voyage, client_sender, client_recipient, weight, id_tariff) 
                                    VALUES (%s, %s, %s, %s, %s) """
            connect_obj[1].execute(insert_query, data)
            connect_obj[0].commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    # def get_all_from_test_table(self):
    #     self._cursor.execute("SELECT * FROM test_table")
    #     results = self._cursor.fetchall()
    #     for x in results:
    #         print(x)

class AuthApplication(MySQLConnector):
    def __init__(self):
        super().__init__()
        self.window = tk.Tk()
        self.window.title("Log in/Sign up")
        self.window.geometry("300x100")
        self.window.eval('tk::PlaceWindow . center')

        self.greeting = tk.Label(self.window, text="Hello. Enter your number:")
        self.greeting.pack()

        self.number_field = tk.Entry(self.window)
        self.number_field.pack()

        self.log_label = None

        self.button_login = tk.Button(
            text="Login",
            width=25,
            height=1,
            command=self.button_login_fn
        )
        self.button_login.pack()

    def start_program(self):
        self.window.mainloop()

    def button_login_fn(self):
        entered_string = self.number_field.get()
        if RegexPattern.check_number(entered_string):
            if self.to_connect(entered_string):
                self.got_connection(entered_string)
        else:
            logger.error('Not a Phone number entered')
            self.number_field.delete(0, 'end')
            if self.log_label is None:
                self.log_label = tk.Label(text="Not a Phone number entered")
                self.log_label.pack()

    def got_connection(self, phone_number: str):
        self.window.withdraw()
        UserApplication(self, phone_number)

    def reopen(self):
        logger.info(f"{self._current_user} is log out")
        self.drop_connection()
        self.window.deiconify()

class UserApplication(MySQLConnector):
    def __init__(self, auth_app, user_number: str):
        super().__init__(auth_app)
        self.window = tk.Toplevel(auth_app.window)
        self.window.title("User Panel")
        self.window.geometry("700x500")
        # self.window.eval('tk::PlaceWindow . center')
        # self.window.protocol("WM_DELETE_WINDOW", self.__del__)

        self.tip_to_log_out = tk.Label(self.window, text="Чтобы разлогиниться нажмите Х в правом верхнем углу")
        self.tip_to_log_out.pack()

        self.user_number = user_number
        self.opened_window = None

        self.add_order_button = tk.Button(
            self.window,
            text="Add order",
            width=15,
            height=2,
            command=self.button_add_order_fn
        )
        self.add_order_button.pack()

        self.delete_order_button = tk.Button(
            self.window,
            text="Delete order",
            width=15,
            height=2,
            command=self.button_delete_order_fn
        )
        self.delete_order_button.pack()

        logger.info(f"Current user is {self.get_current_user()}")
        # self.window.mainloop()

    def button_add_order_fn(self):
        if self.opened_window is None or self.opened_window.closed:
            self.opened_window = UserAddOrderApplication(self.window, self.user_number,
                                                         (self._connection, self._cursor))
        else:
            logger.error("Dialogue window already opened")

    def button_delete_order_fn(self):
        if self.opened_window is None or self.opened_window.closed:
            self.opened_window = UserDeleteOrderApplication(self.window, self.user_number)
        else:
            logger.error("Dialogue window already opened")

    def __del__(self):
        # self.window.destroy()
        self.opened_window.__del__()
        App.reopen()

class UserAddOrderApplication:
    def __init__(self, top, num, connection_obj):
        self.window = tk.Toplevel(top)
        self.window.protocol("WM_DELETE_WINDOW", self.__del__)
        self.window.title("Add Order")
        self.window.geometry("400x250")
        # top.eval(f'tk::PlaceWindow {str(self.window)} center')

        self.closed = False
        self.user_number = num
        self.connection_obj = connection_obj

        self.label = tk.Label(self.window, text="Enter info about your order:")
        self.label.pack()

        # order info
        self.id_voyage = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_voyage.pack()
        self.id_sender = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_sender.pack()
        self.id_recipient = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_recipient.pack()
        self.weight = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.weight.pack()
        self.id_tariff = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_tariff.pack()
        #


        self.status_good_flag = False
        self.status_bad_flag = False

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            width=25,
            height=1,
            command=self.button_submit_fn
        )
        self.submit_button.pack()

    def button_submit_fn(self):
        # Checking to valid entered data
        id_voyage = RegexPattern.check_int(self.id_voyage.get())
        if id_voyage is None:
            logger.error("Voyage id entered is invalid")
            self._bad_status()
            return
        id_sender = RegexPattern.check_int(self.id_sender.get())
        if id_sender is None:
            logger.error("Sender id entered is invalid")
            self._bad_status()
            return
        id_recipient = RegexPattern.check_int(self.id_recipient.get())
        if id_recipient is None:
            self._bad_status()
            logger.error("Recipient id entered is invalid")
            return
        weight = RegexPattern.check_int(self.weight.get())
        if weight is None:
            logger.error("Weight entered is invalid")
            self._bad_status()
            return
        id_tariff = RegexPattern.check_int(self.id_tariff.get())
        if id_tariff is None :
            logger.error("Tariff entered is invalid")
            self._bad_status()
            return

        result = MySQLConnector.add_order_by_user((id_voyage, id_sender, id_recipient, weight, id_tariff), self.connection_obj)
        if result:
            logger.info("Order added in table")
            self._good_status()
        else:
            logger.error("Failed to add order")

    def _clean_labels(self):
        if self.status_good_flag:
            # self.status_good.after(1, self.status_good.destroy())
            self.status_good.destroy()
            self.status_good_flag = False
        if self.status_bad_flag:
            # self.status_bad.after(1, self.status_bad.destroy())
            self.status_bad.destroy()
            self.status_bad_flag = False

    def _bad_status(self):
        self._clean_labels()
        self.status_bad = tk.Label(self.window, text="Error adding order - Invalid data format")
        self.status_bad.pack()
        # self.status_bad.after(1, self.status_bad.destroy())
        self.status_bad_flag = True

    def _good_status(self):
        self._clean_labels()
        self.status_good = tk.Label(self.window, text="Successfully added order")
        self.status_good.pack()
        # self.status_good.after(1, self.status_good.destroy())
        self.status_good_flag = True

    def __del__(self):
        self.window.destroy()
        self.closed = True

class UserDeleteOrderApplication:
    def __init__(self, top, num):
        self.window = tk.Toplevel(top)
        self.window.protocol("WM_DELETE_WINDOW", self.__del__)
        self.window.title("Delete Order")
        # top.eval(f'tk::PlaceWindow {str(self.window)} center')

        self.closed = False
        self.user_number = num

        self.label = tk.Label(self.window, text="Enter your order id:")
        self.label.pack()
        self.id_field = tk.Entry(self.window)
        self.id_field.pack()

    def __del__(self):
        self.window.destroy()
        self.closed = True


if __name__=="__main__":
    App = AuthApplication()
    App.start_program()