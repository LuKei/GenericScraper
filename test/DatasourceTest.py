import unittest
from Datasource import Datasource
from HtmlIdentifier import HtmlIdentifier, IdentifierType, HtmlAttribute


class DatasourceTest(unittest.TestCase):

    def test_attributes(self):
        website = DatasourceTest.createDatasource("testname")
        self.assertEqual(website.name, "testname")
        self.assertEqual(website.url, "testurl")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.NEXTPAGE).tagName, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.NEXTPAGE).class_, "testclass")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.NEXTPAGE).innerIdentifier.additionalAttributes[0].name, "testname")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.NEXTPAGE).innerIdentifier.additionalAttributes[0].value, "testvalue")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.LISTITEM).tagName, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.LISTITEM).class_, "testclass")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.DOWNLOADLINK).tagName, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.DOWNLOADLINK).class_, "testclass")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE).tagName, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE).class_, "testclass")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT).tagName, "testtag")
        self.assertEqual(website.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT).class_, "testclass")



    @staticmethod
    def createDatasource(name):
        identifiers = [HtmlIdentifier("testtag", "testclass", IdentifierType.NEXTPAGE),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.DOWNLOADLINK),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.LISTITEM),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.DOCUMENTTITLE),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.LEGALTEXTCONTENT)]

        identifiers[0].addInnermostIdentifier(HtmlIdentifier("testtag1", "testclass1", IdentifierType.NEXTPAGE, [HtmlAttribute("testname", "testvalue")]))

        return Datasource(name, "testurl", identifiers)

        #return Datasource(name="nameWithoutIdentifiers", url="urlWithoutIdentifiers", isUsingAjax=False)

    if __name__ == '__main__':
        unittest.main()