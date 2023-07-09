import re
import pandas as pd

class DataPreparer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataPreparer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def clean_prices(price):
        match = re.search(r"R\$(.+)", price)
        if match:
            cleaned_price = match.group(1).strip()
            return cleaned_price
        else:
            return ''

    @staticmethod
    def prepare_data(dataframe, config):
        prepared_data = []
        for _, row in dataframe.iterrows():
            title = row['title']
            price = DataPreparer.clean_prices(row['price'])
            url = row['url']
            store = row['website']
            query = row['query']

            if store not in url:
                url = config['base_url'] + url

            prepared_data.append({
                'title': title,
                'price': price,
                'url': url,
                'website': store,
                'query': query
            })
        df = pd.DataFrame(prepared_data)
        return df
