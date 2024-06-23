import mysql.connector  # Importamos la librería instalada
try:
    # Nos conectamos con la base de datos 'demo'
    database = mysql.connector.connect(
        host = "localhost",
        user = 'root',
        password = 'Haruko_13',
        database = 'demo',
        port = '3306'
    )
    # Verificamos que se haya realizado la conexión e imprimimos los resultados
    if database.is_connected():
        print("Conexión exitosa")
        mysql_cursor = database.cursor()
        mysql_cursor.execute("SELECT DATABASE()")
        print("Conectado con la base de datos: {}". format(mysql_cursor.fetchone()))


# En caso de algún error, se imprimirá la excepción correspondiente
except Exception as ex:
    print(ex)
