from HtmlIdentifier import IdentifierType


class Website:

    def __init__(self, name, url, isUsingAjax, isMultiPage, nextPageIdentifier, listItemIdentifier,
                 downloadLinkIdentifier, legalTextTitleIdentifier):
        self.name = name
        self.url = url
        self.isUsingAjax = isUsingAjax
        self.isMultiPage = isMultiPage
        self.nextPageIdentifier = nextPageIdentifier
        self.nextPageIdentifier.type = IdentifierType.NEXTPAGE
        self.listItemIdentifier = listItemIdentifier
        self.listItemIdentifier.type = IdentifierType.LISTITEM
        self.downloadLinkIdentifier = downloadLinkIdentifier
        self.downloadLinkIdentifier.type = IdentifierType.DOWNLOADLINK
        self.legalTextTitleIdentifier = legalTextTitleIdentifier
        self.legalTextTitleIdentifier.type = IdentifierType.LEGALTEXTTITLE



