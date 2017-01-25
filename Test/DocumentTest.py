import unittest
from Document import Document

from Datasource import DatasourceType

class DocumentTest(unittest.TestCase):

    def test_attributes(self):
        text = DocumentTest.createDocument("testtitle", None)
        self.assertEqual(text.title, "testtitle")
        self.assertEqual(text.datasource, None)

    @staticmethod
    def createDocument(title, datasource):
        return Document(title, "testfilepath", datasource, DatasourceType.GESETZESTEXTE, "testurl", "testdate")

    if __name__ == '__main__':
        unittest.main()