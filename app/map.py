import pandas as pd

def get_transaction_count(secret_key):
    url = 'https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY=' + secret_key
    try:
        df = pd.read_json(url, typ='series')
        count = df.get('current_transactions', 0)
    except Exception as e:
        print("Error in our call:", str(e))
        count = 0
    return count
