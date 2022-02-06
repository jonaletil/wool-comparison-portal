import time
import requests
import pandas as pd
from wool import Wool
from website import Website
from container import Container
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask('Wool App')
engine = create_engine('sqlite:///result_data.db')

delivery_url = 'https://www.wollplatz.de/versandkosten-und-lieferung'
wool_json = pd.read_json('wool_data.json')
wool_df = pd.DataFrame(wool_json)

wool_item = Wool()

price_container = Container('span', 'class', 'product-price-amount')
needle_size_container = Container('td', 'string', 'Nadelstärke')
composition_container = Container('td', 'string', 'Zusammenstellung')

website_1 = Website("https://www.wollplatz.de/wolle", "https://www.wollplatz.de/wolle?page=", 28, price_container,
                    needle_size_container, composition_container)
website_2 = Website("https://www.wollplatz.de/wolle", "https://www.wollplatz.de/wolle?page=", 20, price_container,
                    needle_size_container, composition_container)

product_links = []


def get_product_links(website):
    print('Collecting product links...')
    start_time = time.time()

    for i in range(1, website.page_num + 1):
        if i == 1:
            url = website.base_url
        else:
            url = website.pagination_url + str(i)

        soup = get_soup(url)

        for x in range(len(wool_df)):
            title = wool_df.brand[x] + ' ' + wool_df.name[x]
            item = soup.find("a", title=str(title))

            if item:
                link = item.get('href')
                product_links.append(link)

        if i == website.page_num:
            print_time(start_time)
            print('-' * 40)
            get_product_data(product_links)


def get_product_data(urls):
    data = []
    print('Collecting product data...')
    start_time = time.time()
    for url in urls:
        soup = get_soup(url)

        delivery = get_delivery_info(soup)
        properties_table = get_properties_table(soup)

        wool_item.get_name(url, wool_df)
        wool_item.get_price(soup, price_container)
        wool_item.get_delivery_time(get_soup(delivery_url), delivery)
        wool_item.get_needle_size(properties_table, needle_size_container)
        wool_item.get_composition(properties_table, composition_container)

        data.append(Wool(wool_item.name, wool_item.price, wool_item.delivery_time, wool_item.needle_size,
                         wool_item.composition))

    df = pd.DataFrame([vars(w) for w in data])

    print_time(start_time)
    print('-' * 40)
    save_results(df)


def get_properties_table(soup):
    return soup.find("div", id="pdetailTableSpecs")


def get_delivery_info(soup):
    return soup.find("div", id="ContentPlaceHolder1_upStockInfoDescription").findNext('span').contents[0]


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def save_results(df):
    print('Saving results...')
    start_time = time.time()
    # merge dataframes
    result = pd.merge(wool_df, df, how='left', on="name")
    # fill missing values
    result.fillna('Not Found', inplace=True)
    # save to excel file
    result.to_excel("result_data.xlsx")
    # save to json file
    result.to_json("result_data.json")
    # save to db
    result.to_sql('result_data', engine, if_exists='replace')

    print_time(start_time)
    print('-' * 40)


def print_time(start):
    print("\nThis took %s seconds." % int((time.time() - start)))


def run_app():
    df = pd.read_json('result_data.json')

    @app.route('/')
    def index():
        return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

    print('App is running and you can open the link below in order to check the results')
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)


def main():
    for website in Website.instances:
        print(
            'Let\'s explore some information from {} website for the following items:'.format(website.base_url))
        for x in range(len(wool_df)):
            print(wool_df.brand[x] + ' ' + wool_df.name[x])
        print('-' * 40)
        get_product_links(website)

    # run flask app
    run_app()


if __name__ == "__main__":
    main()
