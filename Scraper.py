from Document import Document
from HtmlIdentifier import IdentifierType
from Datasource import DatasourceType
import bs4 as bs
import urllib.request
import os
import re


class Scraper:

    def __init__(self, dbAccess):
        self.dbAccess = dbAccess

    def scrapeDatasources(self, datasources):
        for datasource in datasources:
            self.scrapeDatasource(datasource)


    def scrapeDatasource(self, datasource):

        if not self.dbAccess.datasourceExists(datasource.name):
            self.dbAccess.addDatasource(datasource)

        self.dbAccess.commit()

        listItemIdentifier = datasource.getOutermostIdentifier(IdentifierType.LISTITEM)
        titleIdentifier = datasource.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE)
        subTitleIdentifier = datasource.getOutermostIdentifier(IdentifierType.DOCUMENTSUBTITLE)
        documentContentIdentifier = datasource.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT)
        downloadLinkIdentifier = datasource.getOutermostIdentifier(IdentifierType.DOWNLOADLINK)
        nextPageIdentifier = datasource.getOutermostIdentifier(IdentifierType.NEXTPAGE)
        dateIdentifier = datasource.getOutermostIdentifier(IdentifierType.DATEIDENTIFIER)

        source = urllib.request.urlopen(datasource.url)
        soup = bs.BeautifulSoup(source, "lxml")

        folderPath = "documents_" + datasource.name
        if not os.path.exists(folderPath):
            # Ordner für .pdfs anlegen, falls noch nicht vorhanden
            os.makedirs(folderPath)
        i = 0
        while True:

            # alle listItems durchlaufen
            for li in self._getInnerItemsFromSoup(soup, listItemIdentifier):


                #try:
                    i += 1
                    print(i)
                    #TODO: richtigen DatasourceType suchen
                    document = Document(None, None, datasource, DatasourceType.GESETZESTEXTE, None, None)

                    liLink = li.get("href")
                    source2 = Scraper.openLink(liLink, datasource)
                    soup2 = bs.BeautifulSoup(source2, "lxml")

                    if titleIdentifier is None:
                        document.title = li.text.strip()
                    else:
                        document.title = self._getInnerItemsFromSoup(soup2, titleIdentifier)[0].text.strip()

                    if subTitleIdentifier is not None:
                        subTitleItems = self._getInnerItemsFromSoup(soup2, subTitleIdentifier)
                        if len(subTitleItems) > 0:
                            document.title += subTitleItems[0].text.strip()

                    if dateIdentifier is not None:
                        dateItems = self._getInnerItemsFromSoup(soup2, dateIdentifier)
                        if len(dateItems) > 0:
                            document.date = dateItems[0].text

                    if self.dbAccess.documentExists(document.title, datasource.name):
                        #Wenn Gesetzestext bereits in der Db: neuere Version verwenden.
                        #Wenn kein Datum gescraped werden kann -> überspringen
                        if document.date is not None:
                            documentInDb = self.dbAccess.getDocument(document.title, datasource)
                            if documentInDb.date < document.date:
                                self.dbAccess.removeDocument(documentInDb.title, datasource)
                            else:
                                continue
                        else:
                            continue



                    if downloadLinkIdentifier is None:
                        #TODO
                        #als xml speichern
                        content = self._getInnerItemsFromSoup(soup, documentContentIdentifier)[0].text
                    else:
                        downloadLinkItems = self._getInnerItemsFromSoup(soup2, downloadLinkIdentifier)

                        if len(downloadLinkItems) == 0:
                            #TODO: mehrere DownloadLinks zulassen?
                            continue

                        downloadLink = downloadLinkItems[0].get("href")
                        downloadResponse = Scraper.openLink(downloadLink, datasource)
                        if downloadResponse is not None:
                            document.url = downloadResponse.url

                            documentId = self.dbAccess.addDocument(document, datasource)

                            documentPath = folderPath + "/" + str(documentId) + ".pdf"

                            urllib.request.urlretrieve(downloadResponse.url, documentPath)

                            document.filepath = documentPath

                            self.dbAccess.setDocumentFilePath(documentId, documentPath)

                            self.dbAccess.commit()

                #except:
                    #self.dbAccess.rollback()

            #TODO:
            paginationItems = self._getInnerItemsFromSoup(soup, nextPageIdentifier)
            if len(paginationItems) == 0:
                break
            else:
                nextPageLink = paginationItems[0].get("href")
                if nextPageLink is None:
                    nextPageLink = paginationItems[0].parent.get("href")
                if nextPageLink is None:
                    break
                source = Scraper.openLink(nextPageLink, datasource)
                soup = bs.BeautifulSoup(source, "lxml")






    @staticmethod
    def openLink(link, datasource):

        try:
            response = urllib.request.urlopen(link)
        except:
            #Wenn Link nicht geöffnet werden kann -> wahrscheinlich relativer Link
            slashIndex = re.search(r"[^/]/[^/]", datasource.url).start() + 1
            motherUrl = datasource.url[0:slashIndex]

            if link[0] != "/":
                link = "/" + link
            link = motherUrl + link
            try:
                #Wenn Link immer noch nicht geöffnet werden kann -> Fehler
                response = urllib.request.urlopen(link)
            except:
                return None

        return response


    def _getInnerItemsFromSoup(self, soup, topIdentifier):

        #items = soup.find_all(topIdentifier.tag, class_=topIdentifier.class_)
        items = []
        if topIdentifier.class_ is None:
            items += soup.find_all(topIdentifier.tag)
        else:
            classes = topIdentifier.class_.split(" ")
            cssSelector = topIdentifier.tag
            for class_ in classes:
                cssSelector += "." + class_
            items = soup.select(cssSelector)

        if topIdentifier.innerIdentifier is None:
            return items
        else:
            return self._getInnerItemsFromItems(items, topIdentifier.innerIdentifier)


    def _getInnerItemsFromItems(self, items, identifier):

        innerItems = []
        for item in items:
            if identifier.class_ is None:
                innerItems += item.find_all(identifier.tag)
            else:
                classes = identifier.class_.split(" ")
                cssSelector = identifier.tag
                for class_ in classes:
                    cssSelector += "." + class_
                innerItems += item.select(cssSelector)

        if identifier.innerIdentifier is None:
            return innerItems
        else:
            return self._getInnerItemsFromItems(innerItems, identifier.innerIdentifier)