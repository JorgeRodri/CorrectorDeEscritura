from bson import json_util
import pandas as pd
from io import open


def load_ham(file_name):
    with open(file_name, 'r', encoding='utf8') as fly:
        data = json_util.loads(fly.read())
    df = pd.DataFrame(data)

    df.columns = ['audio_description', 'audio_duration', 'audio_fksubcategory',
                  'audio_fkaudio', 'audio_title']
    df['audio_description'] = df['audio_description'].apply(lambda x: x.replace('\n', ''))
    df['audio_description'] = df['audio_description'].apply(lambda x: x.replace('\r', ''))

    df['label'] = 0
    return df
