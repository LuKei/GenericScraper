from DatabaseAccess import DatabaseAccess
from Website import Website
from LegalText import LegalText
from HtmlIdentifier import IdentifierType
import bs4 as bs
import urllib.request


class Crawler:

    def scrapeWebsites(self, websites):

        for website in websites:
            self.scrapeWebsite(website)


    def scrapeWebsite(self, website):

        source = urllib.request.urlopen(website)
        soup = bs.BeautifulSoup(source, "lxml")

        #alle listItems durchlaufen
        listItemIdentifier = website.getIdentifier(IdentifierType.LISTITEM)
        for li in soup.find_all(listItemIdentifier.tag, class_=listItemIdentifier.class_):



