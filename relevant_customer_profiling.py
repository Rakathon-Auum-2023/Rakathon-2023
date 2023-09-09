# this will give you relevant customers for a real estate business based on customer data (we have used salary and location, which are the major factors)

import requests, math
from tqdm import tqdm
tqdm.pandas()

class MapPropertyToCustomer:
    api_key = 'b830155d756677116bcc85d10eee2001'
    def __init__(self, property_cost, locality_lat, locality_lon):
        self.property_cost = property_cost
        self.locality_lat = locality_lat
        self.locality_lon = locality_lon
    
    def calculate_distance(self, dest_lat, dest_lon):
        response = requests.get(f'https://apis.mappls.com/advancedmaps/v1/{self.api_key}/distance_matrix/driving/{self.locality_lat},{self.locality_lon};{dest_lat},{dest_lon};17ZUL7??sources=0&destinations=1')
        distance1 = response.json()['results']['distances'][0][0]
        response = requests.get(f'https://apis.mappls.com/advancedmaps/v1/{self.api_key}/distance_matrix/driving/{dest_lat},{dest_lon};{self.locality_lat},{self.locality_lon};17ZUL7??sources=0&destinations=1')
        distance2 = response.json()['results']['distances'][0][0]

        return round((distance1+distance2)/2000, 1)
    
    def customer_property_correlation(self, customer_monthly_income, customer_residence_lat, customer_residence_lon, customer_workplace_lat, customer_workplace_lon):
        residence_locality_dist = self.calculate_distance(customer_residence_lat, customer_residence_lon)
        workplace_locality_dist = self.calculate_distance(customer_workplace_lat, customer_workplace_lon)/100
        proximity_score = (1/(1+math.e**residence_locality_dist) + 1/(1+math.e**workplace_locality_dist)) * 2

        emi_value = self.property_cost * 0.0075*(1.0075**240)/(1.0075**240-1)
        emi_salary_ratio = round(emi_value/customer_monthly_income, 3)
        loan_salary_ratio = round(self.property_cost/(customer_monthly_income*1000), 3)
        monetary_score = 1/(1+math.e**emi_salary_ratio) + 1/(1+math.e**loan_salary_ratio)

        return proximity_score + monetary_score
        
    
    def get_customer_matches(self, customer_df, count = 10, customer_residence_lat_col = 'residence_lat', customer_residence_lon_col = 'residence_lon', 
                             customer_workplace_lat_col = 'workplace_lat', customer_workplace_lon_col = 'workplace_lon', customer_salary_col = 'salary',
                             monthly = True):
        customer_df.drop_duplicates(inplace=True)
        if not monthly:
            customer_df[customer_salary_col] /= 12
        
        customer_df['property_correlation_score'] = customer_df.progress_apply(lambda x: self.customer_property_correlation(customer_monthly_income=x[customer_salary_col],
                                                                                                                            customer_residence_lat= x[customer_residence_lat_col],
                                                                                                                            customer_residence_lon= x[customer_residence_lon_col],
                                                                                                                            customer_workplace_lat= x[customer_workplace_lat_col],
                                                                                                                            customer_workplace_lon= x[customer_workplace_lon_col]), axis = 1)
        
        best_matches = customer_df.sort_values(by = 'property_correlation_score', ascending = False).iloc[:10]

        return best_matches