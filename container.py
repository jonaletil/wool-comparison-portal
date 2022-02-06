# creating Container class
class Container:
    def __init__(self, tag, attr, value):
        """
        Container class

        Attributes:
            tag (str)
            attr (str)
            value (str)
        """
        self.tag = tag
        self.attribute = {attr: value}
