import tkinter as tk
from collections import namedtuple

from log import logger
from MySQLConnector import MySQLConnector
from RegexChecker import RegexPattern


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
        if entered_string == self._admin_number:
            self.got_connection()
        else:
            if RegexPattern.check_number(entered_string):
                if self.to_connect(entered_string):
                    self.got_connection()
                else:
                    logger.error('Invalid phone number')
                    self.number_field.delete(0, 'end')
                    if self.log_label is not None:
                        self.log_label.destroy()
                    self.log_label = tk.Label(text="Invalid phone number")
                    self.log_label.pack()
            else:
                logger.error('Not a Phone number entered')
                self.number_field.delete(0, 'end')
                if self.log_label is not None:
                    self.log_label.destroy()
                self.log_label = tk.Label(text="Not a Phone number entered")
                self.log_label.pack()

    def got_connection(self):
        self.window.withdraw()
        if self._current_user == self._usernames[0]:
            AdminPanelApplication((self, "500x350"))
        else:
            UserPanelApplication((self, "500x350"))

    def reopen(self):
        logger.info(f"{self._current_user} is log out")
        self.drop_connection()
        self.window.deiconify()

class PanelApplication(MySQLConnector):
    def __init__(self, auth_app: AuthApplication, window_size="500x350"):
        super().__init__(auth_app)
        self.reopen_auth_window = auth_app.reopen
        self.window = tk.Toplevel(auth_app.window)
        self.window.title(f"{self._current_user} Panel")
        self.window.geometry(window_size)

        self.tip_to_log_out = tk.Label(self.window, text="Чтобы разлогиниться нажмите Х в правом верхнем углу")
        self.tip_to_log_out.pack()

        self.opened_dialogue_window = None

        logger.info(f"Current user is {self.get_current_user()}")

    def __del__(self):
        if self.opened_dialogue_window is not None:
            self.opened_dialogue_window.__del__()
        self.reopen_auth_window()

    @staticmethod
    def _button_fn_dec(func):
        def wrapper(self):
            if self.opened_dialogue_window is None or self.opened_dialogue_window.closed:
                func(self)
            else:
                logger.warning("Dialogue window already opened")

        return wrapper

class UserPanelApplication(PanelApplication):
    def __init__(self, app_data: tuple[AuthApplication, str]):
        """
        :param app_data: tuple of: instance of AuthApplication class, window size
        :rtype app_data: tuple[AuthApplication, str]
        :example: (auth_app, "500x350")
        """
        super().__init__(*app_data)

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

        self.view_orders_button = tk.Button(
            self.window,
            text="View orders",
            width=15,
            height=2,
            command=self.button_view_orders_fn
        )
        self.view_orders_button.pack()

        self.view_voyages_button = tk.Button(
            self.window,
            text="View voyages",
            width=15,
            height=2,
            command=self.button_view_voyages_fn
        )
        self.view_voyages_button.pack()

        self.view_tariffs_button = tk.Button(
            self.window,
            text="View tariffs",
            width=15,
            height=2,
            command=self.button_view_tariffs_fn
        )
        self.view_tariffs_button.pack()

        self.view_additional_services_button = tk.Button(
            self.window,
            text="View additional services",
            width=15,
            height=2,
            command=self.button_view_additional_services_fn
        )
        self.view_additional_services_button.pack()

    @PanelApplication._button_fn_dec
    def button_add_order_fn(self):
            self.opened_dialogue_window = AddOrderApplication((self.window, self.get_dto(),
                                                               'Add Order', '300x200'))

    @PanelApplication._button_fn_dec
    def button_delete_order_fn(self):
        self.opened_dialogue_window = DeleteOrderApplication((self.window, self.get_dto(),
                                                               'Delete Order', '400x120'))

    @PanelApplication._button_fn_dec
    def button_view_orders_fn(self):
        self.opened_dialogue_window = ViewOrderApplication((self.window, self.get_dto(),
                                                               'View Orders', '805x600'))

    @PanelApplication._button_fn_dec
    def button_view_voyages_fn(self):
        self.opened_dialogue_window = ViewVoyagesApplication((self.window, self.get_dto(),
                                                            'View Voyages', '938x600'))

    @PanelApplication._button_fn_dec
    def button_view_tariffs_fn(self):
        self.opened_dialogue_window = ViewTariffsApplication((self.window, self.get_dto(),
                                                            'View Tariffs', '402x600'))

    @PanelApplication._button_fn_dec
    def button_view_additional_services_fn(self):
        self.opened_dialogue_window = ViewAdditionalServicesApplication((self.window, self.get_dto(),
                                                            'View Additional Services', '402x600'))

    @PanelApplication._button_fn_dec
    def button_view_additional_services_fn(self):
        self.opened_dialogue_window = ViewOrdersAndAdditionalServicesApplication((self.window, self.get_dto(),
                                                            'View Orders and Additional Services', '268x200'))

class DialogueApplication:
    def __init__(self, top: tk.Toplevel,
                 dto_object: namedtuple('dto',['user_id', 'connection', 'cursor']),
                 move: str = 'None',
                 window_size: str = "500x500"):
        self.window = tk.Toplevel(top)
        self.window.protocol("WM_DELETE_WINDOW", self.__del__)
        self.window.title(f"{move}")
        self.window.geometry(window_size)

        self.dto = dto_object
        self.closed = False

        self.status_good_flag = False
        self.status_bad_flag = False

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

    def print_table_wrapper(self, func, column_names):
        result = func(self.dto)

        n_cols = len(column_names)
        n_rows = len(result)

        i = 0
        for j, col in enumerate(column_names):
            text = tk.Text(self.window, width=16, height=1, bg="#9BC2E6")
            text.grid(row=i, column=j)
            text.insert(tk.INSERT, col)

            # Dictionary for storing the text widget
        # references
        cells = {}

        # adding all the other rows into the grid
        for i in range(n_rows):
            for j in range(n_cols):
                text = tk.Text(self.window, width=16, height=1)
                text.grid(row=i + 1, column=j)
                text.insert(tk.INSERT, result[i][j])
                cells[(i, j)] = text

    def __del__(self):
        self.window.destroy()
        self.closed = True

class AddOrderApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto',['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter info about your order:")
        self.label.pack()

        # order info
        self.id_voyage = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_voyage.pack()
        self.id_recipient = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_recipient.pack()
        self.weight = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.weight.pack()
        self.id_tariff = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_tariff.pack()
        #

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

        result = MySQLConnector.add_order((id_voyage, self.dto.user_id, id_recipient, weight, id_tariff),
                                                  self.dto)
        if result:
            logger.info("Order added in table")
            self._good_status()
        else:
            logger.error("Failed to add order")

class DeleteOrderApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto',['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter order id that you want to delete:")
        self.label.pack()

        # order info
        self.id_order = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_order.pack()

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
        id_order = RegexPattern.check_int(self.id_order.get())
        if id_order is None:
            logger.error("Order id entered is invalid")
            self._bad_status()
            return

        result = MySQLConnector.delete_order((id_order, self.dto.user_id), self.dto)
        if result:
            logger.info("Order deleted from table")
            self._good_status()
        else:
            logger.error("Failed to delete order")

class ViewOrderApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto',['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)

        self.print_table_wrapper(MySQLConnector.view_orders,
                                 ("id", "id_voyage", "client_sender",
                                  "client_recipient", "weight", "id_tariff"))

class ViewVoyagesApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto',['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)
        self.print_table_wrapper(MySQLConnector.view_voyages,
                                 ("id", "port_of_departure", "port_of_arrival",
                                  "date_departure", "date_arrival", "id_status", "max_weight"))

class ViewTariffsApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto',['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)

        self.print_table_wrapper(MySQLConnector.view_tariffs,
                                 ("id", "type_of_product", "price"))

class ViewAdditionalServicesApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto',['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)

        self.print_table_wrapper(MySQLConnector.view_additional_services,
                                 ("id", "service_name", "price"))

class ViewOrdersAndAdditionalServicesApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto',['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)

        self.print_table_wrapper(MySQLConnector.view_additional_services,
                                 ("id_order", "id_additional_service"))

class AdminPanelApplication(PanelApplication):
    def __init__(self, app_data: tuple[AuthApplication, str]):
        """
        :param app_data: tuple of: instance of AuthApplication class, window size
        :rtype app_data: tuple[AuthApplication, str]
        :example: (auth_app, "500x350")
        """
        super().__init__(*app_data)