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
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ScraperThread(threading.Thread):

    def __init__(self, datasource, datasourceType, dbAccess, parser="html5lib"):
        super(ScraperThread, self).__init__()
        self.datasource = datasource
        self.datasourceType = datasourceType
        self.dbAccess = dbAccess
        self.name= "Thread-" + datasource.name
        self.driver = None
        self.stopFlag = False
        self.parser = parser


    def run(self):

        # Variablen für logging
        scrapedDocuments, sameDocument, noDownloadlink, noListItemLink, exceptionCaught, i = 0, 0, 0, 0, 0, 0

        self._writeToLog("Started Scraping: " + str(datetime.datetime.now()))

        with DatabaseAccess.lock:
            if not self.dbAccess.datasourceExists(self.datasource.name):
                self.dbAccess.addDatasource(self.datasource)
                self.dbAccess.commit()

        identifierDict = self._buildIdentifierDict()

        folderPath = self.dbAccess.filePath + "documents_" + self.datasource.name
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)  # Ordner für .pdfs anlegen, falls noch nicht vorhanden

        source = self._getSourceForUrl(self.datasource.url, self.datasource.isUsingAjax, identifierDict.get(IdentifierType.AJAXWAIT, None))
        soup = bs.BeautifulSoup(source, self.parser)

        lastLiLink = ""

        while not self.stopFlag:

            # alle ListItems durchlaufen
            for li in self._getInnerItemsFromSoup(soup, identifierDict[IdentifierType.LISTITEM]):
                i += 1
                print(self.datasource.name + ": " + str(i))

                if self.stopFlag:
                    break
                try:
                    if IdentifierType.LISTITEMLINK in identifierDict:
                        liDownloadlinkitem = self._getItemFromListItem(li, identifierDict[IdentifierType.LISTITEMLINK])
                        if liDownloadlinkitem is not None:
                            liLink = self._getFullLink(liDownloadlinkitem.get("href"), soup)
                        else:
                            noListItemLink += 1
                    else:
                        liLink = self._getFullLink(li.get("href"), soup)
                    if liLink == lastLiLink:
                        continue

                    lastLiLink = liLink

                    liSource = self._getSourceForUrl(liLink, usingAjax=False)
                    liSoup = bs.BeautifulSoup(liSource, self.parser)

                    document = Document(None, None, self.datasource, self.datasourceType, None, time.strftime("%d.%m.%Y"))

                    if IdentifierType.DOCUMENTTITLE in identifierDict:
                        item = self._getItemFromListItemSoup(li, liSoup, identifierDict[IdentifierType.DOCUMENTTITLE])
                        if item is not None:
                            document.title = item.text.strip()
                    if document.title is None:
                        document.title = li.text.strip()

                    if IdentifierType.DOCUMENTSUBTITLE in identifierDict:
                        item = self._getItemFromListItemSoup(li, liSoup, identifierDict[IdentifierType.DOCUMENTSUBTITLE])
                        if item is not None:
                            document.title += item.text.strip()

                    with DatabaseAccess.lock:
                        if self.dbAccess.documentExists(document.title, self.datasource.name):
                            # Wenn Gesetzestext bereits in der Db: neuere Version verwenden.
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
                        item = self._getItemFromListItemSoup(li, liSoup, identifierDict[IdentifierType.DOWNLOADLINK])
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
                    exceptionCaught += 1
                    self._writeToLog("Exception caught at index: " + str(i),
                                        path=os.path.expanduser(r"~\Desktop\\") + "excLog_" + self.datasource.name + ".txt")
                    traceback.print_exc(file=open(os.path.expanduser(r"~\Desktop\\") + "excLog_" + self.datasource.name + ".txt", "a+"))
            try:
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
                    soup = bs.BeautifulSoup(source, self.parser)
            except Exception as e:
                exceptionCaught += 1
                self._writeToLog("Exception caught at index: " + str(i) + " (while trying to navigate to next page)",
                                 path=os.path.expanduser(r"~\Desktop\\") + "excLog_" + self.datasource.name + ".txt")
                traceback.print_exc(file=open(os.path.expanduser(r"~\Desktop\\") + "excLog_" + self.datasource.name + ".txt", "a+"))
                break

        if self.driver is not None:
            self.driver.close()

        if self.stopFlag:
            self._writeToLog("Stopped Scraping: " + str(datetime.datetime.now()))
        else:
            self._writeToLog("Finished Scraping: " + str(datetime.datetime.now()))
        self._writeToLog("Scraped documents: " + str(scrapedDocuments))
        self._writeToLog("Not scraped because of same name: " + str(sameDocument))
        self._writeToLog("Not scraped because list item link was not fount: " + str(noListItemLink))
        self._writeToLog("Not scraped because download link was not found: " + str(noDownloadlink))
        self._writeToLog("Not scraped because an exception occured: " + str(exceptionCaught))
        self._writeToLog("\n\n\n")




    def _getItemFromListItemSoup(self, li, liSoup, identifier):
        # Zuerst im ListItem suchen
        item = self._getItemFromListItem(li, identifier)
        if item is None:
            # Wenn nichts im ListItem gefunden -> auf Seite des ListItems suchen
            items = self._getInnerItemsFromSoup(liSoup, identifier)
            if items is not None and len(items) > 0:
                item = items[0]

        return item


    def _getItemFromListItem(self, li, identifier):
        item = None
        items = self._getInnerItemsFromItems([li], identifier)
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
        url = self.datasource.url
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
                innerItems += item.find_all(lambda tag: self._matchTag(tag, identifier), recursive=False)
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