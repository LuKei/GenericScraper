import unittest
from Test.DatabaseAccessTest import DatabaseAccessTest
from Datasource import Datasource
from HtmlIdentifier import  HtmlIdentifier, IdentifierType
from Scraper import Scraper

class ScraperTest(unittest.TestCase):

    def test_scrapeWebsite(self):
        dbAccess = DatabaseAccessTest.createDbAccess()

        #Bundesfinanzministerium
        datasource1 = self.createBundesfinanzministeriumDatasource()


        #Bundesministerium für Wirtschaft und Energie

        datasource2 = self.createBMWiDatasource()

        datasources = [datasource1, datasource2]
        scraper = Scraper(dbAccess)
        scraper.scrapeDatasource(datasource2)
        #scraper.scrapeDatasources(datasources)



    def createBundesfinanzministeriumDatasource(self):

        nextPageIdentifier = HtmlIdentifier("div", "special-box", IdentifierType.NEXTPAGE)
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "navIndex clearfix"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "forward active"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "active"))

        listItemIdentifier = HtmlIdentifier("ol", "result-list", IdentifierType.LISTITEM)
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "result-list-entry"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "listenteaser-wrapper"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "teaser listenteaser teaser-publication"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "listenteaser-text  no-img "))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("h3"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "pbhandout"))

        downloadLinkIdentifier = HtmlIdentifier("div", "article-content-wrapper", IdentifierType.DOWNLOADLINK)
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "article-text-wrapper"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "article-text singleview"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "publication-download-link"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "download"))

        identifiers = [nextPageIdentifier, listItemIdentifier, downloadLinkIdentifier]

        datasource = Datasource("Bundesministerium der Finanzen",
                                "http://www.bundesfinanzministerium.de/Web/DE/Service/"
                                "Publikationen/BMF_Schreiben/bmf_schreiben.html",
                                identifiers=identifiers)
        return datasource


    def createBMWiDatasource(self):

        nextPageIdentifier = HtmlIdentifier("div", "container", IdentifierType.NEXTPAGE)
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "pagination"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "pagination-item"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "pagination-link"))

        listItemIdentifier = HtmlIdentifier("div", "container container-search-results", IdentifierType.LISTITEM)
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "search-results"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "card-list card-list-search-results"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "card-list-item"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "card card-is-linked"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "card-block"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "card-link-overlay"))

        documentTitleIdentifier = HtmlIdentifier("div", "container main-head", IdentifierType.DOCUMENTTITLE)
        documentTitleIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "headline headline-main"))
        documentTitleIdentifier.addInnermostIdentifier(HtmlIdentifier("h1", "title"))

        documentTitleIdentifier = HtmlIdentifier("div", "container main-head", IdentifierType.DOCUMENTSUBTITLE)
        documentTitleIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "headline headline-main"))
        documentTitleIdentifier.addInnermostIdentifier(HtmlIdentifier("h1", "title"))
        documentTitleIdentifier.addInnermostIdentifier(HtmlIdentifier("span", "subtitle"))

        downloadLinkIdentifier = HtmlIdentifier("div", "content-block", IdentifierType.DOWNLOADLINK)
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "content"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "document-info document-info-law"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "document-info-item-links"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("p"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "link link-download"))

        identifiers = [nextPageIdentifier, listItemIdentifier, documentTitleIdentifier, downloadLinkIdentifier]

        datasource = Datasource("Bundesministerium für Wirtsschaft und Energie",
                                 "http://www.bmwi.de/Navigation/DE/Service/Gesetze-und-Verordnungen/"
                                 "gesetze-und-verordnungen.html",
                                identifiers=identifiers)
        return datasource

