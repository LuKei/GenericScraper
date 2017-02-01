import unittest
from Datasource import Datasource
from HtmlIdentifier import HtmlIdentifier, IdentifierType


class DatasourceTest(unittest.TestCase):

    def test_attributes(self):
        website = DatasourceTest.createDatasource("testname")
        self.assertEqual(website.name, "testname")
        self.assertEqual(website.url, "testurl")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.NEXTPAGE).tag, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.NEXTPAGE).class_, "testclass")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.LISTITEM).tag, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.LISTITEM).class_, "testclass")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.DOWNLOADLINK).tag, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.DOWNLOADLINK).class_, "testclass")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE).tag, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE).class_, "testclass")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT).tag, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT).class_, "testclass")

    @staticmethod
    def createDatasource(name):
        identifiers = [HtmlIdentifier("testtag", "testclass", IdentifierType.NEXTPAGE),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.DOWNLOADLINK),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.LISTITEM),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.DOCUMENTTITLE),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.LEGALTEXTCONTENT)]

        identifiers[0].innerIdentifier = HtmlIdentifier("testtag", "testclass", IdentifierType.NEXTPAGE)

        return Datasource(name, "testurl", identifiers)

    if __name__ == '__main__':
        unittest.main()