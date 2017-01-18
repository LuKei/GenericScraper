import sys
import DatabaseAccess
import Website
import LegalText
import bs4 as bs
import urllib.request


class Crawler:

    def startcrawling(self, websites):

        for site in websites:

            source = urllib.request.urlopen(site)
            soup = bs.BeautifulSoup(source, "lxml")

            for li in soup.find_all(site.listItemHtmlFrag, class_=):

