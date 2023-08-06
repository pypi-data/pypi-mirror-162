"""The xml_node_list module"""


def equal_predicate(v1: str, v2: str):
    """Check to see if the two values are equal"""
    return v1 == v2


def not_equal_predicate(v1: str, v2: str):
    """Check to see if the values are not equal"""
    return not equal_predicate(v1, v2)


def like_predicate(v1: str, v2: str):
    """Check to see if one value contains the other"""
    return v1 in v2 or v2 in v1


def startswith_predicate(v1: str, v2: str):
    """Check to see if the first value starts with the second"""
    return v1.startswith(v2) if v1 else False


def endswith_predicate(v1: str, v2: str):
    """Check to see if the first value ends with the second"""
    return v1.endswith(v2) if v1 else False


class XmlNodeList(list):
    """
    Sometimes when navigating a XmlNode graph, there will be child elements with the same
    tag name (i.e. <Credential />).  When this occurs, the XmlNode will expose that attribute
    as a XmlNodeList, a subclass of Python's native list.  This list has some extra, helper
    methods to make interacting with a list of XmlNodes easier.
    """

    def first(self, default=None):
        """
        Returns the first item in the list.  If the list happens to be empty, returns the
        default value instead.
        :param default: What to return if the list is empty.
        :return:
        """
        return self[0] if len(self) else default

    def last(self, default=None):
        """
        Returns the last item in the list.  If the list happens to be empty, returns the
        default value instead.
        :param default: What to return if the list is empty.
        :return:
        """
        return self[-1] if len(self) else default

    def filter(self, func: callable):
        """
        Filters out nodes that don't meet the given criteria
        :param func: single argument callable that returns True to keep the node or False to exempt it
        :return: list of nodes that meet the given criteria
        """
        return XmlNodeList([n for n in self if func(n)])

    def filter_prop(self, property_name: str, property_value: str, comparison=equal_predicate):
        """
        Returns any items in the list in which they have a property with the given name that
        and has a value that meets the criteria of the comparison predicate.
        :param property_name: The name of the property to search on.
        :param property_value: The value to compare it to.
        :param comparison: What kind of comparison to perform. (Defaults to equality)
        :return: A list of nodes that meet the given criteria
        """
        return XmlNodeList([n for n in self if comparison(n.get(property_name), property_value)])

    def filter_text(self, text_value: str, comparison=equal_predicate):
        """
        Returns any items in the list in which they have a text value that meets the criteria
        of the comparison predicate.
        :param text_value: The text value to search on.
        :param comparison: What kind of comparison to perform. (Defaults to equality)
        :return: A list of nodes that meet the given criteria
        """
        return XmlNodeList([n for n in self if comparison(n.text(), text_value)])

    def join_prop(self, property_name: str, sep: str = ', '):
        """
        Performs a string-join on the property values of the nodes in the list.
        :param property_name: The name of the property value to extract from the nodes.
        :param sep: A string-join separator (i.e. new-line, comma, etc.)
        :return: A string with the values joined together
        """
        return sep.join([n[property_name] for n in self])

    def join_text(self, sep: str = ', '):
        """
        Performs a string-join on the text values of the nodes in the list.
        :param sep: A string-join separator (i.e. new-line, comma, etc.)
        :return: A string with the values joined together
        """
        return sep.join([n.text() for n in self])

    def map(self, func: callable):
        """
        Translates each item in the list to another
        :param func: single argument callable that returns a new value given a node
        :return: list
        """
        return XmlNodeList([func(n) for n in self])

    def map_attr(self, attribute_name: str) -> list:
        """
        Can be used to map from the list to a child attribute of each child
        :param attribute_name: name of the attribute to map to
        :return: list of XmlNodes
        """
        return [getattr(n, attribute_name) for n in self]

    def map_prop(self, property_name: str) -> list:
        """
        Can be used to map from the list to a property value of each child
        :param property_name: name of the attribute to map to
        :return: list of XmlNodes
        """
        return [n[property_name] for n in self]

    def map_text(self) -> list:
        """
        Can be used to map from the list to the text value of each child
        :return: list of XmlNodes
        """
        return [n.text() for n in self]

    def __repr__(self):
        if not len(self):
            return "XmlNodeList: []"
        try:
            return f"XmlNodeList: [{self[0].tag()}]"
        except:
            return super(XmlNodeList, self).__repr__()
