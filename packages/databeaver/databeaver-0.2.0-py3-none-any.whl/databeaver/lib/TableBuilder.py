from .Object import Object
from .PostgreSQL import PostgreSQL

class TableBuilder(Object):
    def __init__(self):
        """

        """
        self.references = None
        super().__init__()

    def build(self, table_name:str, postgres:PostgreSQL):
        """

        :param table_name:
        :param postgres:
        :return:
        """
        raise NotImplementedError

    def references(self):
        """

        :return:
        """
        return self.references





