from sqlite3 import dbapi2

from LegalText import LegalText
from HtmlIdentifier import IdentifierType, HtmlIdentifier
import bs4 as bs
import urllib.request
import os
import re


class Scraper:

    maxPathLength = 200

    def __init__(self, dbAccess):
        self.dbAccess = dbAccess

    def scrapeWebsites(self, websites):
        for website in websites:
            self.scrapeWebsite(website)


    def scrapeWebsite(self, website):

        if not self.dbAccess.websiteExists(website.name):
            self.dbAccess.addWebsite(website)


        listItemIdentifier = website.getIdentifier(IdentifierType.LISTITEM)
        legalTextTitleIdentifier = website.getIdentifier(IdentifierType.LEGALTEXTTITLE)
        legalTextContentIdentifier = website.getIdentifier(IdentifierType.LEGALTEXTCONTENT)
        downloadLinkIdentifier = website.getIdentifier(IdentifierType.DOWNLOADLINK)
        nextPageIdentifier = website.getIdentifier(IdentifierType.NEXTPAGE)

        source = urllib.request.urlopen(website.url)
        soup = bs.BeautifulSoup(source, "lxml")

        #TODO:
        #while True:

        # alle listItems durchlaufen
        for li in soup.find_all(listItemIdentifier.tag, class_=listItemIdentifier.class_):
        #TODO:
        #for li in Scraper.getInnerItems(soup, listItemIdentifier):

            legalText = LegalText(None, None, None, website)

            if legalTextTitleIdentifier is None:
                legalText.title = li.text.strip()
            else:
                legalText.title = li.find(legalTextTitleIdentifier).strip()

            if self.dbAccess.legalTextExists(legalText.title, website.name):
                #Wenn Gesetzestext bereits in der Db: mit nächstem fortfahren
                continue

            liLink = li.get("href")
            liLink = Scraper.makeLinkAbsolute(liLink, website)

            source2 = urllib.request.urlopen(liLink)
            soup2 = bs.BeautifulSoup(source2, "lxml")

            if downloadLinkIdentifier is None:
                #Wenn kein downloadLinkIdentifier vorhanden => Text direk in Html => legalTextContentIdentifier nutzen
                content = soup2.find(legalTextContentIdentifier.tag, class_=legalTextContentIdentifier.class_).text
                legalText.text = content
            else:
                folderPath = website.name + "pdfs"
                if not os.path.exists(folderPath):
                    # Ordner für .pdfs anlegen, falls noch nicht vorhanden
                    os.makedirs(folderPath)

                downloadLink = soup2.find(downloadLinkIdentifier.tag, class_=downloadLinkIdentifier.class_).get("href")
                downloadLink = Scraper.makeLinkAbsolute(downloadLink, website)

                pdfPath = folderPath + "/" + legalText.title + ".pdf"
                if len(os.curdir) + len(pdfPath) > Scraper.maxPathLength:
                    #pdfPath kürzen, wenn gesamte Pfadlänge > 260
                    pdfPath = pdfPath[0:len(pdfPath)-4]
                    pdfPath = pdfPath[0:Scraper.maxPathLength-4-len(os.curdir)] + ".pdf"

                urllib.request.urlretrieve(downloadLink, pdfPath)

                legalText.location = pdfPath
                self.dbAccess.addLegalText(legalText, website)

            #TODO:
            #nextPageItem =soup.find(nextPageIdentifier.tag, class_=nextPageIdentifier.class_)
            #if nextPageItem is None:
                #break
            #else:
                #nextPageLink = nextPageItem....
                #source = urllib.request.urlopen(nextPageLink)
                #soup = bs.BeautifulSoup(source, "lxml")
        self.dbAccess.commit()


    @staticmethod
    def makeLinkAbsolute(link, website):
        if link[0] == "/":
            slashIndex = re.search(r"[^/]/[^/]", website.url).start() + 1
            motherUrl = website.url[0:slashIndex]
            return  motherUrl + link

        return link