import unittest
from LegalText import LegalText


class LegalTextTest(unittest.TestCase):

    def test_attributes(self):
        text = LegalTextTest.createLegalText("testtitle", None)
        self.assertEqual(text.title, "testtitle")
        self.assertEqual(text.text, "testtext")
        self.assertEqual(text.website, None)

    @staticmethod
    def createLegalText(title, website):
        return LegalText(title, "testtext", "testlocation", website)

    if __name__ == '__main__':
        unittest.main()