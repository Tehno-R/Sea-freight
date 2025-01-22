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

    cursor.execute("SELECT id FROM Clients WHERE number=%s", (number,))
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
            self._user_id = connection._user_id
        else:
            self._connection = self._cursor = self._current_user = self._user_id = None

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
                id_user = check_number(number[1:])
                if id_user is not None:
                    self._connection = mysql.connector.connect(
                        host='localhost',
                        user=self._usernames[1],
                        password='',
                        database='Transportations'
                    )
                    self._current_user = self._usernames[1]
                    self._user_id = id_user[0] # Возвращается либо (user id,) либо None (которые обрабатывается выше)
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
        self._connection = self._cursor = self._current_user = self._user_id = None

    def get_dto(self):
        return (namedtuple('dto',['user_id', 'connection', 'cursor'])
                (self._user_id, self._connection, self._cursor))

    # user
    @staticmethod
    def add_order(data: tuple[int, int, int, int, int],
                  dto: namedtuple('dto',['user_id', 'connection', 'cursor'])) -> bool:
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
                     dto: namedtuple('dto',['user_id', 'connection', 'cursor'])) -> int:
        try:
            insert_query = """DELETE FROM Orders WHERE id=%s AND client_sender=%s"""
            dto.cursor.execute(insert_query, data)
            dto.connection.commit()

            result = dto.cursor.rowcount
        except Exception as err:
            logger.error(err)
            return 0
        return result

    @staticmethod
    def view_orders(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Orders WHERE client_sender=%s", (dto.user_id, ))
            result = dto.cursor.fetchall()
        except mysql.connector.errors as err:
            logger.error("Error get orders data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_voyages(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Voyages")
            result = dto.cursor.fetchall()
        except Exception as err:
            logger.error("Error get voyages data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_tariffs(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Tariffs")
            result = dto.cursor.fetchall()
        except Exception as err:
            logger.error("Error get tariffs data from database")
            return None
        else:
            if result is not None:
                return result
            else:
                return 0

    @staticmethod
    def view_additional_services(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
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
                result = 0

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


    # admin
    @staticmethod
    def add_additional_services(data: tuple[str, int],
                                dto: namedtuple('dto', ['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO AdditionalServices (servic_name, price) 
                                    VALUES (%s, %s) """
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()
        except mysql.connector.errors as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def delete_additional_services_by_admin(data: tuple[int], dto: namedtuple('dto',['user_id',
                                                                                     'connection', 'cursor'])):
        try:
            insert_query = """DELETE FROM AdditionalServices WHERE id=%s"""
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()

            result = dto.cursor.rowcount
            if result is None:
                return 0
            else:
                return result[0]
        except Exception as err:
            logger.error(err)
            return None

    @staticmethod
    def view_additional_services_by_admin(dto: namedtuple('dto',['user_id',
                                                                 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM AdditionalServices")
            result = dto.cursor.fetchall()
            if result is not None:
                return result
            else:
                return 0
        except mysql.connector.errors as err:
            logger.error("Error get additional services data from database")
            return None

    @staticmethod
    def add_clients_by_admin(data: tuple[str, str],
                             dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Clients (fio, number) 
                                    VALUES (%s, %s) """
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()
        except mysql.connector.errors as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def delete_clients_by_admin(data: tuple[int],
                                dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """DELETE FROM Clients WHERE id=%s"""
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()

            result = dto.cursor.rowcount
            if result is None:
                return 0
            else:
                return result[0]
        except Exception as err:
            logger.error(err)
            return None

    @staticmethod
    def view_clients_by_admin(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Clients")
            result = dto.cursor.fetchall()
            if result is not None:
                return result
            else:
                return 0
        except mysql.connector.errors as err:
            logger.error("Error get clients data from database")
            return None

    @staticmethod
    def add_ports_by_admin(data: tuple[str, str, str],
                           dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Ports (port_name, country, city) 
                                    VALUES (%s, %s, %s) """
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()
        except mysql.connector.errors as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def delete_ports_by_admin(data: tuple[int],
                              dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """DELETE FROM Ports WHERE id=%s"""
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()

            result = dto.cursor.rowcount
            if result is None:
                return 0
            else:
                return result[0]
        except Exception as err:
            logger.error(err)
            return None

    @staticmethod
    def view_ports_by_admin(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Ports")
            result = dto.cursor.fetchall()
            if result is not None:
                return result
            else:
                return 0
        except mysql.connector.errors as err:
            logger.error("Error get clients data from database")
            return None

    @staticmethod
    def add_statuses_by_admin(data: tuple[str],
                              dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Ports (status_name) 
                                    VALUES (%s) """
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()
        except mysql.connector.errors as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def delete_statuses_by_admin(data: tuple[int],
                                 dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """DELETE FROM Statuses WHERE id=%s"""
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()

            result = dto.cursor.rowcount
            if result is None:
                return 0
            else:
                return result[0]
        except mysql.connector.errors as err:
            logger.error(err)
            return None

    @staticmethod
    def view_statuses_by_admin(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Ports")
            result = dto.cursor.fetchall()
            if result is not None:
                return result
            else:
                return 0
        except mysql.connector.errors as err:
            logger.error("Error get clients data from database")
            return None

    @staticmethod
    def add_tariffs_by_admin(data: tuple[str, int],
                             dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Ports (type_of_product, price) 
                                    VALUES (%s, %s) """
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()
        except mysql.connector.Error as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def delete_tariffs_by_admin(data: tuple[int],
                                dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """DELETE FROM Tariffs WHERE id=%s"""
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()

            result = dto.cursor.rowcount
            if result is None:
                return 0
            else:
                return result[0]
        except mysql.connector.errors as err:
            logger.error(err)
            return None

    @staticmethod
    def view_tariffs_by_admin(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Tariffs")
            result = dto.cursor.fetchall()
            if result is not None:
                return result
            else:
                return 0
        except mysql.connector.errors as err:
            logger.error("Error get clients data from database")
            return None

    @staticmethod
    def add_voyages_by_admin(data:tuple[int, int, str, str, int, int],
                             dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """INSERT INTO Ports (port_of_departure, port_of_arrival, data_departure, data_arrival,
                                                        id_status, max_weight) 
                                VALUES (%s, %s, %s, %s, %s, %s) """
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()
        except mysql.connector.errors as err:
            logger.error(err)
            return False
        return True

    @staticmethod
    def delete_voyages_by_admin(data: tuple[int],
                                dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            insert_query = """DELETE FROM Voyages WHERE id=%s"""
            dto.cursor.execute(insert_query, data)
            dto: namedtuple('dto',['user_id', 'connection', 'cursor'])[0].commit()

            result = dto.cursor.rowcount
            if result is None:
                return 0
            else:
                return result[0]
        except mysql.connector.errors as err:
            logger.error(err)
            return None

    @staticmethod
    def view_voyages_by_admin(dto: namedtuple('dto',['user_id', 'connection', 'cursor'])):
        try:
            dto.cursor.execute("SELECT * FROM Voyages")
            result = dto.cursor.fetchall()
            if result is not None:
                return result
            else:
                return 0
        except mysql.connector.errors as err:
            logger.error("Error get clients data from database")
            return None
