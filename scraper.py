import time
import requests
import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask('Flask App')
engine = create_engine('sqlite:///result_data.db')

base_url = "https://www.wollplatz.de/wolle"
pagination_url = "https://www.wollplatz.de/wolle?page="

wool = pd.read_json('wool_data.json')
wool_df = pd.DataFrame(wool)

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

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for x in range(len(wool_df)):
            title = wool_df.brand[x] + ' ' + wool_df.name[x]
            item = soup.find("a", title=str(title))

            if item:
                link = item.get('href')
                product_links.append(link)

        if i == 28:
            print("\nThis took %s seconds." % (time.time() - start_time))
            print('-' * 40)
            get_product_data()


def get_product_data():
    print('Collecting product data...')
    start_time = time.time()
    global name
    for url in product_links:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        price = soup.find("span", class_="product-price-amount").text
        delivery_time = soup.find("span", class_="stock-green").text
        properties_table = soup.find("div", id="pdetailTableSpecs")
        needle_size = properties_table.find('td', string="Nadelstärke").findNext('td').contents[0]
        composition = properties_table.find('td', string="Zusammenstellung").findNext('td').contents[0]

        for x in range(len(wool_df)):
            wool_name = wool_df.name[x].replace(' ', '-').lower()
            if wool_name in url:
                name = wool_df.name[x]

        wool = {"name": name, "price": price, "delivery time": delivery_time, "needle size": needle_size,
                "composition": composition}

        data.append(wool)

    df = pd.DataFrame(data)

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-' * 40)
    save_results(df)


def save_results(df):
    print('Saving results...')
    start_time = time.time()
    # merge dataframes
    result = pd.merge(wool_df, df, how='left', on="name")
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
