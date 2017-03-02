import os
import unittest
from DatabaseAccess import DatabaseAccess
from HtmlIdentifier import HtmlIdentifier, IdentifierType
from DocumentTest import DocumentTest
from DatasourceTest import DatasourceTest



class DatabaseAccessTest(unittest.TestCase):

    def test_datasourceExists(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        datasource = DatasourceTest.createDatasource("testname")

        self.assertFalse(dbAcces.datasourceExists("testname"))
        dbAcces.addDatasource(datasource)
        self.assertTrue(dbAcces.datasourceExists("testname"))

        dbAcces.close()
        os.remove("test.db")

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
        os.remove("test.db")


    def test_addDatasource(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        datasource = DatasourceTest.createDatasource("testname")

        self.assertTrue(dbAcces.addDatasource(datasource)) #Website erfolgreich einfügen
        self.assertFalse(dbAcces.addDatasource(datasource)) #Website bereits in Db

        dbAcces.close()
        os.remove("test.db")

    def test_addDocument(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = DatasourceTest.createDatasource("testname")
        doc = DocumentTest.createDocument("testtitle", website)

        self.assertEqual(dbAcces.addDocument(doc, website), -1) #Website existiert nicht

        dbAcces.addDatasource(website)

        self.assertGreater(dbAcces.addDocument(doc, website), 0) #Text erfolgreich einfügen
        self.assertEqual(dbAcces.addDocument(doc, website), -1) #Text bereits in Db

        dbAcces.close()
        os.remove("test.db")

    def test_getDatasource(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        website = DatasourceTest.createDatasource("testname")

        self.assertEqual(dbAcces.getDatasource(website.name), None) #Website nicht in Db enthalten
        dbAcces.addDatasource(website)
        websiteFromDb = dbAcces.getDatasource(website.name)
        #Attribute vergleichen:
        self.assertEqual(websiteFromDb.name, website.name)
        self.assertEqual(websiteFromDb.url, website.url)

        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.NEXTPAGE).tagName, website.getOutermostIdentifier(IdentifierType.NEXTPAGE).tagName)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.NEXTPAGE).class_, website.getOutermostIdentifier(IdentifierType.NEXTPAGE).class_)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.LISTITEM).tagName, website.getOutermostIdentifier(IdentifierType.LISTITEM).tagName)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.LISTITEM).class_, website.getOutermostIdentifier(IdentifierType.LISTITEM).class_)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.DOWNLOADLINK).tagName, website.getOutermostIdentifier(IdentifierType.DOWNLOADLINK).tagName)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.DOWNLOADLINK).class_, website.getOutermostIdentifier(IdentifierType.DOWNLOADLINK).class_)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE).tagName, website.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE).tagName)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE).class_,
                         website.getOutermostIdentifier(IdentifierType.DOCUMENTTITLE).class_)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT).tagName,
                         website.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT).tagName)
        self.assertEqual(websiteFromDb.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT).class_,
                         website.getOutermostIdentifier(IdentifierType.LEGALTEXTCONTENT).class_)

        dbAcces.close()
        os.remove("test.db")

    def test_getDatasources(self):
        dbAcces = DatabaseAccessTest.createDbAccess()
        datasource1 = DatasourceTest.createDatasource("testname1")
        datasource2 = DatasourceTest.createDatasource("testname2")

        self.assertEqual(dbAcces.getDatasources(), [])

        dbAcces.addDatasource(datasource1)
        dbAcces.addDatasource(datasource2)

        self.assertEqual(len(dbAcces.getDatasources()), 2)

        dbAcces.close()
        os.remove("test.db")

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
        os.remove("test.db")

    @staticmethod
    def createDbAccess():
        return DatabaseAccess("", "test")


    if __name__ == '__main__':
        unittest.main()