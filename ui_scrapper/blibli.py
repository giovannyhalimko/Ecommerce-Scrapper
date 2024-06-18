import time
from .util import display_progress, write_to_excel
from seleniumbase import Driver
import json


# Perubahan dari sebelumnya
# Blibli melakukan pembaruan terhadap keamanan API untuk mengambil data, dimana kami tidak menemukan cara untuk mereplikasi cara melakukan request ke server mereka diluar browser,
# Sehingga diperlukan mekanisme untuk mereplikasi perilaku browser untuk melakukan scraping data dari Blibli
# Dalam hal ini data scrapping dilakukan dengan menggunakan SeleniumBase yang merupakan library yang memungkinkan kita untuk melakukan automation testing pada website
# Data hasil scrapping diambil melalui CDP (Chrome DevTools Protocol) yang memungkinkan kita untuk mengakses data yang diambil oleh browser
# Setelah browser mendapatkan data, kita akan melakukan URL matching untuk mencari URL yang mengandung data yang kita cari dan mengambil response body dari URL tersebut
# Hal ini diperlukan interaksi eksplisit terhadap CDP (Chrome DevTools Protocol) untuk mengambil data dari browser

products = []

blibli_searching_base_api_url = "https://www.blibli.com/backend/search/products"
    
def process_cdp_event(data, driver):
    event_type = data.get("method")

    # kita melakukan pengecekan apakah event yang terjadi adalah Network.requestWillBeSent
    if event_type == "Network.requestWillBeSent":

        # kita mengambil request url dari event tersebut
        request_url = data["params"]["request"]["url"]

        # kita melakukan pengecekan apakah request url tersebut mengandung blibli_searching_base_api_url
        if blibli_searching_base_api_url in request_url:

            # jika iya, maka kita akan mencetak request url tersebut
            print(f"Matching request URL: {request_url}")

    # kita melakukan pengecekan apakah event yang terjadi adalah Network.responseReceived
    elif event_type == "Network.responseReceived":

        # kita mengambil response url dari event tersebut
        response_url = data["params"]["response"]["url"]

        # kita melakukan pengecekan apakah response url tersebut mengandung blibli_searching_base_api_url
        if blibli_searching_base_api_url in response_url:

            # jika iya, maka kita mengambil request id dari event tersebut
            request_id = data["params"]["requestId"]

            # setelah itu kita akan mengambil response body dari request tersebut 
            # caranya adalah dengan menggunakan cdp command Network.getResponseBody dan mengirimkan request id tersebut
            # maka kita akan mendapatkan response body dari request tersebut
            response = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})

            # kita melakukan pengecekan apakah response body tersebut ada atau tidak
            if response is None:
                print("No response body found")
            else:
                # Jika ada maka kita akan mengambil nya dan simpan ke dalam variabel response_body
                if "body" in response:
                    response_body = response["body"]
                    
                    try:
                        # disini kita akan mencoba untuk melakukan parsing terhadap response body tersebut kedalam bentuk json
                        response_json = json.loads(response_body)
                        for product in response_json['data']['products']:
                            products.append({
                                'id': product['id'],
                                'name': product['name'],
                                'category': product["rootCategory"]["name"],
                                'brand': product['brand'],
                                'price': product['price']["minPrice"],
                                'image_url': product['images'][0],
                                'rating': product['review']['absoluteRating'],
                                'url': 'https://www.blibli.com' + product['url'],
                            })

                    # jika gagal melakukan parsing, maka akan muncul error
                    except json.JSONDecodeError:
                        print("Failed to parse the response body as JSON.")


def scrape(driver, phrase, page):
    base_url = 'https://www.blibli.com/backend/search/products?page=' + str(page) + '&start=0&searchTerm=' + phrase

    # memasangkan event listener untuk CDP (Chrome DevTools Protocol) agar kita dapat mengakses data yang diambil oleh browser
    driver.add_cdp_listener("*", lambda data: process_cdp_event(data, driver))
    driver.open(base_url)

    # force reload untuk metrigger Chrome melakukan request ke server agar CDP dapat menangkap event yang terjadi
    driver.execute_script("location.reload(true);")
    time.sleep(1.2)

def scrape_blibli(max_page, phrase):
    page = 1
    global products
    products = []

    # mendefinisikan driver yang akan digunakan (seleniumbase)
    with Driver(undetectable=True, uc_cdp_events=True, headless=False, uc=True) as driver:
        while page <= max_page:
            scrape(driver, phrase, page)
            display_progress(page, max_page, 100)

            page += 1
            time.sleep(0.5)
        write_to_excel(products, './ui_data/blibli.xlsx')

    driver.quit()
        
    print("\nScrapping Finished Blibli!")