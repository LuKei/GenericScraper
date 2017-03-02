from Document import Document
from HtmlIdentifier import HtmlIdentifier, IdentifierType
from Datasource import DatasourceType
from DatabaseAccess import DatabaseAccess
import bs4 as bs
import urllib.request
import urllib.parse
import datetime
import traceback
import os
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ScraperThread(threading.Thread):

    def __init__(self, datasource, dbAccess):
        super(ScraperThread, self).__init__()
        self.datasource = datasource
        self.dbAccess = dbAccess
        self.name= "Thread-" + datasource.name
        self.driver = None
        self.stopFlag = False


    def run(self):

        # Variablen für logging
        scrapedDocuments, sameDocument, noDownloadlink, exceptionCaught = 0, 0, 0, 0

        self._writeToLog("Started Scraping: " + str(datetime.datetime.now().time()))

        with DatabaseAccess.lock:
            if not self.dbAccess.datasourceExists(self.datasource.name):
                self.dbAccess.addDatasource(self.datasource)
                self.dbAccess.commit()

        identifierDict = self._buildIdentifierDict()

        folderPath = self.dbAccess.filePath + "documents_" + self.datasource.name
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)  # Ordner für .pdfs anlegen, falls noch nicht vorhanden

        source = self._getSourceForUrl(self.datasource.url, self.datasource.isUsingAjax, identifierDict.get(IdentifierType.AJAXWAIT, None))
        soup = bs.BeautifulSoup(source, "lxml")

        i = 0

        while not self.stopFlag:

            # alle ListItems durchlaufen
            for li in self._getInnerItemsFromSoup(soup, identifierDict[IdentifierType.LISTITEM]):
                if self.stopFlag:
                    break
                try:
                    i += 1
                    print(i)

                    document = Document(None, None, self.datasource, DatasourceType.GESETZESTEXTE, None, None)

                    if IdentifierType.DOCUMENTTITLE in identifierDict:
                        item = self._getItemFromListItem(li, identifierDict[IdentifierType.DOCUMENTTITLE], soup)
                        if item is not None:
                            document.title = item.text.strip()
                    if document.title is None:
                        document.title = li.text.strip()

                    if IdentifierType.DOCUMENTSUBTITLE in identifierDict:
                        item = self._getItemFromListItem(li, identifierDict[IdentifierType.DOCUMENTSUBTITLE], soup)
                        if item is not None:
                            document.title += item.text.strip()

                    if IdentifierType.DATEIDENTIFIER in identifierDict:
                        item = self._getItemFromListItem(li, identifierDict[IdentifierType.DATEIDENTIFIER], soup)
                        if item is not None:
                            document.date = item.text.strip()

                    with DatabaseAccess.lock:
                        if self.dbAccess.documentExists(document.title, self.datasource.name):
                            # Wenn Gesetzestext bereits in der Db: neuere Version verwenden.
                            # Wenn kein Datum gescraped werden kann -> überspringen
                            documentInDb = self.dbAccess.getDocument(document.title, self.datasource)
                            if document.date is not None:
                                if documentInDb.date is None or documentInDb.date < document.date:
                                    self.dbAccess.removeDocument(documentInDb.title, self.datasource)
                                    self.dbAccess.commit()
                                else:
                                    sameDocument += 1
                                    continue
                            else:
                                sameDocument += 1
                                continue

                    if IdentifierType.DOWNLOADLINK in identifierDict:
                        item = self._getItemFromListItem(li, identifierDict[IdentifierType.DOWNLOADLINK], soup)
                        if item is not None:
                            downloadLink = item.get("href")
                        else:
                            noDownloadlink += 1
                            continue

                        downloadResponse = self._getSourceForUrl(self._getFullLink(downloadLink, soup), usingAjax=False)

                        if downloadResponse is not None:
                            document.url = downloadResponse.url
                            with DatabaseAccess.lock:
                                documentId = self.dbAccess.addDocument(document, self.datasource)
                                self.dbAccess.commit()
                            document.filepath = folderPath + "/" + str(documentId)

                            if downloadResponse.info().get_content_subtype() == "html":
                                # options = {"quiet":""}
                                # pdfkit.from_url(downloadResponse.url, document.filepath, options=options)
                                urllib.request.urlretrieve(downloadResponse.url, document.filepath + ".html")
                            else:
                                urllib.request.urlretrieve(downloadResponse.url, document.filepath + ".pdf")
                            with DatabaseAccess.lock:
                                self.dbAccess.setDocumentFilePath(documentId, document.filepath)
                                self.dbAccess.commit()

                    scrapedDocuments += 1
                except Exception as e:
                    with DatabaseAccess.lock:
                        self.dbAccess.rollback()
                    self._writeToLog("Exception caught at index: " + str(i),
                                        path=os.path.expanduser(r"~\Desktop\\") + "excLog_" + self.datasource.name + ".txt")
                    traceback.print_exc(file=open(os.path.expanduser(r"~\Desktop\\") + "excLog_" + self.datasource.name + ".txt", "a+"))

            items = self._getInnerItemsFromSoup(soup, identifierDict[IdentifierType.NEXTPAGE])
            if self.stopFlag or len(items) == 0:
                break
            else:
                nextPageLink = items[0].get("href")
                if nextPageLink is None:
                    nextPageLink = items[0].parent.get("href")
                if nextPageLink is None:
                    break
                source = self._getSourceForUrl(self._getFullLink(nextPageLink, soup), self.datasource.isUsingAjax,
                                               identifierDict.get(IdentifierType.AJAXWAIT))
                soup = bs.BeautifulSoup(source, "lxml")

        if self.driver is not None:
            self.driver.close()

        if self.stopFlag:
            self._writeToLog("Stopped Scraping: " + str(datetime.datetime.now().time()))
        else:
            self._writeToLog("Finished Scraping: " + str(datetime.datetime.now().time()))
        self._writeToLog("Scraped documents: " + str(scrapedDocuments))
        self._writeToLog("Not scraped because of same name: " + str(sameDocument))
        self._writeToLog("Not scraped because download link was not found: " + str(noDownloadlink))
        self._writeToLog("Not scraped because an exception occured: " + str(exceptionCaught))
        self._writeToLog("\n\n\n")




    def _getItemFromListItem(self, li, identifier, soup):
        # Zuerst im ListItem suchen
        item = None
        items = self._getInnerItemsFromItems([li], identifier)
        if items is not None and len(items) > 0:
            item = items[0]
        else:
            # Wenn nichts im ListItem gefunden -> auf Seite des ListItems suchen
            source = self._getSourceForUrl(self._getFullLink(li.get("href"), soup), usingAjax=False)
            soup = bs.BeautifulSoup(source, "lxml")
            items = self._getInnerItemsFromSoup(soup, identifier)
            if items is not None and len(items) > 0:
                item = items[0]

        return item


    def _getSourceForUrl(self, fullUrl, usingAjax, ajaxWaitIdentifier=None):
        if usingAjax:
            if self.driver is None:
                self.driver = webdriver.Chrome()
            self.driver.get(url=fullUrl)

            xpathWaitString = "//" + ajaxWaitIdentifier.tagName + "["
            if ajaxWaitIdentifier.class_ is not None:
                xpathWaitString += "(@class=" + "\"" + ajaxWaitIdentifier.class_ + "\"" + ") and "
            if ajaxWaitIdentifier.additionalAttributes is not None:
                for attribute in ajaxWaitIdentifier.additionalAttributes:
                    xpathWaitString += "(@" + attribute.name + "=" + "\"" + attribute.value + "\"" + ") and "
            if (ajaxWaitIdentifier.class_ is not None) or (ajaxWaitIdentifier.additionalAttributes is not None):
                xpathWaitString = xpathWaitString[0:len(xpathWaitString) - 5]
            xpathWaitString += "]"

            if ajaxWaitIdentifier.class_ is None and ajaxWaitIdentifier.additionalAttributes is None:
                xpathWaitString = xpathWaitString[0:len(xpathWaitString) - 2]

            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpathWaitString)))

            source = self.driver.page_source

        else:
            source = urllib.request.urlopen(fullUrl)

        return source



    def _getFullLink(self, link, soup):
        baseItems = self._getInnerItemsFromSoup(soup, HtmlIdentifier("base"))
        if len(baseItems) > 0:
            url = baseItems[0].get("href")

        fullLink = urllib.parse.urljoin(url, link)
        return fullLink



    def _getInnerItemsFromSoup(self, soup, topIdentifier):

        items = []
        if topIdentifier.class_ is None:
            # items = soup.find_all(topIdentifier.tagName, attrs=topIdentifier.getAdditionalAttributesDict())
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
                # innerItems += item.find_all(identifier.tagName, attrs=identifier.getAdditionalAttributesDict())
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



    def _writeToLog(self, text, path=None):
        if path is None:
            path = os.path.expanduser(r"~\Desktop\\") + "log_" + self.datasource.name + ".txt"
        with open(path, "a+") as logFile:
            print(text, file=logFile)
        print(text)



    def _buildIdentifierDict(self):
        dict = {}
        for identifier in self.datasource.identifiers:
            dict[identifier.type_] = identifier
        return dict