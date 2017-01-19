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
                            "text TEXT, location TEXT, WebsiteId INTEGER NOT NULL, "
                       "FOREIGN KEY (WebsiteId) REFERENCES Website(Id))")

        cursor.execute("CREATE  TABLE  IF NOT EXISTS HtmlIdentifier(Id INTEGER PRIMARY KEY, tag TEXT NOT NULL, "
                       "class TEXT NOT NULL, type INTEGER NOT NULL, WebsiteId INTEGER NOT NULL, "
                       "innerIdentifierId INTEGER, isTopIdentifier BOOLEAN,"
                       "FOREIGN KEY (WebsiteId) REFERENCES Website(Id))")



    def websiteExists(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Id FROM Website WHERE name = ?", (name,))
        r = cursor.fetchone()
        if r is None:
            return False
        return True



    def legalTextExists(self, title, websiteName):
        cursor = self.connection.cursor()
        cursor.execute("SELECT lt.Id FROM LegalText as lt INNER JOIN Website AS w ON lt.WebsiteId = w.Id "
                       "WHERE lt.title = ? AND w.name = ?", (title,websiteName))
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

        for identifier in website.identifiers:
            self._addInnerIdentifier(websiteId, identifier, isTopIdentifier=True)

        return True


    def _addInnerIdentifier(self, websiteId, identifier, isTopIdentifier):
        cursor = self.connection.cursor()

        if identifier.innerIdentifier is None:
            cursor.execute("INSERT INTO HtmlIdentifier(tag, class, type, WebsiteId, innerIdentifierId, isTopIdentifier) "
                           "VALUES (?,?,?,?,?,?)",
                           (identifier.tag, identifier.class_, identifier.type_.value, websiteId, None, isTopIdentifier))
            r = cursor.execute("SELECT last_insert_rowid()").fetchone()
            identifierId = int(r[0])
            return identifierId
        else:
            cursor.execute("INSERT INTO HtmlIdentifier(tag, class, type, WebsiteId, innerIdentifierId, isTopIdentifier) "
                           "VALUES (?,?,?,?,?,?)",
                           (identifier.tag, identifier.class_, identifier.type_.value, websiteId,
                            self._addInnerIdentifier(websiteId, identifier.innerIdentifier, isTopIdentifier=False),
                            isTopIdentifier))


    def addLegalText(self, legalText, website):
        #TODO: umbauen, so dass mehrere Texte gleichzeitig eingefügt werden können
        if self.legalTextExists(legalText.title, website.name):
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

        cursor.execute("SELECT tag, class, type, innerIdentifierId, isTopIdentifier FROM HtmlIdentifier "
                       "WHERE WebsiteId = ? AND isTopIdentifier = 1", (r1[0],))
        r2 = cursor.fetchall()
        identifiers = []
        for r in r2:
            identifier = HtmlIdentifier(r[0], r[1], IdentifierType(r[2]))
            self._appendInnerIdentifier(identifier, innerIdentifierId=r[3])
            identifiers.append(identifier)

        website = Website(r1[1], r1[2], r1[3], r1[4], identifiers)

        return website


    def _appendInnerIdentifier(self, identifier, innerIdentifierId):
        if innerIdentifierId is None:
            return

        cursor = self.connection.cursor()

        cursor.execute("SELECT tag, class, type, innerIdentifierId FROM HtmlIdentifier WHERE Id = ?", (innerIdentifierId,))
        r=cursor.fetchone()

        nextInnerIdentifierId = r[3]
        innerIdentifier = HtmlIdentifier(r[0], r[1], IdentifierType(r[2]))
        identifier.InnerIdentifier = innerIdentifier
        if innerIdentifierId is None:
            return
        else:
            self._appendInnerIdentifier(innerIdentifier,nextInnerIdentifierId)


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


    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()



