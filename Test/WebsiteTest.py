import sys
import unittest
import Website


class WebsiteTest(unittest.TestCase):

    def test_attributes(self):
        website = Website.Website("testname", "testurl", False, True, "testnextPageHtmlFrag", "testlistItemHtmlFrag", "testdownloadHtmlFrag", "testlegalTextTitleHtmlFrag")
        self.assertEqual(website.name, "testname")
        self.assertEqual(website.url, "testurl")
        self.assertFalse(website.isUsingAjax)
        self.assertTrue(website.isMultiPage)
        self.assertEqual(website.nextPageHtmlFrag, "testnextPageHtmlFrag")
        self.assertEqual(website.listItemHtmlFrag, "testlistItemHtmlFrag")
        self.assertEqual(website.downloadHtmlFrag, "testdownloadHtmlFrag")
        self.assertEqual(website.legalTextTitleHtmlFrag, "testlegalTextTitleHtmlFrag")

    if __name__ == '__main__':
        unittest.main()