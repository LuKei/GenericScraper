from sqlite3 import dbapi2

from Document import Document
from HtmlIdentifier import IdentifierType, HtmlIdentifier
import bs4 as bs
import urllib.request
import os
import re


class Scraper:

    maxPathLength = 200

    def __init__(self, dbAccess):
        self.dbAccess = dbAccess

    def scrapeDatasources(self, datasources):
        for datasource in datasources:
            self.scrapeDatasource(datasource)


    def scrapeDatasource(self, datasource):

        if not self.dbAccess.datasourceExists(datasource.name):
            self.dbAccess.addDatasource(datasource)


        listItemIdentifier = datasource.getIdentifier(IdentifierType.LISTITEM)
        legalTextTitleIdentifier = datasource.getIdentifier(IdentifierType.LEGALTEXTTITLE)
        legalTextContentIdentifier = datasource.getIdentifier(IdentifierType.LEGALTEXTCONTENT)
        downloadLinkIdentifier = datasource.getIdentifier(IdentifierType.DOWNLOADLINK)
        nextPageIdentifier = datasource.getIdentifier(IdentifierType.NEXTPAGE)

        source = urllib.request.urlopen(datasource.url)
        soup = bs.BeautifulSoup(source, "lxml")

        #TODO:
        #while True:

        # alle listItems durchlaufen
        for li in soup.find_all(listItemIdentifier.tag, class_=listItemIdentifier.class_):
        #TODO:
        #for li in Scraper.getInnerItems(soup, listItemIdentifier):

            document = Document(None, None, datasource, None, None, None)

            if legalTextTitleIdentifier is None:
                document.title = li.text.strip()
            else:
                document.title = li.find(legalTextTitleIdentifier).strip()

            if self.dbAccess.legalTextExists(document.title, datasource.name):
                #Wenn Gesetzestext bereits in der Db: mit nächstem fortfahren
                continue

            liLink = li.get("href")
            liLink = Scraper.makeLinkAbsolute(liLink, datasource)

            source2 = urllib.request.urlopen(liLink)
            soup2 = bs.BeautifulSoup(source2, "lxml")

            if downloadLinkIdentifier is None:
                #TODO: als xml speichern
                #Wenn kein downloadLinkIdentifier vorhanden => Text direk in Html => legalTextContentIdentifier nutzen
                content = soup2.find(legalTextContentIdentifier.tag, class_=legalTextContentIdentifier.class_).text
                #document.text = content
            else:
                folderPath = datasource.name + "pdfs"
                if not os.path.exists(folderPath):
                    # Ordner für .pdfs anlegen, falls noch nicht vorhanden
                    os.makedirs(folderPath)

                downloadLink = soup2.find(downloadLinkIdentifier.tag, class_=downloadLinkIdentifier.class_).get("href")
                downloadLink = Scraper.makeLinkAbsolute(downloadLink, datasource)
                document.url = downloadLink

                pdfPath = folderPath + "/" + document.title + ".pdf"
                if len(os.curdir) + len(pdfPath) > Scraper.maxPathLength:
                    #pdfPath kürzen, wenn gesamte Pfadlänge > 260
                    pdfPath = pdfPath[0:len(pdfPath)-4]
                    pdfPath = pdfPath[0:Scraper.maxPathLength-4-len(os.curdir)] + ".pdf"

                urllib.request.urlretrieve(downloadLink, pdfPath)

                document.filepath = pdfPath
                self.dbAccess.addLegalText(document, datasource)

                #TODO: date des documents

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