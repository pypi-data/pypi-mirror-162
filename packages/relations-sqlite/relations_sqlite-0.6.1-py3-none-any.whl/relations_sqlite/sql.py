"""
Base SQL module for all of sqlite SQL
"""


class SQL: # pylint: disable=too-few-public-methods
    """
    Base class for every sqlite expression storing constants
    """

    QUOTE = '`'
    STR = "'"
    SEPARATOR = '.'
    PLACEHOLDER = "?"
    JSONIFY = "json_extract(%s,'$')"
    PATH = "json_extract(%s,%s)"

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
