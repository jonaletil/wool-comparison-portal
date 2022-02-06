import weakref


# creating Website class
class Website:
    instances = []

    def __init__(self, base_url, pagination_url, page_num, price_container, needle_size_container,
                 composition_container):
        self.__class__.instances.append(weakref.proxy(self))
        """
        Wool class

        Attributes:
            base_url (str)
            pagination_url (str)
            page_num (int)
        """
        self.base_url = base_url
        self.pagination_url = pagination_url
        self.page_num = page_num
        self.price_container = price_container
        self.needle_size_container = needle_size_container
        self.composition_container = composition_container
