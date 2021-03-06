from HtmlIdentifier import IdentifierType
from enum import Enum


class Datasource:

    def __init__(self, name, url, identifiers=None, isUsingAjax=False):
        self.name = name
        self.url = url
        self.identifiers = identifiers
        self.isUsingAjax = isUsingAjax


    def getOutermostIdentifier(self, type_=IdentifierType.NONE):
        for identifier in self.identifiers:
            if identifier.type_ == type_:
                return identifier
        return None


class DatasourceType(Enum):
    SCHREIBEN = 1
    ENTSCHEIDUNGEN = 2
    GESETZESTEXTE = 4
    PRESSEMITTEILUNGEN = 5
    UNKNOWN = None



