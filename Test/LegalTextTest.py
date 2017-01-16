import sys
import unittest
import LegalText


class LegalTextTest(unittest.TestCase):

    def test_attributes(self):
        text = LegalText.LegalText("testtitle","testtext", None)
        self.assertEqual(text.title, "testtitle")
        self.assertEqual(text.text, "testtext")
        self.assertEqual(text.website, None)

    if __name__ == '__main__':
        unittest.main()