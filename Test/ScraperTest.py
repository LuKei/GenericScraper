import unittest
from Test.DatabaseAccessTest import DatabaseAccessTest
from Website import Website
from HtmlIdentifier import  HtmlIdentifier, IdentifierType
from Scraper import Scraper

class ScraperTest(unittest.TestCase):

    def test_scrapeWebsite(self):
        dbAccess = DatabaseAccessTest.createDbAccess()

        #TODO:
        # identifiers = [HtmlIdentifier("li", "forward active", IdentifierType.NEXTPAGE),
        #                HtmlIdentifier("h3", IdentifierType.LISTITEM),
        #                HtmlIdentifier("a", "download", IdentifierType.DOWNLOADLINK)]
        #
        # identifiers[0].innerIdentifier(HtmlIdentifier("a", "active"))
        # identifiers[1].innerIdentifier(HtmlIdentifier("a", "pbhandout"))

        identifiers = [HtmlIdentifier("a", "download", IdentifierType.DOWNLOADLINK),
                       HtmlIdentifier("a", "pbhandout", IdentifierType.LISTITEM)]

        website = Website("Bundesministerium der Finanzen",
                          "http://www.bundesfinanzministerium.de/Web/DE/Service/"
                          "Publikationen/BMF_Schreiben/bmf_schreiben.html",
                          isUsingAjax=False, isMultiPage=True, identifiers=identifiers)

        scraper = Scraper(dbAccess)
        scraper.scrapeWebsite(website)