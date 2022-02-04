import time
import requests
import pandas as pd
from wool import Wool
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask('Flask App')
engine = create_engine('sqlite:///result_data.db')

base_url = "https://www.wollplatz.de/wolle"
pagination_url = "https://www.wollplatz.de/wolle?page="
delivery_url = 'https://www.wollplatz.de/versandkosten-und-lieferung'
wool_json = pd.read_json('wool_data.json')
wool_df = pd.DataFrame(wool_json)
product_links = []
data = []


def get_product_links():
    print('Collecting product links...')
    start_time = time.time()
    for i in range(1, 29):
        if i == 1:
            url = base_url
        else:
            url = pagination_url + str(i)

        soup = get_soup(url)

        for x in range(len(wool_df)):
            title = wool_df.brand[x] + ' ' + wool_df.name[x]
            item = soup.find("a", title=str(title))

            if item:
                link = item.get('href')
                product_links.append(link)

        if i == 28:
            print("\nThis took %s seconds." % (time.time() - start_time))
            print('-' * 40)
            get_product_data(product_links)


def get_product_data(urls):
    print('Collecting product data...')
    start_time = time.time()
    for url in urls:
        soup = get_soup(url)

        delivery = soup.find("div", id="ContentPlaceHolder1_upStockInfoDescription").findNext('span').contents[0]
        properties_table = soup.find("div", id="pdetailTableSpecs")

        name = get_name(url)
        price = get_price(soup)
        delivery_time = get_delivery_time(delivery)
        needle_size = get_needle_size(properties_table)
        composition = get_composition(properties_table)

        wool_item = Wool(name, price, delivery_time, needle_size, composition)

        data.append(wool_item)

    df = pd.DataFrame([vars(w) for w in data])

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-' * 40)
    save_results(df)


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def get_name(url):
    global wool_name
    for x in range(len(wool_df)):
        w_name = wool_df.name[x].replace(' ', '-').lower()
        if w_name in url:
            wool_name = wool_df.name[x]
    return wool_name


def get_price(soup):
    price = soup.find("span", class_="product-price-amount").text
    return price


def get_delivery_time(delivery):
    soup = get_soup(delivery_url)
    if delivery == 'Lieferbar':
        delivery_table = soup.find('tbody')
        delivery_time = delivery_table.find("td", text="Gratis Versand").find_next_sibling("td").text
        print(delivery_time)
        return delivery_time
    else:
        return 'Nicht lieferbar'


def get_needle_size(table):
    needle_size = table.find('td', string="Nadelstärke").findNext('td').contents[0]
    return needle_size


def get_composition(table):
    composition = table.find('td', string="Zusammenstellung").findNext('td').contents[0]
    return composition


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

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-' * 40)
    # run flask app
    run_app(result)


def run_app(df):
    @app.route('/')
    def index():
        return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

    print('App is running and you can open the link below in order to check the results')
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)


def main():
    print('Hello! Let\'s explore some information from {} website for the following items:'.format(base_url))
    for x in range(len(wool_df)):
        print(wool_df.brand[x] + ' ' + wool_df.name[x])
    print('-' * 40)
    get_product_links()


if __name__ == "__main__":
    main()
