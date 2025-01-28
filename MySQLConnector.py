from log import logger
import mysql.connector
from collections import namedtuple

def check_number(number):
    connection = mysql.connector.connect(
        host='localhost',
        user='ADMINISTRATOR',
        password='132',
        database='Transportations'
    )
    cursor = connection.cursor()

    cursor.execute("SELECT number FROM Clients WHERE number=%s", (number,))
    result = cursor.fetchone()

    logger.debug(f"Number check returned: {result}")
    return result

class MySQLConnector:
    def __init__(self, connection = None):
        self._admin_number = '-000'
        self._usernames = ('admin', 'user')

        if connection is not None and isinstance(connection, MySQLConnector):
            self._connection = connection._connection
            self._cursor = connection._cursor
            self._current_user = connection._current_user
            self._user_phone = connection._user_phone
        else:
            self._connection = self._cursor = self._current_user = self._user_phone = None

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
                logger.info(f"Connected to MySQL by {self._current_user}")
            else:
                phone_number = check_number(number[1:])
                if phone_number is not None:
                    self._connection = mysql.connector.connect(
                        host='localhost',
                        user=self._usernames[1],
                        password='',
                        database='Transportations'
                    )
                    self._current_user = self._usernames[1]
                    self._user_phone = phone_number[0] # Возвращается либо (user id,) либо None (которые обрабатывается выше)
                    logger.info(f"Connected to MySQL by {self._current_user}")
                else:
                    logger.error(f"Invalid phone number")
                    return False
        except mysql.connector.Error:
            logger.error("Error connecting to MySQL")
            return False

        self._cursor = self._connection.cursor()
        return True

    def check_connection(self):
        return self._connection is not None

    def get_current_user(self):
        return self._current_user

    def drop_connection(self):
        self._connection = self._cursor = self._current_user = self._user_phone = None

    def get_dto(self):
        return (namedtuple('dto',['user_phone', 'connection', 'cursor'])
                (self._user_phone, self._connection, self._cursor))

    # user
    @staticmethod
    def add_order(data: tuple[int, int, int, int, int],
                  dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])) -> bool:
        try:
            insert_query = """INSERT INTO Orders (id_voyage, client_sender, client_recipient, weight, id_tariff) 
                                    VALUES (%s, %s, %s, %s, %s) """
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def delete_order(data: tuple[int, int],
                     dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])) -> int:
        try:
            insert_query = """DELETE FROM Orders WHERE id=%s AND client_sender=%s"""
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()

            result = dto.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(err)
            return 0
        return result

    @staticmethod
    def view_orders(dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])) -> tuple | None:
        if dto.user_phone is not None:
            try:
                dto.cursor.execute("SELECT * FROM Orders WHERE client_sender=%s", (dto.user_phone, ))
                result = dto.cursor.fetchall()
            except mysql.connector.errors:
                logger.error("Error get orders data from database")
                return None
            else:
                if result is not None:
                    return result
                else:
                    return ()
        else:
            try:
                dto.cursor.execute("SELECT * FROM Orders")
                result = dto.cursor.fetchall()
            except mysql.connector.Error:
                logger.error("Error get orders data from database")
                return None
            else:
                if result is not None:
                    return result
                else:
                    return ()

    @staticmethod
    def view_orders_by_user(dto: namedtuple('dto', ['user_phone', 'connection', 'cursor'])) -> tuple | None:
        sql_request = ("SELECT "
                       "Orders.id, Orders.id_voyage, Clients.fio, Clients.number, Orders.weight, "
                       "Tariffs.type_of_product, Tariffs.price, "
                       "GROUP_CONCAT(aas.service_name) AS additional_services "
                       "FROM Orders "
                       "INNER JOIN Clients ON Orders.client_recipient = Clients.number "
                       "INNER JOIN Tariffs ON Orders.id_tariff = Tariffs.id "
                       "LEFT JOIN OrdersAndAdditionalServices oas ON Orders.id = oas.id_order "
                       "LEFT JOIN AdditionalServices aas ON oas.id_additional_service = aas.id "
                       "WHERE Orders.client_sender = %s "
                       "GROUP BY Orders.id, Orders.id_voyage, Clients.fio, Clients.number, "
                       "Orders.weight, Tariffs.type_of_product, Tariffs.price "
                       "ORDER BY Orders.id DESC;")
        try:
            dto.cursor.execute(sql_request, (dto.user_phone,))
            result = dto.cursor.fetchall()
        except mysql.connector.Error as err:
            logger.error(f"Error get orders data from database\n{err}")
            return None
        else:
            if result is not None:
                return result
            else:
                return ()

    @staticmethod
    def view_voyages(dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Voyages")
            result = dto.cursor.fetchall()
        except mysql.connector.Error:
            logger.error("Error get voyages data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_voyages_by_user(dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])):
        sql_request = ("SELECT Voyages.id, port_departure.country, port_departure.city, "
                       "port_arrival.country, port_arrival.city, "
                       "Voyages.date_departure, Voyages.date_arrival, Statuses.status_name, Voyages.max_weight "
                       "FROM Voyages "
                       "INNER JOIN Ports port_departure ON Voyages.port_of_departure=port_departure.id "
                       "INNER JOIN Ports port_arrival ON Voyages.port_of_arrival=port_arrival.id "
                       "INNER JOIN Statuses ON Voyages.id_status=Statuses.id;")
        try:
            dto.cursor.execute(sql_request)
            result = dto.cursor.fetchall()
        except mysql.connector.Error:
            logger.error("Error get voyages data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_tariffs(dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Tariffs")
            result = dto.cursor.fetchall()
        except mysql.connector.Error:
            logger.error("Error get tariffs data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_ports(dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Ports")
            result = dto.cursor.fetchall()
        except mysql.connector.Error:
            logger.error("Error get ports data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_statuses(dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Statuses")
            result = dto.cursor.fetchall()
        except mysql.connector.Error:
            logger.error("Error get statuses data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_clients(dto: namedtuple('dto', ['user_phone', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Clients;")
            result = dto.cursor.fetchall()
        except mysql.connector.Error:
            logger.error("Error get clients data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_additional_services(dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM AdditionalServices")
            result = dto.cursor.fetchall()
        except mysql.connector.errors:
            logger.error("Error get tariffs data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_orders_and_additional_services(data, dto: namedtuple('dto',['user_id',
                                                                                 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT id FROM Orders WHERE client_sender=%s", data)
            result = dto.cursor.fetchall()
        except mysql.connector.errors:
            logger.error("Error get orders id from database (in getting orders and additional services)")
            return None
        else:
            if result is not None:
                return 0

        try:
            dto.cursor.execute("SELECT * FROM OrdersAndAdditionalServices WHERE client_sender IN (%s)", *data)
            result = dto.cursor.fetchall()
        except mysql.connector.errors:
            logger.error("Error get orders and additional services data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def add_order_and_additional_service(data: tuple[int, int],
                  dto: namedtuple('dto',['user_phone', 'connection', 'cursor'])) -> bool:
        try:
            insert_query = """INSERT INTO OrdersAndAdditionalServices (id_order, id_additional_service) 
            SELECT %s, %s 
            WHERE EXISTS 
            (SELECT 1 FROM Orders WHERE Orders.client_sender = %s limit 1);"""
            dto.cursor.execute(insert_query, (*data, dto.user_phone))
            dto.connection.commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    # admin
    @staticmethod
    def add_additional_services(data: tuple[str, int],
                                dto: namedtuple('dto', ['user_phone', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO AdditionalServices (service_name, price) 
                                    VALUES (%s, %s) """
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def add_client_services(data: tuple[str, str],
                                dto: namedtuple('dto', ['user_phone', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Clients (fio, number) 
                                    VALUES (%s, %s) """
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def add_port(data: tuple[str, str, str],
                                dto: namedtuple('dto', ['user_phone', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Ports (port_name, country, city) 
                                    VALUES (%s, %s, %s);"""
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def add_status(data: tuple[str],
                                dto: namedtuple('dto', ['user_phone', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Statuses (status_name) 
                                    VALUES (%s);"""
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def add_tariff(data: tuple[str, int],
                                dto: namedtuple('dto', ['user_phone', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Tariffs (type_of_product, price) 
                                    VALUES (%s, %s);"""
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def add_voyage(data: tuple[int, int, str, str, int, int],
                                dto: namedtuple('dto', ['user_phone', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Voyages (port_of_departure, port_of_arrival, date_departure, date_arrival,
            id_status, max_weight) 
            VALUES (%s, %s, %s, %s, %s, %s);"""
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True
