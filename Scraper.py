from DatabaseAccess import DatabaseAccess
from ScraperThread import ScraperThread


class Scraper:

    threads = []


    @staticmethod
    def startScrapingDatasource(datasource, datasourceType):
        newThread = ScraperThread(datasource, datasourceType, DatabaseAccess())
        newThread.daemon = True
        Scraper.threads.append(newThread)
        newThread.start()


    @staticmethod
    def stopScrapingDatasource(datasource):
        for thread in Scraper.threads:
            if datasource.name in thread.name:
                thread.stopFlag = True
                Scraper.threads.remove(thread)


