from MySQL.connection import getconnection
import pandas as pd
from bson import json_util
import time


def get_values(connection_credentials_files, ini_date, final_date):
    platforms = ['ANDROID', 'IOS']
    user_type = ['STANDARD', 'FACEBOOK', 'GOOGLE']
    query = 'SELECT * FROM ivoox.user JOIN useraccess ON useraccess_fkuser = user_id WHERE ' \
            'user_registerdate > "{0}" AND user_registerdate < "{1}" ' \
            'AND useraccess_platform = "{2}" ' \
            'AND user_type = "{3}"'
    fin = {}

    with open(connection_credentials_files, 'r') as f:
        connection_credentials = json_util.loads(f.read())
    connection = getconnection(connection_credentials)
    for platform in platforms:
        fin[platform] = dict()
        for utype in user_type:
            df = pd.read_sql(query.format(ini_date, final_date, platform, utype), connection)
            fin[platform][utype] = df['user_id'].nunique()
            time.sleep(5)
            print('%s %s: %d' % (platform, utype, fin[platform][utype]))
    return fin


if __name__ == '__main__':
    arch = 'credenciales_server.json'
    print(get_values(arch, '2018-04-01', '2018-05-02'))
