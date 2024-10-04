import psycopg2
from psycopg2 import Error

db_server_user = "postgres"
db_server_host = "localhost"
db_sever_port = "5432"
db_server_password = "127238"
db_server_name = "tele_storage"


def test_connection():
    try:
        connection = psycopg2.connect(user=db_server_user,
                                      # пароль, который указали при установке PostgreSQL
                                      password=db_server_password,
                                      host=db_server_host,
                                      port=db_sever_port,
                                      database=db_server_name)

        cursor = connection.cursor()
        print("Информация о сервере PostgreSQL", cursor)
        print(connection.get_dsn_parameters(), "\n")
        cursor.execute("SELECT version();")

        record = cursor.fetchone()
        print("Вы подключены к - ", record, "\n")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


if __name__ == "__main__":
    test_connection()
