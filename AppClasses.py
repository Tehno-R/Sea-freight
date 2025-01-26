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

        self.number_field = tk.Entry(self.window, )
        self.number_field.pack()
        self.number_field.insert(tk.END, "-000")

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
        if entered_string == self._admin_number or RegexPattern.check_number(entered_string) is not None:
            if self.to_connect(entered_string):
                self.got_connection()
            else:
                logger.warning('Invalid phone number')
                self.number_field.delete(0, 'end')
                if self.log_label is not None:
                    self.log_label.destroy()
                self.log_label = tk.Label(text="Invalid phone number")
                self.log_label.pack()
        else:
            logger.warning('Not a Phone number entered')
            self.number_field.delete(0, 'end')
            if self.log_label is not None:
                self.log_label.destroy()
            self.log_label = tk.Label(text="Not a Phone number entered")
            self.log_label.pack()

    def got_connection(self):
        self.window.withdraw()
        if self._current_user == self._usernames[0]:
            AdminPanelApplication((self, "550x380"))
        else:
            UserPanelApplication((self, "500x350"))

    def reopen(self):
        logger.info(f"{self._current_user} is log out")
        self.drop_connection()
        self.window.deiconify()


class PanelApplication(MySQLConnector):
    """
    NOT FOR INSTANCE
    """

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
                                                           'Add Order', '500x300'))

    @PanelApplication._button_fn_dec
    def button_delete_order_fn(self):
        self.opened_dialogue_window = DeleteOrderApplication((self.window, self.get_dto(),
                                                              'Delete Order', '400x120'))

    @PanelApplication._button_fn_dec
    def button_view_orders_fn(self):
        # + инфа о клиентах и текущем тарифе
        self.opened_dialogue_window = ViewOrdersApplication((self.window, self.get_dto(),
                                                             'View Orders', '805x600'))

    @PanelApplication._button_fn_dec
    def button_view_voyages_fn(self):
        # С рейсами вместе выводятся название портов и текущий статус
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


class DialogueApplication:
    """
    NOT FOR INSTANCE
    """

    def __init__(self, top: tk.Toplevel,
                 dto_object: namedtuple('dto', ['user_id', 'connection', 'cursor']),
                 move: str = 'None',
                 window_size: str = "500x500"):
        self.window = tk.Toplevel(top)
        self.window.protocol("WM_DELETE_WINDOW", self.__del__)
        self.window.title(f"{move}")
        self.window.geometry(window_size)

        self._log_label_pos_bad = (180, 240)
        self._log_label_pos_good = (162, 240)
        self._log_label_text_bad = "Error adding order"
        self._log_label_text_good = "Successfully added order"

        self.dto = dto_object
        self.closed = False

        self.status_good_flag = False
        self.status_bad_flag = False

        # For print (view tables)
        self.column_names = ("id", "id_voyage", "client_sender",
                             "client_recipient", "weight", "id_tariff")

    def print_view(self):
        self.print_table_wrapper(*self._prepare_data())

    def _prepare_data(self) -> tuple[tuple, tuple]:
        return MySQLConnector.view_orders(self.dto), self.column_names  #

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
        self.status_bad = tk.Label(self.window, text=self._log_label_text_bad)
        self.status_bad.place(x=self._log_label_pos_bad[0], y=self._log_label_pos_bad[1])
        # self.status_bad.after(1, self.status_bad.destroy())
        self.status_bad_flag = True

    def _good_status(self):
        self._clean_labels()
        self.status_good = tk.Label(self.window, text=self._log_label_text_good)
        self.status_good.place(x=self._log_label_pos_good[0], y=self._log_label_pos_good[1])
        # self.status_good.after(1, self.status_good.destroy())
        self.status_good_flag = True

    def print_table_wrapper(self, data, column_names):
        n_cols = len(column_names)
        n_rows = len(data)

        i = 0
        for j, col in enumerate(column_names):
            text = tk.Text(self.window, width=13, height=2, bg="#9BC2E6")
            text.grid(row=i, column=j)
            text.insert(tk.INSERT, col)

        cells = {}

        for i in range(n_rows):
            for j in range(n_cols):
                text = tk.Text(self.window, width=13, height=1)
                text.grid(row=i + 1, column=j)
                text.insert(tk.INSERT, '' if data[i][j] is None else data[i][j])
                cells[(i, j)] = text

    def __del__(self):
        self.window.destroy()
        self.closed = True


class AddOrderApplication(DialogueApplication):
    def __init__(self,
                 application_data: tuple[tk.Toplevel, namedtuple('dto', ['user_id', 'connection', 'cursor']),
                 str,
                 str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter info about your order:")
        self.label.pack()

        # order info
        self.id_voyage_label = tk.Label(self.window, text="Enter voyage id: ")
        self.id_voyage = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_voyage.place(x=250, y=30)
        self.id_voyage_label.place(x=145, y=32)

        self.id_recipient_label = tk.Label(self.window, text="Enter recipient client id: ")
        self.id_recipient = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_recipient.place(x=250, y=70)
        self.id_recipient_label.place(x=100, y=73)

        self.weight_label = tk.Label(self.window, text="Enter weight of your order: ")
        self.weight = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.weight.place(x=250, y=110)
        self.weight_label.place(x=76, y=112)

        self.id_tariff_label = tk.Label(self.window, text="Enter tariff id: ")
        self.id_tariff = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.id_tariff.place(x=250, y=155)
        self.id_tariff_label.place(x=160, y=157)
        #

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            width=25,
            height=1,
            command=self.button_submit_fn
        )
        self.submit_button.place(x=120, y=200)

    def button_submit_fn(self):
        # Checking to valid entered data
        id_voyage = RegexPattern.check_int(self.id_voyage.get())
        if id_voyage is None:
            logger.warning("Voyage id entered is invalid")
            self._bad_status()
            return
        id_recipient = RegexPattern.check_int(self.id_recipient.get())
        if id_recipient is None:
            self._bad_status()
            logger.warning("Recipient id entered is invalid")
            return
        weight = RegexPattern.check_int(self.weight.get())
        if weight is None:
            logger.warning("Weight entered is invalid")
            self._bad_status()
            return
        id_tariff = RegexPattern.check_int(self.id_tariff.get())
        if id_tariff is None:
            logger.warning("Tariff entered is invalid")
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
    namedtuple('dto', ['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter order id that you want to delete:")
        self.label.pack()

        self._log_label_pos_bad = (140, 90)
        self._log_label_pos_good = (115, 90)
        self._log_label_text_bad = "Error deleting order"
        self._log_label_text_good = "Successfully deleted order"

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
            logger.error("Entered order id is invalid")
            self._bad_status()
            return

        result = MySQLConnector.delete_order((id_order, self.dto.user_id), self.dto)
        if result:
            logger.info("Order deleted from table")
            self._good_status()
        else:
            logger.error("Failed to delete order")
            self._bad_status()


class ViewOrdersApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto', ['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)
        self.column_names = ("id", "id_voyage", "sender_fio", "sender_phone",
                             "weight", "type_of_product", "price_per_one_of_weight", "additional_services")

        self.print_view()

    def _prepare_data(self):
        orders_data = MySQLConnector.view_orders_by_user(self.dto)
        return orders_data, self.column_names


class ViewVoyagesApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto', ['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)
        self.column_names = ("id",
                             "departure_port_name", "departure_port_country", "departure_port_city",
                             "arrival_port_name", "arrival_port_country", "arrival_port_city",
                             "date_departure", "date_arrival",
                             "status_name", "max_weight")

        self.print_view()

    def _prepare_data(self):
        orders_data = MySQLConnector.view_voyages_by_user(self.dto)
        return orders_data, self.column_names


class ViewTariffsApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto', ['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)
        self.column_names = ("id", "type_of_product", "price_per_one_of_weight")

        self.print_view()

    def _prepare_data(self):
        orders_data = MySQLConnector.view_tariffs(self.dto)
        return orders_data, self.column_names


class ViewAdditionalServicesApplication(DialogueApplication):
    def __init__(self, application_data: tuple[tk.Toplevel,
    namedtuple('dto', ['user_id', 'connection', 'cursor']),
    str,
    str]):
        super().__init__(*application_data)
        self.column_names = ("id", "service_name", "service_price")

        self.print_view()

    def _prepare_data(self):
        orders_data = MySQLConnector.view_additional_services(self.dto)
        return orders_data, self.column_names


class AdminPanelApplication(PanelApplication):
    def __init__(self, app_data: tuple[AuthApplication, str]):
        super().__init__(*app_data)

        self.add_additional_services_button = tk.Button(
            self.window,
            text="Add additional service",
            width=15,
            height=2,
            command=self.button_add_additional_service_fn
        )
        self.add_additional_services_button.place(x=100, y=50)

        self.view_additional_services_button = tk.Button(
            self.window,
            text="View additional service",
            width=15,
            height=2,
            command=self.button_view_additional_service_fn
        )
        self.view_additional_services_button.place(x=300, y=50)

        self.add_client_button = tk.Button(
            self.window,
            text="Add Client service",
            width=15,
            height=2,
            command=self.button_add_client_fn
        )
        self.add_client_button.place(x=100, y=100)

        self.view_client_button = tk.Button(
            self.window,
            text="View Client service",
            width=15,
            height=2,
            command=self.button_view_client_fn
        )
        self.view_client_button.place(x=300, y=100)

        self.add_port_button = tk.Button(
            self.window,
            text="Add Port service",
            width=15,
            height=2,
            command=self.button_add_port_fn
        )
        self.add_port_button.place(x=100, y=150)

        self.view_port_button = tk.Button(
            self.window,
            text="Delete Port service",
            width=15,
            height=2,
            command=self.button_view_port_fn
        )
        self.view_port_button.place(x=300, y=150)

        self.add_status_button = tk.Button(
            self.window,
            text="Add Status service",
            width=15,
            height=2,
            command=self.button_add_status_fn
        )
        self.add_status_button.place(x=100, y=200)

        self.view_status_button = tk.Button(
            self.window,
            text="View Status service",
            width=15,
            height=2,
            command=self.button_view_status_fn
        )
        self.view_status_button.place(x=300, y=200)

        self.add_tariff_button = tk.Button(
            self.window,
            text="Add Tariff service",
            width=15,
            height=2,
            command=self.button_add_tariff_fn
        )
        self.add_tariff_button.place(x=100, y=250)

        self.view_tariff_button = tk.Button(
            self.window,
            text="View Tariff service",
            width=15,
            height=2,
            command=self.button_view_tariff_fn
        )
        self.view_tariff_button.place(x=300, y=250)

        self.add_voyage_button = tk.Button(
            self.window,
            text="Add Voyage service",
            width=15,
            height=2,
            command=self.button_add_voyage_fn
        )
        self.add_voyage_button.place(x=100, y=300)

        self.view_voyage_button = tk.Button(
            self.window,
            text="View Voyage service",
            width=15,
            height=2,
            command=self.button_view_voyage_fn
        )
        self.view_voyage_button.place(x=300, y=300)


    @PanelApplication._button_fn_dec
    def button_add_additional_service_fn(self):
        self.opened_dialogue_window = AddAdditionalServiceApplication((self.window, self.get_dto(),
                                                           'Add Additional Service', '500x300'))

    @PanelApplication._button_fn_dec
    def button_view_additional_service_fn(self):
        self.opened_dialogue_window = AddOrderApplication((self.window, self.get_dto(),
                                                           'View Additional Service', '500x300'))

    @PanelApplication._button_fn_dec
    def button_add_client_fn(self):
        self.opened_dialogue_window = AddClientApplication((self.window, self.get_dto(),
                                                           'Add Client', '500x300'))

    @PanelApplication._button_fn_dec
    def button_view_client_fn(self):
        self.opened_dialogue_window = AddOrderApplication((self.window, self.get_dto(),
                                                           'Add Order', '500x300'))

    @PanelApplication._button_fn_dec
    def button_add_port_fn(self):
        self.opened_dialogue_window = AddPortApplication((self.window, self.get_dto(),
                                                           'Add Port', '500x300'))

    @PanelApplication._button_fn_dec
    def button_view_port_fn(self):
        self.opened_dialogue_window = AddOrderApplication((self.window, self.get_dto(),
                                                           'Add Order', '500x300'))

    @PanelApplication._button_fn_dec
    def button_add_status_fn(self):
        self.opened_dialogue_window = AddStatusApplication((self.window, self.get_dto(),
                                                           'Add Status', '500x300'))

    @PanelApplication._button_fn_dec
    def button_view_status_fn(self):
        self.opened_dialogue_window = AddOrderApplication((self.window, self.get_dto(),
                                                           'Add Order', '500x300'))

    @PanelApplication._button_fn_dec
    def button_add_tariff_fn(self):
        self.opened_dialogue_window = AddTariffApplication((self.window, self.get_dto(),
                                                           'Add Tariff', '500x300'))

    @PanelApplication._button_fn_dec
    def button_view_tariff_fn(self):
        self.opened_dialogue_window = AddOrderApplication((self.window, self.get_dto(),
                                                           'Add Order', '500x300'))

    @PanelApplication._button_fn_dec
    def button_add_voyage_fn(self):
        self.opened_dialogue_window = AddVoyageApplication((self.window, self.get_dto(),
                                                           'Add Voyage', '500x300'))

    @PanelApplication._button_fn_dec
    def button_view_voyage_fn(self):
        self.opened_dialogue_window = AddOrderApplication((self.window, self.get_dto(),
                                                           'Add Order', '500x300'))

class AddAdditionalServiceApplication(DialogueApplication):
    def __init__(self,
                 application_data: tuple[tk.Toplevel, namedtuple('dto', ['user_id', 'connection', 'cursor']),
                 str,
                 str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter info about Additional Service:")
        self.label.pack()

        # order info
        self.service_name_label = tk.Label(self.window, text="Enter service name: ")
        self.service_name = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.service_name.place(x=250, y=30)
        self.service_name_label.place(x=145, y=32)

        self.service_price_label = tk.Label(self.window, text="Enter price for service: ")
        self.service_price = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.service_price.place(x=250, y=70)
        self.service_price_label.place(x=100, y=73)
        #

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            width=25,
            height=1,
            command=self.button_submit_fn
        )
        self.submit_button.place(x=120, y=200)

    def button_submit_fn(self):
        # Checking to valid entered data
        service_name = self.service_name.get()
        if len(service_name) == 0:
            logger.warning("Service name entered is invalid")
            self._bad_status()
            return
        service_price = RegexPattern.check_int(self.service_price.get())
        if service_price is None:
            self._bad_status()
            logger.warning("Service price entered is invalid")
            return

        result = MySQLConnector.add_additional_services((service_name, service_price),
                                          self.dto)
        if result:
            logger.info("Additional service added in table")
            self._good_status()
        else:
            logger.error("Failed to add additional service")

class AddClientApplication(DialogueApplication):
    def __init__(self,
                 application_data: tuple[tk.Toplevel, namedtuple('dto', ['user_id', 'connection', 'cursor']),
                 str,
                 str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter info about Client:")
        self.label.pack()

        # order info
        self.client_fio_label = tk.Label(self.window, text="Enter client fio: ")
        self.client_fio = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.client_fio.place(x=250, y=30)
        self.client_fio_label.place(x=145, y=32)

        self.client_number_label = tk.Label(self.window, text="Enter client number: ")
        self.client_number = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.client_number.place(x=250, y=70)
        self.client_number_label.place(x=100, y=73)
        #

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            width=25,
            height=1,
            command=self.button_submit_fn
        )
        self.submit_button.place(x=120, y=200)

    def button_submit_fn(self):
        # Checking to valid entered data
        client_fio = self.client_fio.get()
        if len(client_fio) == 0:
            logger.warning("Client fio entered is invalid")
            self._bad_status()
            return
        client_number = RegexPattern.check_number(self.client_number.get())
        if client_number is None:
            self._bad_status()
            logger.warning("Client number entered is invalid")
            return

        result = MySQLConnector.add_client_services((client_fio, client_number[1:]),
                                          self.dto)
        if result:
            logger.info("Additional service added in table")
            self._good_status()
        else:
            logger.error("Failed to add additional service")

class AddPortApplication(DialogueApplication):
    def __init__(self,
                 application_data: tuple[tk.Toplevel, namedtuple('dto', ['user_id', 'connection', 'cursor']),
                 str,
                 str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter info about Port:")
        self.label.pack()

        # order info
        self.port_name_label = tk.Label(self.window, text="Enter port name: ")
        self.port_name = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.port_name.place(x=250, y=30)
        self.port_name_label.place(x=145, y=32)

        self.country_label = tk.Label(self.window, text="Enter port country: ")
        self.country = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.country.place(x=250, y=70)
        self.country_label.place(x=100, y=73)

        self.city_label = tk.Label(self.window, text="Enter port city: ")
        self.city = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.city.place(x=250, y=110)
        self.city_label.place(x=100, y=114)
        #

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            width=25,
            height=1,
            command=self.button_submit_fn
        )
        self.submit_button.place(x=120, y=200)

    def button_submit_fn(self):
        # Checking to valid entered data
        port_name = self.port_name.get()
        if len(port_name) == 0:
            logger.warning("Port name entered is invalid")
            self._bad_status()
            return
        country = self.country.get()
        if len(country) == 0:
            logger.warning("Port country entered is invalid")
            self._bad_status()
            return
        city = self.city.get()
        if len(city) == 0:
            logger.warning("Port city entered is invalid")
            self._bad_status()
            return

        result = MySQLConnector.add_port((port_name, country, city),
                                          self.dto)
        if result:
            logger.info("Port added in table")
            self._good_status()
        else:
            logger.error("Failed to add port")

class AddStatusApplication(DialogueApplication):
    def __init__(self,
                 application_data: tuple[tk.Toplevel, namedtuple('dto', ['user_id', 'connection', 'cursor']),
                 str,
                 str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter info about Status:")
        self.label.pack()

        # order info
        self.status_name_label = tk.Label(self.window, text="Enter status name: ")
        self.status_name = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.status_name.place(x=250, y=30)
        self.status_name_label.place(x=145, y=32)
        #

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            width=25,
            height=1,
            command=self.button_submit_fn
        )
        self.submit_button.place(x=120, y=200)

    def button_submit_fn(self):
        # Checking to valid entered data
        status_name = self.status_name.get()
        if len(status_name) == 0:
            logger.warning("Status name entered is invalid")
            self._bad_status()
            return

        result = MySQLConnector.add_status((status_name, ),
                                          self.dto)
        if result:
            logger.info("Status added in table")
            self._good_status()
        else:
            logger.error("Failed to add status")

class AddTariffApplication(DialogueApplication):
    def __init__(self,
                 application_data: tuple[tk.Toplevel, namedtuple('dto', ['user_id', 'connection', 'cursor']),
                 str,
                 str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter info about Tariff:")
        self.label.pack()

        # order info
        self.type_product_label = tk.Label(self.window, text="Enter type of product name: ")
        self.type_product = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.type_product.place(x=250, y=30)
        self.type_product_label.place(x=145, y=32)

        self.price_label = tk.Label(self.window, text="Enter price name: ")
        self.price = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.price.place(x=250, y=70)
        self.price_label.place(x=145, y=72)
        #

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            width=25,
            height=1,
            command=self.button_submit_fn
        )
        self.submit_button.place(x=120, y=200)

    def button_submit_fn(self):
        # Checking to valid entered data
        type_product = self.type_product.get()
        if len(type_product) == 0:
            logger.warning("Product type entered is invalid")
            self._bad_status()
            return
        price = RegexPattern.check_int(self.price.get())
        if price is None:
            self._bad_status()
            logger.warning("Tariff price entered is invalid")
            return

        result = MySQLConnector.add_tariff((type_product, price),
                                          self.dto)
        if result:
            logger.info("Tariff added in table")
            self._good_status()
        else:
            logger.error("Failed to add tariff")

class AddVoyageApplication(DialogueApplication):
    def __init__(self,
                 application_data: tuple[tk.Toplevel, namedtuple('dto', ['user_id', 'connection', 'cursor']),
                 str,
                 str]):
        super().__init__(*application_data)

        self.label = tk.Label(self.window, text="Enter info about Voyage:")
        self.label.pack()

        # order info
        self.port_departure_label = tk.Label(self.window, text="Enter port departure id: ")
        self.port_departure = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.port_departure.place(x=250, y=30)
        self.port_departure_label.place(x=145, y=32)

        self.port_arrival_label = tk.Label(self.window, text="Enter port arrival id: ")
        self.port_arrival = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.port_arrival.place(x=250, y=70)
        self.port_arrival_label.place(x=145, y=72)

        self.departure_date_label = tk.Label(self.window, text="Enter departure date: ")
        self.departure_date = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.departure_date.place(x=250, y=110)
        self.departure_date_label.place(x=145, y=114)

        self.arrival_date_label = tk.Label(self.window, text="Enter arrival date: ")
        self.arrival_date = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.arrival_date.place(x=250, y=150)
        self.arrival_date_label.place(x=145, y=154)

        self.status_id_label = tk.Label(self.window, text="Enter status id: ")
        self.status_id = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.status_id.place(x=250, y=190)
        self.status_id_label.place(x=145, y=198)

        self.max_weight_label = tk.Label(self.window, text="Enter max weight: ")
        self.max_weight = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
        self.max_weight.place(x=250, y=240)
        self.max_weight_label.place(x=145, y=248)
        #

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            width=25,
            height=1,
            command=self.button_submit_fn
        )
        self.submit_button.place(x=120, y=280)

    def button_submit_fn(self):
        # Checking to valid entered data
        port_departure = RegexPattern.check_int(self.port_departure.get())
        if port_departure is None:
            self._bad_status()
            logger.warning("Departure port entered is invalid")
            return
        port_arrival = RegexPattern.check_int(self.port_arrival.get())
        if port_arrival is None:
            self._bad_status()
            logger.warning("Arrival port entered is invalid")
            return
        departure_date = RegexPattern.date_check(self.departure_date.get())
        if departure_date is None:
            self._bad_status()
            logger.warning("Departure date entered is invalid")
            return
        arrival_date = RegexPattern.date_check(self.arrival_date.get())
        if arrival_date is None:
            self._bad_status()
            logger.warning("Arrival date entered is invalid")
            return
        status_id = RegexPattern.check_int(self.status_id.get())
        if status_id is None:
            self._bad_status()
            logger.warning("Status id entered is invalid")
            return
        max_weight = RegexPattern.check_int(self.max_weight.get())
        if max_weight is None:
            self._bad_status()
            logger.warning("Max weight entered is invalid")
            return

        result = MySQLConnector.add_voyage((port_departure, port_arrival, departure_date,
                                            arrival_date, status_id, max_weight),
                                          self.dto)
        if result:
            logger.info("Voyage added in table")
            self._good_status()
        else:
            logger.error("Failed to add voyage")
