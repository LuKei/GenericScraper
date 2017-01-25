import os
import unittest
from DatabaseAccess import DatabaseAccess
from HtmlIdentifier import HtmlIdentifier, IdentifierType
from Test.DatasourceTest import DatasourceTest
from Test.DocumentTest import DocumentTest


class DatabaseAccessTest(unittest.TestCase):

    def test_datasourceExists(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        datasource = DatasourceTest.createDatasource("testname")

        self.assertFalse(dbAcces.datasourceExists("testname"))
        dbAcces.addDatasource(datasource)
        self.assertTrue(dbAcces.datasourceExists("testname"))

        dbAcces.close()
        os.remove("Test.db")

    def test_documentExists(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        datasource = DatasourceTest.createDatasource("testname")
        doc = DocumentTest.createDocument("testtitle", datasource)

        self.assertFalse(dbAcces.documentExists(doc.title, datasource.name))
        dbAcces.addDocument(doc, datasource)
        self.assertFalse(dbAcces.documentExists(doc.title, datasource.name))
        dbAcces.addDatasource(datasource)
        dbAcces.addDocument(doc, datasource)
        self.assertTrue(dbAcces.documentExists(doc.title, datasource.name))

        dbAcces.close()
        os.remove("Test.db")

    def test_documentTitlesInDb(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        datasource1 = DatasourceTest.createDatasource("testname1")
        datasource2 = DatasourceTest.createDatasource("testname2")
        doc1 = DocumentTest.createDocument("testtitle1", datasource1)
        doc2 = DocumentTest.createDocument("testtitle2", datasource1)
        doc3 = DocumentTest.createDocument("testtitle3", datasource2)
        doc4 = DocumentTest.createDocument("testtitle4", datasource2)


        self.assertEqual(len(dbAcces.documentTitlesInDb(datasource1)),0)

        dbAcces.addDatasource(datasource1)
        dbAcces.addDatasource(datasource2)
        dbAcces.addDocument(doc1, datasource1)
        dbAcces.addDocument(doc2, datasource1)
        dbAcces.addDocument(doc3, datasource2)
        dbAcces.addDocument(doc4, datasource2)

        docTitles = dbAcces.documentTitlesInDb(datasource1)
        self.assertTrue(docTitles[0], "testtitle1")
        self.assertTrue(docTitles[1], "testtitle2")

        dbAcces.close()
        os.remove("Test.db")

    def test_addDatasource(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        datasource = DatasourceTest.createDatasource("testname")

        self.assertTrue(dbAcces.addDatasource(datasource)) #Website erfolgreich einfügen
        self.assertFalse(dbAcces.addDatasource(datasource)) #Website bereits in Db

        dbAcces.close()
        os.remove("Test.db")

    def test_addDocument(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = DatasourceTest.createDatasource("testname")
        doc = DocumentTest.createDocument("testtitle", website)

        self.assertFalse(dbAcces.addDocument(doc, website)) #Website existiert nicht

        dbAcces.addDatasource(website)

        self.assertTrue(dbAcces.addDocument(doc, website)) #Text erfolgreich einfügen
        self.assertFalse(dbAcces.addDocument(doc, website)) #Text bereits in Db

        dbAcces.close()
        os.remove("Test.db")

    def test_getDatasource(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = DatasourceTest.createDatasource("testname")

        self.assertEqual(dbAcces.getDatasource(website.name), None) #Website nicht in Db enthalten
        dbAcces.addDatasource(website)
        websiteFromDb = dbAcces.getDatasource(website.name)
        #Attribute vergleichen:
        self.assertEqual(websiteFromDb.name, website.name)
        self.assertEqual(websiteFromDb.url, website.url)

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

    def test_getDocuments(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website1 = DatasourceTest.createDatasource("testname1")
        website2 = DatasourceTest.createDatasource("testname2")
        text1 = DocumentTest.createDocument("testtitle1", website1)
        text2 = DocumentTest.createDocument("testtitle2", website1)
        text3 = DocumentTest.createDocument("testtitle3", website2)
        text4 = DocumentTest.createDocument("testtitle4", website2)

        self.assertEqual(len(dbAcces.getDocuments(website1)), 0) #keine Texts in der Db

        dbAcces.addDatasource(website1)
        dbAcces.addDatasource(website2)
        dbAcces.addDocument(text1, website1)
        dbAcces.addDocument(text2, website1)
        dbAcces.addDocument(text3, website2)
        dbAcces.addDocument(text4, website2)

        textsFromDb = dbAcces.getDocuments(website1)
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