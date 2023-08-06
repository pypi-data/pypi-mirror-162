"""
Base SQL module for all of PostgreSQL SQL
"""


class SQL: # pylint: disable=too-few-public-methods
    """
    Base class for every PostgreSQL expression storing constants
    """

    QUOTE = '"'
    STR = "'"
    SEPARATOR = '.'
    PLACEHOLDER = "%s"
    JSONIFY = "(%s)::JSONB"
    PATH = "%s#>>%s"

    @staticmethod
    def walk(path):
        """
        Translates a path array to JSON access
        """

        places = []

        for place in path:
            if isinstance(place, str) and place[0] in "-1234567890":
                places.append(f'"{place}"')
            else:
                places.append(str(place))

        return f"{{{','.join(places)}}}"
