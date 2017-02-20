import unittest
from DatabaseAccessTest import DatabaseAccessTest
from Datasource import Datasource
from HtmlIdentifier import  HtmlIdentifier, IdentifierType, HtmlAttribute
from Scraper import Scraper

class ScraperTest(unittest.TestCase):

    def test_scrapeWebsite(self):
        dbAccess = DatabaseAccessTest.createDbAccess()


        datasource1 = self.createBundesfinanzministeriumDatasource()
        datasource2 = self.createBMWiDatasource()
        datasource3 = self.createLegislationGovDatasource()
        datasource4 = self.createBundesrechnungshofDatasource()
        datasource5 = self.createEurLexDatasource()
        datasource6 = self.createCuriaDatasource()
        datasource7 = self.createBundesfinanzhofDatasource()


        datasources = [datasource1, datasource4]
        scraper = Scraper(dbAccess)
        scraper.scrapeDatasource(datasource3)
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

        dateIdentifier = HtmlIdentifier("div", "article-wrapper publication pbhandout no-image", IdentifierType.DATEIDENTIFIER)
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "article-content-wrapper"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "article-text-wrapper"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "article-text singleview"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "doc-data publication"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("li", ))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("span", "value"))

        identifiers = [nextPageIdentifier, listItemIdentifier, downloadLinkIdentifier, dateIdentifier]

        datasource = Datasource("Bundesministerium der Finanzen",
                                "http://www.bundesfinanzministerium.de/Web/DE/Service/"
                                "Publikationen/BMF_Schreiben/bmf_schreiben.html",
                                identifiers=identifiers)
        return datasource

    # Bundesministerium für Wirtschaft und Energie
    def createBMWiDatasource(self):

        nextPageIdentifier = HtmlIdentifier("div", "container", IdentifierType.NEXTPAGE)
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "pagination"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "pagination-item"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "pagination-link"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("span", "link-icon icon icon-arrow-right"))

        listItemIdentifier = HtmlIdentifier("div", "container container-search-results", IdentifierType.LISTITEM)
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "search-results"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "card-list card-list-search-results"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "card-list-item"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "card card-is-linked"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "card-block"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "card-link-overlay"))

        titleIdentifier = HtmlIdentifier("div", "container main-head", IdentifierType.DOCUMENTTITLE)
        titleIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "headline headline-main"))
        titleIdentifier.addInnermostIdentifier(HtmlIdentifier("h1", "title"))

        downloadLinkIdentifier = HtmlIdentifier("div", "content-block", IdentifierType.DOWNLOADLINK)
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "content"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "document-info document-info-law"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "document-info-item-links"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("p"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "link link-download"))

        dateIdentifier = HtmlIdentifier("div", "container main-head", IdentifierType.DATEIDENTIFIER)
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "headline headline-main"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("p", "topline"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("span", "date"))

        identifiers = [nextPageIdentifier, listItemIdentifier, titleIdentifier, downloadLinkIdentifier, dateIdentifier]

        datasource = Datasource("Bundesministerium für Wirtschaft und Energie",
                                 "http://www.bmwi.de/Navigation/DE/Service/Gesetze-und-Verordnungen/"
                                 "gesetze-und-verordnungen.html",
                                identifiers=identifiers)
        return datasource


    def createBundesrechnungshofDatasource(self):

        nextPageIdentifier = HtmlIdentifier("div", "listingBar", IdentifierType.NEXTPAGE)
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("span", "next"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a"))

        listItemIdentifier = HtmlIdentifier("table", "report-preview-items listing", IdentifierType.LISTITEM)
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tr", "reportEntry"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("td"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("a", additionalAttributes=[HtmlAttribute("title", "")]))


        titleIdentifier = HtmlIdentifier("div", type_=IdentifierType.DOCUMENTTITLE)
        titleIdentifier.addInnermostIdentifier(HtmlIdentifier("div"))
        titleIdentifier.addInnermostIdentifier(HtmlIdentifier("h1", "documentFirstHeading"))

        downloadLinkIdentifier = HtmlIdentifier("dl", "portlet portletDownloadPortlet", IdentifierType.DOWNLOADLINK)
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("dd", "portletItem"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "listTypeSquare"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("li"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("a", additionalAttributes=[HtmlAttribute("title", "Langfassung", exactmatch=False)]))

        dateIdentifier = HtmlIdentifier("div", type_=IdentifierType.DATEIDENTIFIER, additionalAttributes=[HtmlAttribute("id", "content-core")])
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div", additionalAttributes=[HtmlAttribute("id", "parent-fieldname-releasedate-9ffa67083e994720ae3c739b7af8ed03")]))

        ajaxWaitIdentifier = HtmlIdentifier("table", "report-preview-items listing", type_=IdentifierType.AJAXWAIT)

        identifiers = [nextPageIdentifier, listItemIdentifier, dateIdentifier,
                       titleIdentifier, downloadLinkIdentifier, ajaxWaitIdentifier]

        datasource = Datasource("Bundesrechnungshof",
                                "https://www.bundesrechnungshof.de/de/veroeffentlichungen/"
                                "datenbank-veroeffentlichungen#b_start=0",
                                identifiers=identifiers, isUsingAjax=True)
        return datasource


    def createEurLexDatasource(self):

        nextPageIdentifier = HtmlIdentifier("div", "headerResult", IdentifierType.NEXTPAGE)
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("form", additionalAttributes=[HtmlAttribute("id", "pagingForm")]))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("p", "pagination"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("img", additionalAttributes=[HtmlAttribute("alt", "Next")]))

        listItemIdentifier = HtmlIdentifier("table", "documentTable", IdentifierType.LISTITEM)
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tr"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("td", "publicationTitle"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("h3"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "title"))

        downloadLinkIdentifier = HtmlIdentifier("div", "tabContent", IdentifierType.DOWNLOADLINK)
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("table", additionalAttributes=[HtmlAttribute("id", "availableFormat")]))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("tr"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("td"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("a", additionalAttributes=[HtmlAttribute("id", "format_language_table_PDF_DE")]))

        dateIdentifier = HtmlIdentifier("div", "box", IdentifierType.DATEIDENTIFIER)
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div", additionalAttributes=[HtmlAttribute("id", "text")]))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div", additionalAttributes=[HtmlAttribute("id", "textTabContent")]))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "tabContent"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("div"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("table"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("tr"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("td"))
        dateIdentifier.addInnermostIdentifier(HtmlIdentifier("p", "hd-date"))

        identifiers = [nextPageIdentifier, listItemIdentifier, downloadLinkIdentifier, dateIdentifier]

        datasource = Datasource("EUR-Lex",
                                "http://eur-lex.europa.eu/search.html?qid=1486377338433&CASE_LAW_SUMMARY=false&DTS_"
                                "DOM=EU_LAW&type=advanced&DTS_SUBDOM=EU_CASE_LAW",
                                identifiers=identifiers)
        return datasource


    def createLegislationGovDatasource(self):

        nextPageIdentifier = HtmlIdentifier("div", "contentFooter", IdentifierType.NEXTPAGE)
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "interface"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "prevPagesNextNav"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("ul"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("li", "pageLink next"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a", additionalAttributes=[HtmlAttribute("title", "next page")]))

        listItemIdentifier = HtmlIdentifier("div", type_=IdentifierType.LISTITEM, additionalAttributes=[HtmlAttribute("id", "content")])
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("table"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tr"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("td"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("a"))

        titleIdentifier = HtmlIdentifier("div", type_=IdentifierType.DOCUMENTTITLE, additionalAttributes=[HtmlAttribute("id", "layout2")])
        titleIdentifier.addInnermostIdentifier(HtmlIdentifier("h1", "pageTitle"))

        downloadLinkIdentifier = HtmlIdentifier("div", type_=IdentifierType.DOWNLOADLINK,  additionalAttributes=[HtmlAttribute("id", "moreResources")])
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("div", "content"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("ul", "toolList"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("li"))
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "pdfLink"))

        identifiers = [nextPageIdentifier, listItemIdentifier, titleIdentifier, downloadLinkIdentifier]

        datasource = Datasource("legislation.gov",
                                "http://www.legislation.gov.uk/2012-*",
                                identifiers=identifiers)
        return datasource


    def createCuriaDatasource(self):
        nextPageIdentifier = HtmlIdentifier("div", "pagination", IdentifierType.NEXTPAGE)
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("img", additionalAttributes=[HtmlAttribute("title", "Letztes Dokument anzeigen")]))

        listItemIdentifier = HtmlIdentifier("table", "detail_table_douments", IdentifierType.LISTITEM)
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tr", "table_document_ligne"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("td", "table_cell_links_eurlex"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("table"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tr"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("td"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("div", additionalAttributes=[HtmlAttribute("id", "docHtml")]))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("a"))

        downloadLinkIdentifier = HtmlIdentifier("", "", IdentifierType.DOWNLOADLINK)

        dateIdentifier = HtmlIdentifier("", "", IdentifierType.DATEIDENTIFIER)

        identifiers = [nextPageIdentifier, listItemIdentifier, downloadLinkIdentifier, dateIdentifier]

        datasource = Datasource("Bundesministerium der Finanzen",
                                "http://www.bundesfinanzministerium.de/Web/DE/Service/"
                                "Publikationen/BMF_Schreiben/bmf_schreiben.html",
                                identifiers=identifiers)
        return datasource


    def createBundesfinanzhofDatasource(self):

        nextPageIdentifier = HtmlIdentifier("form", type_=IdentifierType.NEXTPAGE, additionalAttributes=[HtmlAttribute("name", "list")])
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("table"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("thead"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("tr", "kopfzeile"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("td", "ETitelKopf"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("table"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("tr"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("td", "pagenumber"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("a"))
        nextPageIdentifier.addInnermostIdentifier(HtmlIdentifier("img", additionalAttributes=[HtmlAttribute("title", "nächste Seite")]))

        listItemIdentifier = HtmlIdentifier("form", type_=IdentifierType.LISTITEM, additionalAttributes=[HtmlAttribute("name", "list")])
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("table"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tbody"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("tr"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("td", "EAz"))
        listItemIdentifier.addInnermostIdentifier(HtmlIdentifier("a", "doklink"))

        titleIdentifier = HtmlIdentifier("p", "ueberchrift",type_=IdentifierType.DOCUMENTTITLE)

        downloadLinkIdentifier = HtmlIdentifier("p", "printlink", IdentifierType.DOWNLOADLINK)
        downloadLinkIdentifier.addInnermostIdentifier(HtmlIdentifier("a"))

        ajaxWaitIdentifier = HtmlIdentifier("input", type_=IdentifierType.AJAXWAIT, additionalAttributes=[HtmlAttribute("type", "submit")])

        identifiers = [nextPageIdentifier, listItemIdentifier, titleIdentifier,
                       downloadLinkIdentifier, ajaxWaitIdentifier]

        datasource = Datasource("Bundesfinanzhof",
                                "https://www.bundesfinanzhof.de/entscheidungen/entscheidungen-online",
                                identifiers=identifiers, isUsingAjax=True)
        return datasource