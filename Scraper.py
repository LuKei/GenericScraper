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





class Scraper:

    threads = []
    driver = None

    @staticmethod
    def startScrapingDatasource(datasource):
        datasourceAlreadyBeingScraped = False

        for thread in Scraper.threads:
            if datasource.name in thread.name:
                print("datasource is already being scraped right now!")
                return None

        newThread = threading.Thread(target=Scraper.scrapeDatasource, args=(datasource, DatabaseAccess()), name="Thread-" + datasource.name)
        newThread.daemon = True
        Scraper.threads.append(newThread)
        newThread.start()


    @staticmethod
    def scrapeDatasource(datasource, dbAccess):

        #Variablen für logging
        scrapedDocuments, sameDocument, noDownloadlink, exceptionCaught = 0, 0, 0, 0

        Scraper._writeToLog("Started Scraping: " + str(datetime.datetime.now().time()), datasource.name)


        with DatabaseAccess.lock:
            if not dbAccess.datasourceExists(datasource.name):
                dbAccess.addDatasource(datasource)
                dbAccess.commit()

        isUsingAjax = datasource.isUsingAjax
        identifierDict = Scraper._buildIdentifierDict(datasource)


        folderPath = dbAccess.filePath + "documents_" + datasource.name
        if not os.path.exists(folderPath):
            os.makedirs(folderPath) # Ordner für .pdfs anlegen, falls noch nicht vorhanden


        source = Scraper._getSourceForUrl(datasource.url, datasource.isUsingAjax, identifierDict.get(IdentifierType.AJAXWAIT, None))
        soup = bs.BeautifulSoup(source, "lxml")

        i = 0

        while True:

            # alle ListItems durchlaufen
            for li in Scraper._getInnerItemsFromSoup(soup, identifierDict[IdentifierType.LISTITEM]):
                try:
                    i += 1
                    print(i)

                    document = Document(None, None, datasource, DatasourceType.GESETZESTEXTE, None, None)


                    if IdentifierType.DOCUMENTTITLE in identifierDict:
                        item = Scraper._getItemFromListItem(li, identifierDict[IdentifierType.DOCUMENTTITLE], datasource, soup)
                        if item is not None:
                            document.title = item.text.strip()
                    if document.title is None:
                        document.title = li.text.strip()


                    if IdentifierType.DOCUMENTSUBTITLE in identifierDict:
                        item = Scraper._getItemFromListItem(li, identifierDict[IdentifierType.DOCUMENTSUBTITLE], datasource, soup)
                        if item is not None:
                            document.title += item.text.strip()

                    if IdentifierType.DATEIDENTIFIER in identifierDict:
                        item = Scraper._getItemFromListItem(li, identifierDict[IdentifierType.DATEIDENTIFIER], datasource, soup)
                        if item is not None:
                            document.date = item.text.strip()

                    with DatabaseAccess.lock:
                        if dbAccess.documentExists(document.title, datasource.name):
                            # Wenn Gesetzestext bereits in der Db: neuere Version verwenden.
                            # Wenn kein Datum gescraped werden kann -> überspringen
                            documentInDb = dbAccess.getDocument(document.title, datasource)
                            if document.date is not None:
                                if documentInDb.date is None or documentInDb.date < document.date:
                                    dbAccess.removeDocument(documentInDb.title, datasource)
                                    dbAccess.commit()
                                else:
                                    sameDocument += 1
                                    continue
                            else:
                                sameDocument += 1
                                continue

                    if IdentifierType.DOWNLOADLINK in identifierDict:
                        item = Scraper._getItemFromListItem(li, identifierDict[IdentifierType.DOWNLOADLINK], datasource, soup)
                        if item is not None:
                            downloadLink = item.get("href")
                        else:
                            noDownloadlink += 1
                            continue

                        downloadResponse = Scraper._getSourceForUrl(Scraper._getFullLink(datasource.url, downloadLink, soup), usingAjax=False)

                        if downloadResponse is not None:
                            document.url = downloadResponse.url
                            with DatabaseAccess.lock:
                                documentId = dbAccess.addDocument(document, datasource)
                                dbAccess.commit()
                            document.filepath = folderPath + "/" + str(documentId)

                            if downloadResponse.info().get_content_subtype() == "html":
                                # options = {"quiet":""}
                                # pdfkit.from_url(downloadResponse.url, document.filepath, options=options)
                                urllib.request.urlretrieve(downloadResponse.url, document.filepath + ".html")
                            else:
                                urllib.request.urlretrieve(downloadResponse.url, document.filepath + ".pdf")
                            with DatabaseAccess.lock:
                                dbAccess.setDocumentFilePath(documentId, document.filepath)
                                dbAccess.commit()

                    scrapedDocuments += 1
                except Exception as e:
                    with DatabaseAccess.lock:
                        dbAccess.rollback()
                    Scraper._writeToLog("Exception caught at index: " + str(i), datasource.name,
                                        path=os.path.expanduser(r"~\Desktop\\") + "excLog_" + datasource.name + ".txt")
                    traceback.print_exc(file=open(os.path.expanduser(r"~\Desktop\\") + "excLog_" + datasource.name + ".txt", "a+"))



            items = Scraper._getInnerItemsFromSoup(soup, identifierDict[IdentifierType.NEXTPAGE])
            if len(items) == 0:
                break
            else:
                nextPageLink = items[0].get("href")
                if nextPageLink is None:
                    nextPageLink = items[0].parent.get("href")
                if nextPageLink is None:
                    break
                source = Scraper._getSourceForUrl(Scraper._getFullLink(datasource.url, nextPageLink, soup), datasource.isUsingAjax,
                                                  identifierDict.get(IdentifierType.AJAXWAIT))
                soup = bs.BeautifulSoup(source, "lxml")

        if Scraper.driver is not None:
            Scraper.driver.close()

        Scraper._writeToLog("Finished Scraping: " + str(datetime.datetime.now().time()), datasource.name)
        Scraper._writeToLog("Scraped documents: " + str(scrapedDocuments), datasource.name)
        Scraper._writeToLog("Not scraped because of same name: " + str(sameDocument), datasource.name)
        Scraper._writeToLog("Not scraped because download link was not found: " + str(noDownloadlink), datasource.name)
        Scraper._writeToLog("Not scraped because an exception occured: " + str(exceptionCaught), datasource.name)
        Scraper._writeToLog("/n/n/n", datasource.name)




    @staticmethod
    def _getItemFromListItem(li, identifier, datasource, soup):
        #Zuerst im ListItem suchen
        item = None
        items = Scraper._getInnerItemsFromItems([li], identifier)
        if items is not None and len(items) > 0:
            item = items[0]
        else:
            #Wenn nichts im ListItem gefunden -> auf Seite des ListItems suchen
            source = Scraper._getSourceForUrl(Scraper._getFullLink(datasource.url, li.get("href"), soup), usingAjax=False)
            soup = bs.BeautifulSoup(source, "lxml")
            items = Scraper._getInnerItemsFromSoup(soup, identifier)
            if items is not None and len(items) > 0:
                item = items[0]

        return item



    @staticmethod
    def _getSourceForUrl(url, usingAjax, ajaxWaitIdentifier=None):
        if usingAjax:
            if Scraper.driver is None:
                Scraper.driver = webdriver.Chrome()
            Scraper.driver.get(url=url)

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

            WebDriverWait(Scraper.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpathWaitString)))

            source = Scraper.driver.page_source

        else:
            source = urllib.request.urlopen(url)

        return source



    @staticmethod
    def _getFullLink(url, link, soup):
        baseItems = Scraper._getInnerItemsFromSoup(soup, HtmlIdentifier("base"))
        if len(baseItems) > 0:
            url = baseItems[0].get("href")

        fullLink = urllib.parse.urljoin(url, link)
        return fullLink



    @staticmethod
    def _getInnerItemsFromSoup(soup, topIdentifier):

        items = []
        if topIdentifier.class_ is None:
            #items = soup.find_all(topIdentifier.tagName, attrs=topIdentifier.getAdditionalAttributesDict())
            items = soup.find_all(lambda tag: Scraper._matchTag(tag, topIdentifier))
        else:
            classes = topIdentifier.class_.split(" ")
            cssSelector = topIdentifier.tagName
            for class_ in classes:
                cssSelector += "." + class_
            items += soup.select(cssSelector)

        if topIdentifier.innerIdentifier is None:
            return items
        else:
            return Scraper._getInnerItemsFromItems(items, topIdentifier.innerIdentifier)



    @staticmethod
    def _getInnerItemsFromItems(items, identifier):

        innerItems = []
        for item in items:
            if identifier.class_ is None:
                #innerItems += item.find_all(identifier.tagName, attrs=identifier.getAdditionalAttributesDict())
                innerItems += item.find_all(lambda tag: Scraper._matchTag(tag, identifier))
            else:
                classes = identifier.class_.split(" ")
                cssSelector = identifier.tagName
                for class_ in classes:
                    cssSelector += "." + class_
                innerItems += item.select(cssSelector)


        if identifier.innerIdentifier is None:
            return innerItems
        else:
            return Scraper._getInnerItemsFromItems(innerItems, identifier.innerIdentifier)



    @staticmethod
    def _matchTag(tag, identifier):
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

    @staticmethod
    def _writeToLog(text, datasourceName, path=None):
        if path is None:
            path = os.path.expanduser(r"~\Desktop\\") + "log_" + datasourceName + ".txt"
        with open(path, "a+") as logFile:
            print(text, file=logFile)
        print(text)


    @staticmethod
    def _buildIdentifierDict(datasource):
        dict = {}
        for identifier in datasource.identifiers:
            dict[identifier.type_] = identifier
        return dict

