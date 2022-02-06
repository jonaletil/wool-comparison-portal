# creating Wool class
class Wool:
    def __init__(self, name=None, price=None, delivery_time=None, needle_size=None, composition=None):
        """
        Wool class

        Attributes:
            name (str)
            price (str)
            delivery_time (str)
            needle_size (str)
            composition (str)
        """
        self.name = name
        self.price = price
        self.delivery_time = delivery_time
        self.needle_size = needle_size
        self.composition = composition

    def get_name(self, url, df):
        """
        Returns wool name.

            Args:
                url (str)
                df (pandas dataframe)

            Returns:
                str: wool name
        """
        for x in range(len(df)):
            w_name = df.name[x].replace(" ", "-").lower()
            if w_name in url:
                self.name = df.name[x]
                return self.name

    def get_price(self, soup, container):
        """
        Returns wool price.

            Args:
                soup
                container

            Returns:
                str: wool price
        """
        self.price = soup.find(container.tag, **container.attribute).text + " €"
        return self.price

    def get_delivery_time(self, soup, delivery):
        """
        Function to retrieve wool delivery time.

            Args:
                soup
                delivery

            Returns:
                str: delivery time
        """
        if delivery == "Lieferbar":
            delivery_table = soup.find("tbody")
            delivery_time = delivery_table.find("td", text="Gratis Versand").find_next_sibling("td").text
            self.delivery_time = delivery_time
        else:
            self.delivery_time = "Nicht lieferbar"

        return self.delivery_time

    def get_needle_size(self, table, container):
        """
        Function for wool needle size.

            Args:
                table
                container

            Returns:
                str: wool needle size
        """
        self.needle_size = table.find(container.tag, **container.attribute).findNext('td').contents[0]
        return self.needle_size

    def get_composition(self, table, container):
        """
        Function for wool composition.

            Args:
                table
                container

            Returns:
                str: wool composition
        """
        self.composition = table.find(container.tag, **container.attribute).findNext('td').contents[0]
        return self.composition
