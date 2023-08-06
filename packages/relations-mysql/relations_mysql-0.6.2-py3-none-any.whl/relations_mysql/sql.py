"""
Base SQL module for all of MySQL SQL
"""


class SQL: # pylint: disable=too-few-public-methods
    """
    Base class for every MySQL expression storing constants
    """

    QUOTE = '`'
    STR = "'"
    SEPARATOR = '.'
    PLACEHOLDER = "%s"
    JSONIFY = "CAST(%s AS JSON)"
    PATH = "%s->>%s"

    @staticmethod
    def walk(path):
        """
        Translates a path array to JSON access
        """

        places = []

        for place in path:
            if isinstance(place, int):
                places.append(f"[{place}]")
            elif place[0] in "-1234567890":
                places.append(f'."{place}"')
            else:
                places.append(f'.{place}')

        return f"${''.join(places)}"
