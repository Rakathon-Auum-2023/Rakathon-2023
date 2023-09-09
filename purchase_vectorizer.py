# create a unit vector representing the purchases made by a customer. THe category_prices.json file is a prerequisite for this module.

# the category_prices.json contains a distribution of prices of the products from a business category. This helps us to get the relative 
# positioning of any new product in terms of the already existing ones

import numpy as np
from fuzzywuzzy import process
from scipy.stats import percentileofscore

class PurchaseVectorizer:
    def __init__(self, category_prices, category_column = 'category', price_column = 'price', product_column = 'product_id'):
        self.category_prices = category_prices
        self.category_column = category_column
        self.price_column = price_column
        self.product_column = product_column
    
    def spell_rectifier(self, name):
        return process.extractOne(name, self.category_prices.keys())

    def get_category_prices(self, category_name):
        if category_name in self.category_prices:
            return self.category_prices[category_name]
        else:
            possible_category_name, score = self.spell_checker(category_name)
            if score<80:
                return []
            return self.category_prices[possible_category_name]
    
    
    def get_percentile_class(self, price, category_name):
        prices = self.get_category_prices(category_name)
        if prices == []:
            return -1
        percentile = percentileofscore(prices, price)

        if percentile<=25:
            return 0
        if percentile<=70:
            return 1
        return 2

    def data_to_vector(self, data):
        vector = np.zeros(3, dtype = int)
        for _, row in data.iterrows():
            p_class = self.get_percentile_class(row['price'], row['category'])
            if p_class>=0:
                vector[p_class]+=1
        vector = np.round(vector/math.sqrt(sum(vector*vector)), 3)
        return tuple(vector)
