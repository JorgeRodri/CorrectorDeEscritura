from MySQL.connection import getconnection
import pandas as pd
from bson import json_util

connection_credentials = 'credenciales_server.json'

query = 'SELECT * FROM ivoox.zeroresultsearch WHERE ' \
        '(zeroresultsearch_date > "2018-04-03" AND zeroresultsearch_date < "2018-05-03")'

with open(connection_credentials, 'r') as f:
    connection_credentials = json_util.loads(f.read())

df = pd.read_sql(query, getconnection(connection_credentials))

pd.to_pickle(df, 'zero_search.pkl')

