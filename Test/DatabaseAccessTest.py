import os
import unittest
from DatabaseAccess import DatabaseAccess
from HtmlIdentifier import HtmlIdentifier, IdentifierType
from Test.WebsiteTest import WebsiteTest
from Test.LegalTextTest import LegalTextTest


class DatabaseAccessTest(unittest.TestCase):

    def test_websiteExists(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = WebsiteTest.createWebsite("testname")
        text = LegalTextTest.createLegalText("testtitle", website)

        self.assertFalse(dbAcces.websiteExists("testname"))
        dbAcces.addWebsite(website)
        self.assertTrue(dbAcces.websiteExists("testname"))

        dbAcces.close()
        os.remove("Test.db")

    def test_legalTextExists(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = WebsiteTest.createWebsite("testname")
        text = LegalTextTest.createLegalText("testtitle", website)

        self.assertFalse(dbAcces.legalTextExists(text.title, website.name))
        dbAcces.addLegalText(text, website)
        self.assertFalse(dbAcces.legalTextExists(text.title, website.name))
        dbAcces.addWebsite(website)
        dbAcces.addLegalText(text, website)
        self.assertTrue(dbAcces.legalTextExists(text.title, website.name))

        dbAcces.close()
        os.remove("Test.db")

    def test_legalTextTitlesInDb(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website1 = WebsiteTest.createWebsite("testname1")
        website2 = WebsiteTest.createWebsite("testname2")
        text1 = LegalTextTest.createLegalText("testtitle1", website1)
        text2 = LegalTextTest.createLegalText("testtitle2", website1)
        text3 = LegalTextTest.createLegalText("testtitle3", website2)
        text4 = LegalTextTest.createLegalText("testtitle4", website2)


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
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = WebsiteTest.createWebsite("testname")

        self.assertTrue(dbAcces.addWebsite(website)) #Website erfolgreich einfügen
        self.assertFalse(dbAcces.addWebsite(website)) #Website bereits in Db

        dbAcces.close()
        os.remove("Test.db")

    def test_addLegalText(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = WebsiteTest.createWebsite("testname")
        text = LegalTextTest.createLegalText("testtitle", website)

        self.assertFalse(dbAcces.addLegalText(text, website)) #Website existiert nicht

        dbAcces.addWebsite(website)

        self.assertTrue(dbAcces.addLegalText(text, website)) #Text erfolgreich einfügen
        self.assertFalse(dbAcces.addLegalText(text, website)) #Text bereits in Db

        dbAcces.close()
        os.remove("Test.db")

    def test_getWebsite(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = WebsiteTest.createWebsite("testname")

        self.assertEqual(dbAcces.getWebsite(website.name), None) #Website nicht in Db enthalten
        dbAcces.addWebsite(website)
        websiteFromDb = dbAcces.getWebsite(website.name)
        #Attribute vergleichen:
        self.assertEqual(websiteFromDb.name, website.name)
        self.assertEqual(websiteFromDb.url, website.url)
        self.assertEqual(websiteFromDb.isUsingAjax, website.isUsingAjax)
        self.assertEqual(websiteFromDb.isMultiPage, website.isMultiPage)

        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.NEXTPAGE).tag, website.getIdentifier(IdentifierType.NEXTPAGE).tag)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.NEXTPAGE).class_, website.getIdentifier(IdentifierType.NEXTPAGE).class_)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.LISTITEM).tag, website.getIdentifier(IdentifierType.LISTITEM).tag)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.LISTITEM).class_, website.getIdentifier(IdentifierType.LISTITEM).class_)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.DOWNLOADLINK).tag, website.getIdentifier(IdentifierType.DOWNLOADLINK).tag)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.DOWNLOADLINK).class_, website.getIdentifier(IdentifierType.DOWNLOADLINK).class_)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.LEGALTEXTTITLE).tag, website.getIdentifier(IdentifierType.LEGALTEXTTITLE).tag)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.LEGALTEXTTITLE).class_,
                         website.getIdentifier(IdentifierType.LEGALTEXTTITLE).class_)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.LEGALTEXTCONTENT).tag,
                         website.getIdentifier(IdentifierType.LEGALTEXTCONTENT).tag)
        self.assertEqual(websiteFromDb.getIdentifier(IdentifierType.LEGALTEXTCONTENT).class_,
                         website.getIdentifier(IdentifierType.LEGALTEXTCONTENT).class_)



        dbAcces.close()
        os.remove("Test.db")

    def test_getLegalTexts(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website1 = WebsiteTest.createWebsite("testname1")
        website2 = WebsiteTest.createWebsite("testname2")
        text1 = LegalTextTest.createLegalText("testtitle1", website1)
        text2 = LegalTextTest.createLegalText("testtitle2", website1)
        text3 = LegalTextTest.createLegalText("testtitle3", website2)
        text4 = LegalTextTest.createLegalText("testtitle4", website2)

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

    @staticmethod
    def createDbAccess():
        return DatabaseAccess("Test")


    if __name__ == '__main__':
        unittest.main()