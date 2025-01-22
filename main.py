from MySQLConnector import MySQLConnector
from log import logger
from AppClasses import AuthApplication

# App = None



# class AdminApplication(MySQLConnector):
#     def __init__(self, auth_app):
#         super().__init__(auth_app)
#         self.window = tk.Toplevel(auth_app.window)
#         self.window.title("Admin Panel")
#         self.window.geometry("500x300")
#
#         self.tip_to_log_out = tk.Label(self.window, text="Чтобы разлогиниться нажмите Х в правом верхнем углу")
#         self.tip_to_log_out.pack()
#
#         self.opened_window = None
#
#         self.add_additional_service_button = tk.Button(
#             self.window,
#             text="Add Additional Service",
#             width=15,
#             height=2,
#             command=self.button_add_additional_service_fn
#         )
#         self.add_additional_service_button.pack()
#
#         self.delete_additional_service_button = tk.Button(
#             self.window,
#             text="Add Additional Service",
#             width=15,
#             height=2,
#             command=self.button_delete_additional_service_fn
#         )
#         self.delete_additional_service_button.pack()
#
#         logger.info(f"Current user is {self.get_current_user()}")
#
#     def button_add_additional_service_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = AdminAddAdditionalServiceApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_delete_additional_service_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = AdminDeleteAdditionalServiceApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_view_additional_service_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = AdminViewAdditionalServicesApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_add_client_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = AdminAddAdditionalServiceApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_delete_client_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = AdminDeleteAdditionalServiceApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_view_clients_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = AdminViewAdditionalServicesApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#
#
#
#     def __del__(self):
#         if self.opened_window is not None:
#             self.opened_window.__del__()
#         App.reopen()
#
# class AdminAddAdditionalServiceApplication:
#     def __init__(self, top, connection_obj):
#         self.window = tk.Toplevel(top)
#         self.window.protocol("WM_DELETE_WINDOW", self.__del__)
#         self.window.title("Add Additional Service")
#         self.window.geometry("400x220")
#
#         self.closed = False
#         self.connection_obj = connection_obj
#
#         self.label = tk.Label(self.window, text="Enter info about your order:")
#         self.label.pack()
#
#         # order info
#         self.service_name = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
#         self.service_name.pack()
#         self.price = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
#         self.price.pack()
#         #
#
#
#         self.status_good_flag = False
#         self.status_bad_flag = False
#
#         self.submit_button = tk.Button(
#             self.window,
#             text="Submit",
#             width=25,
#             height=1,
#             command=self.button_submit_fn
#         )
#         self.submit_button.pack()
#
#     def button_submit_fn(self):
#         # Checking to valid entered data
#         service_name = RegexPattern.-check_int(self.service_name.get())
#         if service_name is None:
#             logger.error("Service name entered is invalid")
#             self._bad_status()
#             return
#         price = RegexPattern.-check_int(self.price.get())
#         if price is None:
#             self._bad_status()
#             logger.error("Price id entered is invalid")
#             return
#
#         result = MySQLConnector.add_additional_services((service_name, price), self.connection_obj)
#         if result:
#             logger.info("Order added in table")
#             self._good_status()
#         else:
#             logger.error("Failed to add order")
#
#     def _clean_labels(self):
#         if self.status_good_flag:
#             # self.status_good.after(1, self.status_good.destroy())
#             self.status_good.destroy()
#             self.status_good_flag = False
#         if self.status_bad_flag:
#             # self.status_bad.after(1, self.status_bad.destroy())
#             self.status_bad.destroy()
#             self.status_bad_flag = False
#
#     def _bad_status(self):
#         self._clean_labels()
#         self.status_bad = tk.Label(self.window, text="Error adding order - Invalid data format")
#         self.status_bad.pack()
#         # self.status_bad.after(1, self.status_bad.destroy())
#         self.status_bad_flag = True
#
#     def _good_status(self):
#         self._clean_labels()
#         self.status_good = tk.Label(self.window, text="Successfully added order")
#         self.status_good.pack()
#         # self.status_good.after(1, self.status_good.destroy())
#         self.status_good_flag = True
#
#     def __del__(self):
#         self.window.destroy()
#         self.closed = True



# class UserApplication(MySQLConnector):
#     def __init__(self, auth_app):
#         super().__init__(auth_app)
#         self.window = tk.Toplevel(auth_app.window)
#         self.window.title("User Panel")
#         self.window.geometry("500x350")
#
#         self.tip_to_log_out = tk.Label(self.window, text="Чтобы разлогиниться нажмите Х в правом верхнем углу")
#         self.tip_to_log_out.pack()
#
#         self.opened_window = None
#
#         self.add_order_button = tk.Button(
#             self.window,
#             text="Add order",
#             width=15,
#             height=2,
#             command=self.button_add_order_fn
#         )
#         self.add_order_button.pack()
#
#         self.delete_order_button = tk.Button(
#             self.window,
#             text="Delete order",
#             width=15,
#             height=2,
#             command=self.button_delete_order_fn
#         )
#         self.delete_order_button.pack()
#
#         self.view_orders_button = tk.Button(
#             self.window,
#             text="View orders",
#             width=15,
#             height=2,
#             command=self.button_view_orders_fn
#         )
#         self.view_orders_button.pack()
#
#         self.view_voyages_button = tk.Button(
#             self.window,
#             text="View voyages",
#             width=15,
#             height=2,
#             command=self.button_view_voyages_fn
#         )
#         self.view_voyages_button.pack()
#
#         self.view_tariffs_button = tk.Button(
#             self.window,
#             text="View tariffs",
#             width=15,
#             height=2,
#             command=self.button_view_tariffs_fn
#         )
#         self.view_tariffs_button.pack()
#
#         self.view_additional_services_button = tk.Button(
#             self.window,
#             text="View additional services",
#             width=15,
#             height=2,
#             command=self.button_view_additional_services_fn
#         )
#         self.view_additional_services_button.pack()
#
#         logger.info(f"Current user is {self.get_current_user()}")
#
#     def button_add_order_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = UserAddOrderApplication(self.window, self._user_id,
#                                                          (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_delete_order_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = UserDeleteOrderApplication(self.window, self._user_id,
#                                                             (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_view_orders_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = UserViewOrdersApplication(self.window, self._user_id,
#                                                             (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_view_voyages_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = UserViewVoyagesApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_view_tariffs_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = UserViewTariffsApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#     def button_view_additional_services_fn(self):
#         if self.opened_window is None or self.opened_window.closed:
#             self.opened_window = UserViewAdditionalServicesApplication(self.window, (self._connection, self._cursor))
#         else:
#             logger.error("Dialogue window already opened")
#
#
#     def __del__(self):
#         if self.opened_window is not None:
#             self.opened_window.__del__()
#         App.reopen()



# class DeleteOrderApplication:
#     def __init__(self, top, user_id, connection_obj):
#         self.window = tk.Toplevel(top)
#         self.window.protocol("WM_DELETE_WINDOW", self.__del__)
#         self.window.title("Delete Order")
#         self.window.geometry("400x120")
#
#         self.closed = False
#         self.user_id = user_id
#         self.connection_obj = connection_obj
#
#         self.label = tk.Label(self.window, text="Enter order id that you want to delete:")
#         self.label.pack()
#
#         # order info
#         self.id_order = tk.Entry(self.window, width=10, borderwidth=5, justify='center')
#         self.id_order.pack()
#         #
#
#         self.status_good_flag = False
#         self.status_bad_flag = False
#
#         self.submit_button = tk.Button(
#             self.window,
#             text="Submit",
#             width=25,
#             height=1,
#             command=self.button_submit_fn
#         )
#         self.submit_button.pack()
#
#     def button_submit_fn(self):
#         # Checking to valid entered data
#         id_order = RegexPattern.check_int(self.id_order.get())
#         if id_order is None:
#             logger.error("Order id entered is invalid")
#             self._bad_status()
#             return
#
#         result = MySQLConnector.delete_order_by_user((id_order, self.user_id), self.connection_obj)
#         if result:
#             logger.info("Order deleted from table")
#             self._good_status()
#         else:
#             logger.error("Failed to delete order")
#
#     def _clean_labels(self):
#         if self.status_good_flag:
#             # self.status_good.after(1, self.status_good.destroy())
#             self.status_good.destroy()
#             self.status_good_flag = False
#         if self.status_bad_flag:
#             # self.status_bad.after(1, self.status_bad.destroy())
#             self.status_bad.destroy()
#             self.status_bad_flag = False
#
#     def _bad_status(self):
#         self._clean_labels()
#         self.status_bad = tk.Label(self.window, text="Error deleting order - Invalid data format")
#         self.status_bad.pack()
#         # self.status_bad.after(1, self.status_bad.destroy())
#         self.status_bad_flag = True
#
#     def _good_status(self):
#         self._clean_labels()
#         self.status_good = tk.Label(self.window, text="Successfully deleted order")
#         self.status_good.pack()
#         # self.status_good.after(1, self.status_good.destroy())
#         self.status_good_flag = True
#
#     def __del__(self):
#         self.window.destroy()
#         self.closed = True

# class UserViewOrdersApplication:
#     def __init__(self, top, user_id, connection_obj):
#         self.window = tk.Toplevel(top)
#         self.window.protocol("WM_DELETE_WINDOW", self.__del__)
#         self.window.title("Delete Order")
#         self.window.geometry("805x600")
#
#         self.closed = False
#         self.user_id = user_id
#         self.connection_obj = connection_obj
#
#         self.print_table()
#
#     def print_table(self):
#         result = MySQLConnector.view_orders_by_user((self.user_id,), self.connection_obj)
#
#         n_cols = 6
#         n_rows = len(result)
#
#         column_names = ["id", "id_voyage", "client_sender", "client_recipient", "weight", "id_tariff"]
#         i = 0
#         for j, col in enumerate(column_names):
#             text = tk.Text(self.window, width=16, height=1, bg="#9BC2E6")
#             text.grid(row=i, column=j)
#             text.insert(tk.INSERT, col)
#
#             # Dictionary for storing the text widget
#         # references
#         cells = {}
#
#         # adding all the other rows into the grid
#         for i in range(n_rows):
#             for j in range(n_cols):
#                 text = tk.Text(self.window, width=16, height=1)
#                 text.grid(row=i + 1, column=j)
#                 text.insert(tk.INSERT, result[i][j])
#                 cells[(i, j)] = text
#
#     def __del__(self):
#         self.window.destroy()
#         self.closed = True

if __name__=="__main__":
    App = AuthApplication()
    App.start_program()