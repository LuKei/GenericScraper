from Document import Document
from HtmlIdentifier import IdentifierType
from Datasource import DatasourceType
import bs4 as bs
import urllib.request
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper:

    def __init__(self, dbAccess):
        self.dbAccess = dbAccess
        self.isRunning = False

    def scrapeDatasources(self, datasources):
        for datasource in datasources:
            self.scrapeDatasource(datasource)


    def scrapeDatasource(self, datasource):

        isRunning = True

        #Variablen für logging
        scrapedDocuments = 0
        sameDocument = 0
        noDownloadlink = 0




        if not self.dbAccess.datasourceExists(datasource.name):
            self.dbAccess.addDatasource(datasource)

        self.dbAccess.commit()

        isUsingAjax = datasource.isUsingAjax

        listItemIdentifier = datasource.getOutermostIdentifier(IdentifierType.LISTITEM)
        titleIdentifier = datasource.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE)
        subTitleIdentifier = datasource.getOutermostIdentifier(IdentifierType.DOCUMENTSUBTITLE)
        documentContentIdentifier = datasource.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT)
        downloadLinkIdentifier = datasource.getOutermostIdentifier(IdentifierType.DOWNLOADLINK)
        nextPageIdentifier = datasource.getOutermostIdentifier(IdentifierType.NEXTPAGE)
        dateIdentifier = datasource.getOutermostIdentifier(IdentifierType.DATEIDENTIFIER)
        ajaxWaitIdentifier = datasource.getOutermostIdentifier(IdentifierType.AJAXWAIT)



        folderPath = "documents_" + datasource.name
        if not os.path.exists(folderPath):
            # Ordner für .pdfs anlegen, falls noch nicht vorhanden
            os.makedirs(folderPath)

        driver = None
        if isUsingAjax:
            driver = webdriver.Chrome()
            driver.get(url=datasource.url)

            xpathWaitString = "//" + ajaxWaitIdentifier.tagName + "["
            if ajaxWaitIdentifier.class_ is not None:
                xpathWaitString += "(@class=" + "\"" + ajaxWaitIdentifier.class_ + "\"" + ") and "
            if ajaxWaitIdentifier.additionalAttributes is not None:
                for attribute in ajaxWaitIdentifier.additionalAttributes:
                    xpathWaitString += "(@" + attribute.name + "=" + "\"" + attribute.value + "\"" + ") and "
            if (ajaxWaitIdentifier.class_ is not None) or (ajaxWaitIdentifier.additionalAttributes is not None):
                xpathWaitString = xpathWaitString[0:len(xpathWaitString)-5]
            xpathWaitString += "]"

            if ajaxWaitIdentifier.class_ is None and ajaxWaitIdentifier.additionalAttributes is None:
                xpathWaitString = xpathWaitString[0:len(xpathWaitString)-2]


            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpathWaitString)))

            source = driver.page_source

        else:
            source = urllib.request.urlopen(datasource.url)

        soup = bs.BeautifulSoup(source, "lxml")

        i = 0

        while True:



            # alle ListItems durchlaufen
            for li in self._getInnerItemsFromSoup(soup, listItemIdentifier):

                i += 1
                print(i)

                document = Document(None, None, datasource, DatasourceType.GESETZESTEXTE, None, None)

                liLink = li.get("href")

                # if isUsingAjax:
                #     source2 = Scraper.openLinkAjax(liLink, datasource, driver)
                # else:
                source2 = Scraper.openLinkNonAjax(liLink, datasource)

                soup2 = bs.BeautifulSoup(source2, "lxml")

                if titleIdentifier is not None:
                    documentTitleItems = self._getInnerItemsFromSoup(soup2, titleIdentifier)
                    if len(documentTitleItems) > 0:
                        document.title = documentTitleItems[0].text.strip()
                    else:
                        document.title = li.text.strip()
                else:
                    document.title = li.text.strip()

                if subTitleIdentifier is not None:
                    subTitleItems = self._getInnerItemsFromSoup(soup2, subTitleIdentifier)
                    if len(subTitleItems) > 0:
                        document.title += subTitleItems[0].text.strip()

                if dateIdentifier is not None:
                    dateItems = self._getInnerItemsFromSoup(soup2, dateIdentifier)
                    if len(dateItems) > 0:
                        document.date = dateItems[0].text

                if self.dbAccess.documentExists(document.title, datasource.name):
                    # Wenn Gesetzestext bereits in der Db: neuere Version verwenden.
                    # Wenn kein Datum gescraped werden kann -> überspringen
                    if document.date is not None:
                        documentInDb = self.dbAccess.getDocument(document.title, datasource)
                        if documentInDb.date < document.date:
                            self.dbAccess.removeDocument(documentInDb.title, datasource)
                        else:
                            sameDocument += 1
                            continue

                    else:
                        sameDocument += 1
                        continue

                if downloadLinkIdentifier is None:
                    # TODO
                    # als xml speichern
                    content = self._getInnerItemsFromSoup(soup, documentContentIdentifier)[0].text
                else:
                    downloadLinkItems = self._getInnerItemsFromSoup(soup2, downloadLinkIdentifier)

                    if len(downloadLinkItems) == 0:
                        # TODO: mehrere DownloadLinks zulassen?
                        noDownloadlink += 1
                        continue


                    downloadLink = downloadLinkItems[0].get("href")
                    downloadResponse = Scraper.openLinkNonAjax(downloadLink, datasource)
                    if downloadResponse is not None:
                        document.url = downloadResponse.url

                        documentId = self.dbAccess.addDocument(document, datasource)

                        documentPath = folderPath + "/" + str(documentId) + ".pdf"

                        urllib.request.urlretrieve(downloadResponse.url, documentPath)

                        document.filepath = documentPath

                        self.dbAccess.setDocumentFilePath(documentId, documentPath)

                        self.dbAccess.commit()

                scrapedDocuments += 1


            paginationItems = self._getInnerItemsFromSoup(soup, nextPageIdentifier)
            if len(paginationItems) == 0:
                break
            else:
                nextPageLink = paginationItems[0].get("href")
                if nextPageLink is None:
                    nextPageLink = paginationItems[0].parent.get("href")
                if nextPageLink is None:
                    break
                if isUsingAjax:
                    source = Scraper.openLinkAjax(nextPageLink, datasource, driver)
                else:
                    source = Scraper.openLinkNonAjax(nextPageLink, datasource)
                soup = bs.BeautifulSoup(source, "lxml")

        if driver is not None:
            driver.close()

        print("Wesbeite: " + datasource.name)
        print("Erfasste Dokumente: " + str(scrapedDocuments))
        print("Übersprungen wegen selben Namens: " + str(sameDocument))
        print("Übersprungen, weil kein Download-Link gefunden wurde:" + str(noDownloadlink))

        isRunning = False


    @staticmethod
    def openLinkAjax(link, datasource, driver):

        if not re.match(r"\Ahttp", link):
            # Wenn Link nicht mit http startet -> wahrscheinlich relativer Link
            slashIndex = re.search(r"[^/]/[^/]", datasource.url).start() + 1
            motherUrl = datasource.url[0:slashIndex]

            # Sonder- und Trennzeichen am Anfang des Links entfernen
            link = re.sub(r"\A(\/|\.)*", "", link)

            link = motherUrl + "/" + link

        driver.get(link)

        return driver.page_source




    @staticmethod
    def openLinkNonAjax(link, datasource):

        try:
            response = urllib.request.urlopen(link)
        except:
            #Wenn Link nicht geöffnet werden kann -> wahrscheinlich relativer Link
            slashIndex = re.search(r"[^/]/[^/]", datasource.url).start() + 1
            motherUrl = datasource.url[0:slashIndex]

            #Sonder- und Trennzeichen am Anfang des Links entfernen
            link = re.sub(r"\A(\/|\.)*", "", link)

            link = motherUrl + "/" + link
            try:
                #Wenn Link immer noch nicht geöffnet werden kann -> Fehler
                response = urllib.request.urlopen(link)
            except:
                return None

        return response



    def _getInnerItemsFromSoup(self, soup, topIdentifier):

        items = []
        if topIdentifier.class_ is None:
            #items = soup.find_all(topIdentifier.tagName, attrs=topIdentifier.getAdditionalAttributesDict())
            items = soup.find_all(lambda tag: self._matchTag(tag, topIdentifier))
        else:
            classes = topIdentifier.class_.split(" ")
            cssSelector = topIdentifier.tagName
            for class_ in classes:
                cssSelector += "." + class_
            items += soup.select(cssSelector)

        if topIdentifier.innerIdentifier is None:
            return items
        else:
            return self._getInnerItemsFromItems(items, topIdentifier.innerIdentifier)


    def _getInnerItemsFromItems(self, items, identifier):

        innerItems = []
        for item in items:
            if identifier.class_ is None:
                #innerItems += item.find_all(identifier.tagName, attrs=identifier.getAdditionalAttributesDict())
                innerItems += item.find_all(lambda tag: self._matchTag(tag, identifier))
            else:
                classes = identifier.class_.split(" ")
                cssSelector = identifier.tagName
                for class_ in classes:
                    cssSelector += "." + class_
                innerItems += item.select(cssSelector)


        if identifier.innerIdentifier is None:
            return innerItems
        else:
            return self._getInnerItemsFromItems(innerItems, identifier.innerIdentifier)



    def _matchTag(self, tag, identifier):
        if tag.name != identifier.tagName:
            return False

        if identifier.additionalAttributes is not None:
            for identifierAttr in identifier.additionalAttributes:
                tagAttrVal = tag.attrs.get(identifierAttr.name, None)

                if tagAttrVal is None:
                    return False

                if identifierAttr.value == "":
                    continue

                if identifierAttr.exactmatch:
                    if not identifierAttr.value == tagAttrVal:
                        return False
                else:
                    if identifierAttr.value not in tagAttrVal:
                        return False

        return True
