import pymysql


def getconnection(server_data):
    """
    parameters already fixed inside the function
    :return: the connection to the server
    """
    connection = pymysql.connect(charset='utf8', cursorclass=pymysql.cursors.DictCursor, **server_data)
    return connection
