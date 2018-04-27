import pandas as pd
from MySQL.connection import getconnection
import pymysql
import time
from bson import json_util


def get_top_by_country(country, limit, connection_credentials_files):
    df = pd.DataFrame(columns=['topProgramsCountry_fkprogram', 'topProgramsCountry_position',
                               'audio_description', 'audio_fkprogram', 'audio_title'])

    try:
        with open(connection_credentials_files, 'r') as f:
            connection_credentials = json_util.loads(f.read())
    except IOError:
        raise Exception('Wrong credential file')

    try:
        connection = getconnection(connection_credentials)
        query = 'SELECT topProgramsCountry_fkprogram, topProgramsCountry_position ' \
                'FROM ivoox.topProgramsCountry WHERE topProgramsCountry_fkorigin = %d ' \
                'ORDER BY topProgramsCountry_position ASC LIMIT %d'
        df = pd.read_sql(query % (country, limit), connection)
        connection.close()
    except pymysql.DataError as e:
        print("DataError")
        print(e)
    except pymysql.InternalError as e:
        print("InternalError")
        print(e)
    except pymysql.IntegrityError as e:
        print("IntegrityError")
        print(e)
    except pymysql.OperationalError as e:
        print("OperationalError")
        print(e)
    except pymysql.NotSupportedError as e:
        print("NotSupportedError")
        print(e)
    except pymysql.ProgrammingError as e:
        print("ProgrammingError")
        print(e)
    except Exception as e:
        print(e)
        print("Unknown error occurred")
    return df.topProgramsCountry_fkprogram.values


def get_data(programs, connection_credentials_files):
    query = 'SELECT programs_id, programs_name, programs_description ' \
            'FROM ivoox.programs ' \
            'WHERE programs_id = %d'

    df = pd.DataFrame(
        columns=['programs_id', 'programs_name', 'programs_description'])

    try:
        with open(connection_credentials_files, 'r') as f:
            connection_credentials = json_util.loads(f.read())
    except IOError:
        raise Exception('Wrong credential file')

    try:
        connection = getconnection(connection_credentials)
        cur = connection.cursor()
        count = 0
        for i in programs:
            count += 1
            cur.execute(query % i)
            current = cur.fetchone()
            df = df.append(current, ignore_index=True)
            if count % 100 == 0:
                time.sleep(5)
        connection.close()

    except pymysql.DataError as e:
        print("DataError")
        print(e)
    except pymysql.InternalError as e:
        print("InternalError")
        print(e)
    except pymysql.IntegrityError as e:
        print("IntegrityError")
        print(e)
    except pymysql.OperationalError as e:
        print("OperationalError")
        print(e)
    except pymysql.NotSupportedError as e:
        print("NotSupportedError")
        print(e)
    except pymysql.ProgrammingError as e:
        print("ProgrammingError")
        print(e)
    except Exception as e:
        print(e)
        print("Unknown error occurred")

    df.columns = ['id', 'title', 'description']
    return df


def get_more_data(programs, connection_credentials_files, episodes=20):
    sleep_count = 0
    query = 'SELECT audio_fkprogram, audio_title, audio_description ' \
            'FROM ivoox.audio ' \
            'WHERE audio_fkprogram = %d ' \
            'ORDER BY RAND() ' \
            'LIMIT %d'

    df = pd.DataFrame(
        columns=['audio_fkprogram', 'audio_title', 'audio_description'])

    try:
        with open(connection_credentials_files, 'r') as f:
            connection_credentials = json_util.loads(f.read())
    except IOError:
        raise Exception('Wrong credential file')

    try:
        connection = getconnection(connection_credentials)
        cur = connection.cursor()

        n = 0
        for i in programs:
            sleep_count += 1
            cur.execute(query % (i, episodes))
            while n < episodes:
                n += 1
                current = cur.fetchone()
                if current is None:
                    break
                df = df.append(current, ignore_index=True)
            n = 0
            if sleep_count % 100 == 0:
                time.sleep(1)
        connection.close()

    except pymysql.DataError as e:
        print("DataError")
        print(e)
    except pymysql.InternalError as e:
        print("InternalError")
        print(e)
    except pymysql.IntegrityError as e:
        print("IntegrityError")
        print(e)
    except pymysql.OperationalError as e:
        print("OperationalError")
        print(e)
    except pymysql.NotSupportedError as e:
        print("NotSupportedError")
        print(e)
    except pymysql.ProgrammingError as e:
        print("ProgrammingError")
        print(e)
    except Exception as e:
        print(e)
        print("Unknown error occurred")

    df.columns = ['id', 'title', 'description']
    return df
