import sys
import sqlite3
import Website
import LegalText

class DatabaseAccess:

    def __init__(self, filename):
        self.filename = filename
        self.connection = sqlite3.connect(filename + ".db")
        cursor = self.connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS Website(Id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
                            "url TEXT NOT NULL, isUsingAjax BOOLEAN NOT NULL, isMultiPage BOOLEAN NOT NULL, "
                            "nextPageHtmlFrag TEXT NOT NULL, listItemHtmlFrag TEXT NOT NULL, "
                            "downloadHtmlFrag TEXT NOT NULL, legalTextTitleHtmlFrag TEXT NOT NULL)")

        cursor.execute("CREATE TABLE IF NOT EXISTS LegalText(Id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
                            "text TEXT NOT NULL, location TEXT NOT NULL, WebsiteId INTEGER NOT NULL, "
                       "FOREIGN KEY (WebsiteId) REFERENCES Website(Id))")



    def websiteExists(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Id FROM Website WHERE name = ?", name)
        r = cursor.fetchone()
        if len(r) > 0:
            return True
        return False



    def legalTextExists(self, title):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Id FROM LegalText WHERE title = ?", title)
        r = cursor.fetchone()
        if len(r) > 0:
            return True
        return False


    def legalTextTitlesInDb(self, website):
        cursor = self.connection.cursor()
        cursor.execute("SELECT title FROM LegalText AS lt INNER JOIN Website AS w ON lt.WebsiteId = w.Id "
                       "WHERE w.name = ?", website.name)
        return cursor.fetchall()



    def addWebsite(self, website):
        if self.websiteExists(website.name):
           print("Es existiert bereits eine Webseite mit diesem Namen.")
           return

        cursor = self.connection.cursor()
        tupleToInsert = (website.name, website.url, website.isUsingAjax, website.isMultiPage, website.nextPageHtmlFrag,
                         website.listItemHtmlFrag, website.downloadHtmlFrag, website.legalTextTitleHtmlFrag)
        cursor.execute("INSERT INTO Website VALUES(?,?,?,?,?,?,?,?)", tupleToInsert)



    def addLegalText(self, legalText, website):
        #TODO: umbauen, so dass mehrere Texte gleichzeitig eingefügt werden können
        if self.legalTextExists(self, legalText.title):
            print("Ein Gesetzestext mit dem Titel" + legalText.title + "existert bereits.")
            return

        cursor = self.connection.cursor()
        tupleToInsert = (legalText.title, legalText.text)
        cursor.execute("INSERT INTO Website VALUES(?,?,?,?,?,?,?,?)", tupleToInsert)



    def getWebsite(self, name):
        if not self.websiteExists(name):
            print("Keine Webseite mit diesem Namen gefunden.")
            return None

        cursor = self.connection.cursor()
        cursor.execute("SELECT w.name, w.url, w.isUsingAjax, w.isMultiPage, w.nextPageHtmlFrag, w.listItemHtmlFrag,"
                       " w.downloadHtmlFrag, w.legalTextTitleHtmlFrag FROM Website AS w WHERE name = ?", name)
        r = cursor.fetchone()

        website = Website(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7])
        return website



    def getLegalTexts(self, website):
        texts = []

        cursor = self.connection.cursor()
        cursor.execute("SELECT lt.title, lt.text, lt.location FROM LegalText AS lt INNER JOIN Website AS w ON lt.WebsiteId = w.Id "
                       "WHERE w.name = ?", website.name)
        rows = cursor.fetchall()

        for r in rows:
            text = LegalText(r[0],r[1],r[2])
            texts.append(text)

        return texts


