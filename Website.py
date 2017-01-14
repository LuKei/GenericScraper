import sys


class Website:

    def __init__(self, name, url, isUsingAjax, isMultiPage, nextPageHtmlFrag, listItemHtmlFrag, downloadHtmlFrag, legalTextTitleHtmlFrag):
        self.name = name
        self.url = url
        self.isUsingAjax = isUsingAjax
        self.isMultiPage = isMultiPage
        self.nextPageHtmlFrag = nextPageHtmlFrag
        self.listItemHtmlFrag = listItemHtmlFrag
        self.downloadHtmlFrag = downloadHtmlFrag
        self.legalTextTitleHtmlFrag = legalTextTitleHtmlFrag




