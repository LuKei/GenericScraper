import sqlite3
from Website import Website
from LegalText import LegalText
from HtmlIdentifier import IdentifierType
from HtmlIdentifier import HtmlIdentifier

class DatabaseAccess:

    def __init__(self, filename):
        self.filename = filename
        self.connection = sqlite3.connect(filename + ".db")
        cursor = self.connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS Website(Id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
                            "url TEXT NOT NULL, isUsingAjax BOOLEAN NOT NULL, isMultiPage BOOLEAN NOT NULL)")

        cursor.execute("CREATE TABLE IF NOT EXISTS LegalText(Id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
                            "text TEXT NOT NULL, location TEXT NOT NULL, WebsiteId INTEGER NOT NULL, "
                       "FOREIGN KEY (WebsiteId) REFERENCES Website(Id))")

        cursor.execute("CREATE  TABLE  IF NOT EXISTS HtmlIdentifier(Id INTEGER PRIMARY KEY, tag TEXT NOT NULL, "
                       "class TEXT NOT NULL, type INTEGER NOT NULL, WebsiteId INTEGER NOT NULL, "
                       "FOREIGN KEY (WebsiteId) REFERENCES Website(Id))")



    def websiteExists(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Id FROM Website WHERE name = ?", (name,))
        r = cursor.fetchone()
        if r is None:
            return False
        return True



    def legalTextExists(self, text):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Id FROM LegalText WHERE title = ?", (text.title,))
        r = cursor.fetchone()
        if r is None:
            return False
        return True


    def legalTextTitlesInDb(self, website):
        cursor = self.connection.cursor()
        cursor.execute("SELECT title FROM LegalText AS lt INNER JOIN Website AS w ON lt.WebsiteId = w.Id "
                       "WHERE w.name = ?", (website.name,))
        return cursor.fetchall()



    def addWebsite(self, website):
        if self.websiteExists(website.name):
           print("Es existiert bereits eine Webseite mit diesem Namen.")
           return False

        cursor = self.connection.cursor()

        websiteToInsert = (None, website.name, website.url, website.isUsingAjax, website.isMultiPage)
        cursor.execute("INSERT INTO Website VALUES(?,?,?,?,?)", websiteToInsert)

        r = cursor.execute("SELECT Id FROM Website AS w WHERE w.name = ?", (website.name,)).fetchone()
        websiteId = int(r[0])

        identifiersToInsert = (
            (None, website.nextPageIdentifier.tag, website.nextPageIdentifier.class_, website.nextPageIdentifier.type.value, websiteId),
            (None, website.listItemIdentifier.tag, website.listItemIdentifier.class_, website.listItemIdentifier.type.value,websiteId),
            (None, website.downloadLinkIdentifier.tag, website.downloadLinkIdentifier.class_, website.downloadLinkIdentifier.type.value,websiteId),
            (None, website.legalTextTitleIdentifier.tag, website.legalTextTitleIdentifier.class_, website.legalTextTitleIdentifier.type.value,websiteId))
        for i in range(0,len(identifiersToInsert)):
            cursor.execute("INSERT INTO HtmlIdentifier VALUES (?,?,?,?,?)", identifiersToInsert[i])

        return True



    def addLegalText(self, legalText, website):
        #TODO: umbauen, so dass mehrere Texte gleichzeitig eingefügt werden können
        if self.legalTextExists(legalText):
            print("Ein Gesetzestext mit dem Titel " + legalText.title + " existert bereits.")
            return False

        cursor = self.connection.cursor()
        r = cursor.execute("SELECT Id FROM Website AS w WHERE w.name = ?", (website.name,)).fetchone()
        if r is None:
            print("Eine Webseite mit diesem Namen existiert nicht. Fügen Sie den Gesetzestext einer exsitierenden "
                  "Webseite hinzu")
            return False

        websiteId = int(r[0])

        tupleToInsert = (None, legalText.title, legalText.text, legalText.location, websiteId)
        cursor.execute("INSERT INTO LegalText VALUES(?,?,?,?,?)", tupleToInsert)
        return True


    def getWebsite(self, name):
        if not self.websiteExists(name):
            print("Keine Webseite mit diesem Namen gefunden.")
            return None

        cursor = self.connection.cursor()
        cursor.execute("SELECT Id, name, url, isUsingAjax, isMultiPage FROM Website WHERE name = ?", (name,))
        r1 = cursor.fetchone()

        cursor.execute("SELECT tag, class, type FROM HtmlIdentifier WHERE WebsiteId = ? AND type = ?", (r1[0], IdentifierType.NEXTPAGE.value))
        r2 = cursor.fetchone()
        nextPageIdentifier = HtmlIdentifier(r2[0],r2[1],IdentifierType(r2[2]))
        cursor.execute("SELECT tag, class, type FROM HtmlIdentifier WHERE WebsiteId = ? AND type = ?", (r1[0], IdentifierType.LISTITEM.value))
        r2 = cursor.fetchone()
        listItemIdentifier = HtmlIdentifier(r2[0], r2[1], IdentifierType(r2[2]))
        cursor.execute("SELECT tag, class, type FROM HtmlIdentifier WHERE WebsiteId = ? AND type = ?", (r1[0], IdentifierType.DOWNLOADLINK.value))
        r2 = cursor.fetchone()
        downloadLinkIdentifier = HtmlIdentifier(r2[0], r2[1], IdentifierType(r2[2]))
        cursor.execute("SELECT tag, class, type FROM HtmlIdentifier WHERE WebsiteId = ? AND type = ?", (r1[0], IdentifierType.LEGALTEXTTITLE.value))
        r2 = cursor.fetchone()
        legalTextTitleIdentifier = HtmlIdentifier(r2[0], r2[1], IdentifierType(r2[2]))

        website = Website(r1[1], r1[2], r1[3], r1[4], nextPageIdentifier, listItemIdentifier, downloadLinkIdentifier, legalTextTitleIdentifier)

        return website



    def getLegalTexts(self, website):
        texts = []

        cursor = self.connection.cursor()
        cursor.execute("SELECT lt.title, lt.text, lt.location FROM LegalText AS lt INNER JOIN Website AS w ON lt.WebsiteId = w.Id "
                       "WHERE w.name = ?", (website.name,))
        rows = cursor.fetchall()

        for r in rows:
            text = LegalText(r[0],r[1],r[2], website)
            texts.append(text)

        return texts

    def close(self):
        self.connection.close()



