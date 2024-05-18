import requests
import time
from .util import display_progress, write_to_excel

offset = 0
limit = 200
products = []

url = "https://gql.tokopedia.com/graphql/SearchProductQueryV4"
querySchema = """
query SearchProductQueryV4($params: String!) {
  ace_search_product_v4(params: $params) {
    data {
      products {
        id
        name
        ads {
          adsId: id
          productClickUrl
          productWishlistUrl
          productViewUrl
          __typename
        }
        badges {
          title
          imageUrl
          show
          __typename
        }
        category: departmentId
        categoryBreadcrumb
        categoryId
        categoryName
        countReview
        customVideoURL
        discountPercentage
        gaKey
        imageUrl
        labelGroups {
          position
          title
          type
          url
          __typename
        }
        originalPrice
        price
        priceRange
        rating
        ratingAverage
        shop {
          shopId: id
          name
          url
          city
          isOfficial
          isPowerBadge
          __typename
        }
        url
        wishlist
        sourceEngine: source_engine
        warehouseIdDefault
        __typename
      }
      violation {
        headerText
        descriptionText
        imageURL
        ctaURL
        ctaApplink
        buttonText
        buttonType
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

def scrape(phrase, page):
    global products
    global offset

    response = requests.post(url=url, json={
    "query": querySchema, 
    "variables": {"params": "device=desktop&navsource=&ob=23&page={0}&q={1}&related=true&rows={2}&safe_search=false&scheme=https&shipping=&show_adult=false&source=search&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&st=product&start={3}&topads_bucket=true&unique_id=4272eb71aad7cc24f87231b1889f51f5&user_addressId=&user_cityId=176&user_districtId=2274&user_id=&user_lat=&user_long=&user_postCode=&user_warehouseId=12210375&variants=&warehouses=12210375%232h%2C16699633%23fc".format(page, phrase, limit, offset)
    }}, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.tokopedia.com/search?st=&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&navsource="
    }) 

    if response.status_code == 200: 
        data = response.json()
        for product in data['data']['ace_search_product_v4']['data']['products']:
            products.append({
                'id': product['id'],
                'name': product['name'],
                'category': product["categoryName"],
                'brand': product['shop']['name'],
                'price': ''.join(filter(str.isdigit, product['price'])),
                'image_url': product['imageUrl'],
                'rating': product['ratingAverage'],
                'url': product['url'],
            })
    else:
        print('Failed to fetch page ' + str(page))
    
    time.sleep(0.5)

    offset = limit * page
    page += 1

def scrape_tokopedia(max_page, phrase):
    global offset
    page = 1
    
    while page <= max_page:
        scrape(phrase, page)
        display_progress(page, max_page, 100)

        time.sleep(0.5)

        offset = limit * page
        page += 1
        
    write_to_excel(products, './ui_data/tokopedia.xlsx')

    products.clear()

    print("\nScrapping Finished Tokopedia!")
