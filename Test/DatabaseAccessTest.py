import os
import unittest
import LegalText
import Website
import DatabaseAccess


class DatabaseAccessTest(unittest.TestCase):

    def test_websiteExists(self):
        dbAcces = DatabaseAccess.DatabaseAccess("Test")
        website = Website.Website("testname", "testurl", False, True, "testnextPageHtmlFrag", "testlistItemHtmlFrag", "testdownloadHtmlFrag", "testlegalTextTitleHtmlFrag")
        text = LegalText.LegalText("testtitle","testtext", "testlocation", website)

        self.assertFalse(dbAcces.websiteExists("testname"))
        dbAcces.addWebsite(website)
        self.assertTrue(dbAcces.websiteExists("testname"))

        dbAcces.close()
        os.remove("Test.db")

    def test_legalTextExists(self):
        dbAcces = DatabaseAccess.DatabaseAccess("Test")
        website = Website.Website("testname", "testurl", False, True, "testnextPageHtmlFrag", "testlistItemHtmlFrag",
                                  "testdownloadHtmlFrag", "testlegalTextTitleHtmlFrag")
        text = LegalText.LegalText("testtitle", "testtext", "testlocation", website)

        self.assertFalse(dbAcces.legalTextExists(text))
        dbAcces.addLegalText(text, website)
        self.assertFalse(dbAcces.legalTextExists(text))
        dbAcces.addWebsite(website)
        dbAcces.addLegalText(text, website)
        self.assertTrue(dbAcces.legalTextExists(text))

        dbAcces.close()
        os.remove("Test.db")

    def test_legalTextTitlesInDb(self):
        dbAcces = DatabaseAccess.DatabaseAccess("Test")
        website1 = Website.Website("testname1", "testurl1", False, True, "testnextPageHtmlFrag1", "testlistItemHtmlFrag1",
                                  "testdownloadHtmlFrag1", "testlegalTextTitleHtmlFrag1")
        website2 = Website.Website("testname2", "testurl2", False, True, "testnextPageHtmlFrag2", "testlistItemHtmlFrag2",
                                  "testdownloadHtmlFrag2", "testlegalTextTitleHtmlFrag2")
        text1 = LegalText.LegalText("testtitle1", "testtext1", "testlocation1", website1)
        text2 = LegalText.LegalText("testtitle2", "testtext2", "testlocation2", website1)
        text3 = LegalText.LegalText("testtitle3", "testtext3", "testlocation3", website2)
        text4 = LegalText.LegalText("testtitle4", "testtext4", "testlocation4", website2)

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
        dbAcces = DatabaseAccess.DatabaseAccess("Test")
        website = Website.Website("testname", "testurl", False, True, "testnextPageHtmlFrag", "testlistItemHtmlFrag",
                                  "testdownloadHtmlFrag", "testlegalTextTitleHtmlFrag")

        self.assertTrue(dbAcces.addWebsite(website)) #Website erfolgreich einfügen
        self.assertFalse(dbAcces.addWebsite(website)) #Website bereits in Db

        dbAcces.close()
        os.remove("Test.db")

    def test_addLegalText(self):
        dbAcces = DatabaseAccess.DatabaseAccess("Test")
        website = Website.Website("testname", "testurl", False, True, "testnextPageHtmlFrag", "testlistItemHtmlFrag",
                                  "testdownloadHtmlFrag", "testlegalTextTitleHtmlFrag")
        text = LegalText.LegalText("testtitle", "testtext", "testlocation", website)

        self.assertFalse(dbAcces.addLegalText(text, website)) #Website existiert nicht

        dbAcces.addWebsite(website)

        self.assertTrue(dbAcces.addLegalText(text, website)) #Text erfolgreich einfügen
        self.assertFalse(dbAcces.addLegalText(text, website)) #Text bereits in Db

        dbAcces.close()
        os.remove("Test.db")

    def test_getWebsite(self):
        dbAcces = DatabaseAccess.DatabaseAccess("Test")
        website = Website.Website("testname", "testurl", False, True, "testnextPageHtmlFrag", "testlistItemHtmlFrag",
                                  "testdownloadHtmlFrag", "testlegalTextTitleHtmlFrag")

        self.assertEqual(dbAcces.getWebsite(website.name), None) #Website nicht in Db enthalten
        dbAcces.addWebsite(website)
        websiteFromDb =  dbAcces.getWebsite(website.name)
        #Attribute vergleichen:
        self.assertEqual(websiteFromDb.name, website.name)
        self.assertEqual(websiteFromDb.url, website.url)
        self.assertEqual(websiteFromDb.isUsingAjax, website.isUsingAjax)
        self.assertEqual(websiteFromDb.isMultiPage, website.isMultiPage)
        self.assertEqual(websiteFromDb.nextPageHtmlFrag, website.nextPageHtmlFrag)
        self.assertEqual(websiteFromDb.listItemHtmlFrag, website.listItemHtmlFrag)
        self.assertEqual(websiteFromDb.downloadHtmlFrag, website.downloadHtmlFrag)
        self.assertEqual(websiteFromDb.legalTextTitleHtmlFrag, website.legalTextTitleHtmlFrag)

        dbAcces.close()
        os.remove("Test.db")

    def test_getLegalTexts(self):
        dbAcces = DatabaseAccess.DatabaseAccess("Test")
        website1 = Website.Website("testname1", "testurl1", False, True, "testnextPageHtmlFrag1", "testlistItemHtmlFrag1",
                                  "testdownloadHtmlFrag1", "testlegalTextTitleHtmlFrag1")
        website2 = Website.Website("testname2", "testurl2", False, True, "testnextPageHtmlFrag2", "testlistItemHtmlFrag2",
                                  "testdownloadHtmlFrag2", "testlegalTextTitleHtmlFrag2")
        text1 = LegalText.LegalText("testtitle1", "testtext1", "testlocation1", website1)
        text2 = LegalText.LegalText("testtitle2", "testtext2", "testlocation2", website1)
        text3 = LegalText.LegalText("testtitle1", "testtext3", "testlocation3", website2)
        text4 = LegalText.LegalText("testtitle2", "testtext4", "testlocation4", website2)

        self.assertEqual(len(dbAcces.getLegalTexts(website1)), 0) #keine Texts in der Db

        dbAcces.addWebsite(website1)
        dbAcces.addWebsite(website2)
        dbAcces.addLegalText(text1, website1)
        dbAcces.addLegalText(text2, website1)
        dbAcces.addLegalText(text3, website1)
        dbAcces.addLegalText(text4, website1)

        textsFromDb = dbAcces.getLegalTexts(website1)
        self.assertEqual(len(textsFromDb), 2)
        self.assertEqual(textsFromDb[0].title, "testtitle1")
        self.assertEqual(textsFromDb[1].title, "testtitle2")

        dbAcces.close()
        os.remove("Test.db")

    if __name__ == '__main__':
        unittest.main()