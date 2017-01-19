import unittest
from Website import Website
from HtmlIdentifier import HtmlIdentifier, IdentifierType


class WebsiteTest(unittest.TestCase):

    def test_attributes(self):
        website = WebsiteTest.createWebsite("testname")
        self.assertEqual(website.name, "testname")
        self.assertEqual(website.url, "testurl")
        self.assertFalse(website.isUsingAjax)
        self.assertTrue(website.isMultiPage)
        self.assertEqual(website.getIdentifier(IdentifierType.NEXTPAGE).tag, "testtag")
        self.assertEqual(website.getIdentifier(IdentifierType.NEXTPAGE).class_,"testclass")
        self.assertEqual(website.getIdentifier(IdentifierType.LISTITEM).tag, "testtag")
        self.assertEqual(website.getIdentifier(IdentifierType.LISTITEM).class_,"testclass")
        self.assertEqual(website.getIdentifier(IdentifierType.DOWNLOADLINK).tag, "testtag")
        self.assertEqual(website.getIdentifier(IdentifierType.DOWNLOADLINK).class_,"testclass")
        self.assertEqual(website.getIdentifier(IdentifierType.LEGALTEXTTITLE).tag, "testtag")
        self.assertEqual(website.getIdentifier(IdentifierType.LEGALTEXTTITLE).class_,"testclass")
        self.assertEqual(website.getIdentifier(IdentifierType.LEGALTEXTCONTENT).tag, "testtag")
        self.assertEqual(website.getIdentifier(IdentifierType.LEGALTEXTCONTENT).class_, "testclass")

    @staticmethod
    def createWebsite(name):
        identifiers = [HtmlIdentifier("testtag", "testclass", IdentifierType.NEXTPAGE),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.DOWNLOADLINK),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.LISTITEM),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.LEGALTEXTTITLE),
                       HtmlIdentifier("testtag", "testclass", IdentifierType.LEGALTEXTCONTENT)]

        identifiers[0].innerIdentifier = HtmlIdentifier("testtag", "testclass", IdentifierType.NEXTPAGE)

        return Website(name, "testurl", False, True, identifiers)

    if __name__ == '__main__':
        unittest.main()