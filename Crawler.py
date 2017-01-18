import DatabaseAccess
import Website
import LegalText
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
        for li in soup.find_all(website.listItemIdentifier.tag, class_=website.listItemIdentifier.class_):

