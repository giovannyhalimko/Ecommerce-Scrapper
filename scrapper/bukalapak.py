from selenium import webdriver
import json
import requests
from util import display_progress, write_to_excel
import time

access_token = ''
products = []
page = 1
phrase = ''
api_url = "https://api.bukalapak.com/multistrategy-products"
fronted_url = "https://www.bukalapak.com/"

class LocalStorage:
    def __init__(self, driver) :
        self.driver = driver

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def get(self, key):
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def __getitem__(self, key) :
        value = self.get(key)
        if value is None :
          raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return self.items().__iter__()

    def __repr__(self):
        return self.items().__str__()
    
def obtain_access_token():
    print("Obtaining access token...")
    global access_token

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    driver.get(fronted_url)

    time.sleep(3)

    local_storage = LocalStorage(driver)
    bl_token = local_storage.get("bl_token")
    access_token = json.loads(bl_token)["access_token"]

    print("Access token obtained, Begin scrapping...")

    driver.quit()
    
def scrape():
    global page
    global products
    global phrase
    global access_token
    
    parameter = {
        'prambanan_override': True,
        'keywords': phrase,
        'limit': 50,
        'offset': 50,
        'page': page,
        'facet': True,
        'access_token': access_token
    }

    response = requests.get(api_url, params=parameter)
    if response.status_code == 200:
        data = response.json()

        for p in data['data']:
            product = {
                'id': p['id'],
                'name': p['name'],
                'category': p['category']['name'],
                'price': p['price'],
                'image_url': p['images']['large_urls'][0],
                'rating': p['rating']['average_rate'],
            }

            if 'brand' in p['specs'].keys():
                product['brand'] = str(p['specs']['brand'])
            else:
                product['brand'] = "-"

            products.append(product)
    else:
        print('Failed to fetch page ' + str(page))

    time.sleep(0.5)

    page += 1

while True:
    phrase = input('What do you want to search ? : ')
    if not phrase:
        print('Query cannot be empty')
        continue

    max_page = int(input('How many page you want to fetch ? (max 100): '))
    if max_page > 100:
        print('Max page is 100')
        continue
    break

obtain_access_token()
        
while page <= max_page:
    scrape()
    display_progress(page, max_page, 100)

write_to_excel(products, '../data/bukalapak.xlsx')

print("\nScrapping Finished!")