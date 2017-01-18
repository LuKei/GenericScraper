from HtmlIdentifier import IdentifierType


class Website:

    def __init__(self, name, url, isUsingAjax, isMultiPage, identifiers):
        self.name = name
        self.url = url
        self.isUsingAjax = isUsingAjax
        self.isMultiPage = isMultiPage
        self.identifiers = identifiers

    def getIdentifier(self, type=IdentifierType.NONE):

        for identifier in self.identifiers:
            if identifier.type == type:
                return identifier
        return None




