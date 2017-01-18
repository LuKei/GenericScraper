import os
import unittest
from LegalText import LegalText
from Website import Website
from DatabaseAccess import DatabaseAccess
from HtmlIdentifier import HtmlIdentifier, IdentifierType


class DatabaseAccessTest(unittest.TestCase):

    def test_websiteExists(self):
        dbAcces = self.createDbAccess()
        website = self.createWebsite("testname")
        text = self.createLegalText("testtitle", website)

        self.assertFalse(dbAcces.websiteExists("testname"))
        dbAcces.addWebsite(website)
        self.assertTrue(dbAcces.websiteExists("testname"))

        dbAcces.close()
        os.remove("Test.db")

    def test_legalTextExists(self):
        dbAcces = self.createDbAccess()
        website = self.createWebsite("testname")
        text = self.createLegalText("testtitle", website)

        self.assertFalse(dbAcces.legalTextExists(text))
        dbAcces.addLegalText(text, website)
        self.assertFalse(dbAcces.legalTextExists(text))
        dbAcces.addWebsite(website)
        dbAcces.addLegalText(text, website)
        self.assertTrue(dbAcces.legalTextExists(text))

        dbAcces.close()
        os.remove("Test.db")

    def test_legalTextTitlesInDb(self):
        dbAcces = self.createDbAccess()
        website1 = self.createWebsite("testname1")
        website2 = self.createWebsite("testname2")
        text1 = self.createLegalText("testtitle1", website1)
        text2 = self.createLegalText("testtitle2", website1)
        text3 = self.createLegalText("testtitle3", website2)
        text4 = self.createLegalText("testtitle4", website2)

        self.assertEqual(len(dbAcces.legalTextTitlesInDb(website1)),0)

        dbAcces.addWebsite(website1)
        dbAcces.addWebsite(website2)
        dbAcces.addLegalText(text1, website1)
        dbAcces.addLegalText(text2, website1)
        dbAcces.addLegalText(text3, website2)
        dbAcces.addLegalText(text4, website2)

        textTitles = dbAcces.legalTextTitlesInDb(website1)
        self.assertTrue(textTitles[0], "testtitle1")
        self.assertTrue(textTitles[1], "testtitle2")

        dbAcces.close()
        os.remove("Test.db")

    def test_addWebsite(self):
        dbAcces = self.createDbAccess()
        website = self.createWebsite("testname")

        self.assertTrue(dbAcces.addWebsite(website)) #Website erfolgreich einfügen
        self.assertFalse(dbAcces.addWebsite(website)) #Website bereits in Db

        dbAcces.close()
        os.remove("Test.db")

    def test_addLegalText(self):
        dbAcces = self.createDbAccess()
        website = self.createWebsite("testname")
        text = self.createLegalText("testtitle", website)

        self.assertFalse(dbAcces.addLegalText(text, website)) #Website existiert nicht

        dbAcces.addWebsite(website)

        self.assertTrue(dbAcces.addLegalText(text, website)) #Text erfolgreich einfügen
        self.assertFalse(dbAcces.addLegalText(text, website)) #Text bereits in Db

        dbAcces.close()
        os.remove("Test.db")

    def test_getWebsite(self):
        dbAcces = self.createDbAccess()
        website = self.createWebsite("testname")

        self.assertEqual(dbAcces.getWebsite(website.name), None) #Website nicht in Db enthalten
        dbAcces.addWebsite(website)
        websiteFromDb = dbAcces.getWebsite(website.name)
        #Attribute vergleichen:
        self.assertEqual(websiteFromDb.name, website.name)
        self.assertEqual(websiteFromDb.url, website.url)
        self.assertEqual(websiteFromDb.isUsingAjax, website.isUsingAjax)
        self.assertEqual(websiteFromDb.isMultiPage, website.isMultiPage)
        self.assertEqual(websiteFromDb.nextPageIdentifier.tag, website.nextPageIdentifier.tag)
        self.assertEqual(websiteFromDb.nextPageIdentifier.class_, website.nextPageIdentifier.class_)
        self.assertEqual(websiteFromDb.nextPageIdentifier.type, website.nextPageIdentifier.type)
        self.assertEqual(websiteFromDb.listItemIdentifier.tag, website.listItemIdentifier.tag)
        self.assertEqual(websiteFromDb.listItemIdentifier.class_, website.listItemIdentifier.class_)
        self.assertEqual(websiteFromDb.listItemIdentifier.type, website.listItemIdentifier.type)
        self.assertEqual(websiteFromDb.downloadLinkIdentifier.tag, website.downloadLinkIdentifier.tag)
        self.assertEqual(websiteFromDb.downloadLinkIdentifier.class_, website.downloadLinkIdentifier.class_)
        self.assertEqual(websiteFromDb.downloadLinkIdentifier.type, website.downloadLinkIdentifier.type)
        self.assertEqual(websiteFromDb.legalTextTitleIdentifier.tag, website.legalTextTitleIdentifier.tag)
        self.assertEqual(websiteFromDb.legalTextTitleIdentifier.class_, website.legalTextTitleIdentifier.class_)
        self.assertEqual(websiteFromDb.legalTextTitleIdentifier.type, website.legalTextTitleIdentifier.type)

        dbAcces.close()
        os.remove("Test.db")

    def test_getLegalTexts(self):
        dbAcces = self.createDbAccess()
        website1 = self.createWebsite("testname1")
        website2 = self.createWebsite("testname2")
        text1 = self.createLegalText("testtitle1", website1)
        text2 = self.createLegalText("testtitle2", website1)
        text3 = self.createLegalText("testtitle3", website2)
        text4 = self.createLegalText("testtitle4", website2)

        self.assertEqual(len(dbAcces.getLegalTexts(website1)), 0) #keine Texts in der Db

        dbAcces.addWebsite(website1)
        dbAcces.addWebsite(website2)
        dbAcces.addLegalText(text1, website1)
        dbAcces.addLegalText(text2, website1)
        dbAcces.addLegalText(text3, website2)
        dbAcces.addLegalText(text4, website2)

        textsFromDb = dbAcces.getLegalTexts(website1)
        self.assertEqual(len(textsFromDb), 2)
        self.assertEqual(textsFromDb[0].title, "testtitle1")
        self.assertEqual(textsFromDb[1].title, "testtitle2")

        dbAcces.close()
        os.remove("Test.db")

    def createDbAccess(self):
        return DatabaseAccess("Test")

    def createWebsite(self, name):
        return Website(name, "testurl", False, True,
                                  HtmlIdentifier("testtag", "testclass"),
                                  HtmlIdentifier("testtag", "testclass"),
                                  HtmlIdentifier("testtag", "testclass"),
                                  HtmlIdentifier("testtag", "testclass"))

    def createLegalText(self, title, website):
        return LegalText(title, "testtext", "testlocation", website)

    if __name__ == '__main__':
        unittest.main()