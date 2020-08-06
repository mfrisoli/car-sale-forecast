from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
from re import sub
import pandas as pd
import timeit

with open('url.txt', 'r') as f:
    url = f.read()
    # Load Fist PageOpen connection and download HTML page
    uClient = uReq(url)
    page_soup = soup(uClient.read(), "html.parser")
    uClient.close()

i = 0
success = 0
errors = 0
pages_scrapped = 0
data_set = list()
page = 0

start_time = timeit.default_timer()

while True:
    try:
        # Get only car Data From the HMTL CODE
        containers = page_soup.findAll('li', {"class": "card-item"})

        # Loop for all cars in current page
        for row in containers:

            car = dict()

            # Get ad url
            ad_url = row.a['href']

            car['ad_name'] = row.find('p', {'class': 'card__body-title'}).text

            # Price
            car['price'] = row.find('p', {'class': 'card__price'}).text

            # Get ad and store it in a STR
            uClient = uReq(ad_url)
            ad_soup = str(soup(uClient.read(), "html.parser"))
            uClient.close()
            try:
                # Extract Ad key details dictionary
                start = ad_soup.find('"displayAttributes"') 
                end = ad_soup.find('"publisherName"')
                ad_soup = ad_soup[start:end]
                start = ad_soup.find(r'[{"')
                end = ad_soup.find(r'}}],')
                ad_soup = ad_soup[start:end + 3]
                # Convert String Dic to Dictionary
                ad_soup = ad_soup.replace('false', 'False')
                ad_soup_dic = eval(ad_soup)
                for row in ad_soup_dic:
                    car[str(row["name"])] = row['value']

                data_set.append(car)
                success += 1

                #print(f'{i} -> SUCCESS')

            except:
                errors += 1
                #print(f'{i} -> ERROR')
                pass

            i += 1

        # add 28 to load next set
        page += 28

        # Load Next Page
        page_url = url + '?start=' + str(page)

        # Open connection and download HTML page
        uClient = uReq(page_url)
        page_soup = soup(uClient.read(), "html.parser")
        uClient.close()
        pages_scrapped += 1
        print(f'Pages Scrapped: {pages_scrapped}')

    except:
        errors += 1
        # add 28 to load next set
        page += 28

        # Load Next Page
        page_url = url + '?start=' + str(page)

        pass
    
    if pages_scrapped > 1000:
        break
        
end_time = timeit.default_timer()

# Print Results of scrapping
print(f'Run Time: {end_time - start_time} secods')
print(f'Pages Scrapped: {pages_scrapped}')
print(f'Succes: {success}')
print(f'Errors: {errors}')

df = pd.DataFrame(data_set)

df.to_csv('car_data.csv')