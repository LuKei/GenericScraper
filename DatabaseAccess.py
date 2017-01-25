import sqlite3
from Datasource import Datasource
from Document import Document
from HtmlIdentifier import IdentifierType
from HtmlIdentifier import HtmlIdentifier

class DatabaseAccess:

    def __init__(self, filename):
        self.filename = filename
        self.connection = sqlite3.connect(filename + ".db")
        cursor = self.connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS datasources(id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL)")

        cursor.execute("CREATE TABLE IF NOT EXISTS datasources_type(id INTEGER PRIMARY KEY, name TEXT NOT NULL)")

        cursor.execute("CREATE TABLE IF NOT EXISTS dokumente(id INTEGER PRIMARY KEY, datasource INTEGER NOT NULL, "
                       "datasources_type INTEGER, url TEXT NOT NULL, title TEXT NOT NULL, date DATETIME NOT NULL,"
                       "filepath TEXT NOT NULL, FOREIGN KEY (datasource) REFERENCES datasources(id),"
                       "FOREIGN KEY (datasources_type) REFERENCES datasources_type(id))")

        cursor.execute("CREATE  TABLE  IF NOT EXISTS html_identifier(id INTEGER PRIMARY KEY, tag TEXT NOT NULL, "
                       "class TEXT NOT NULL, type INTEGER NOT NULL, datasource INTEGER NOT NULL, "
                       "innerIdentifier INTEGER, isTopIdentifier BOOLEAN,"
                       "FOREIGN KEY (datasource) REFERENCES datasources(id))")



    def datasourceExists(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM datasources WHERE name = ?", (name,))
        r = cursor.fetchone()
        if r is None:
            return False
        return True



    def documentExists(self, title, datsourceName):
        cursor = self.connection.cursor()
        cursor.execute("SELECT doc.id FROM dokumente AS doc INNER JOIN datasources AS ds ON doc.datasource = ds.id "
                       "WHERE doc.title = ? AND ds.name = ?", (title,datsourceName))
        r = cursor.fetchone()
        if r is None:
            return False
        return True


    def documentTitlesInDb(self, datasource):
        cursor = self.connection.cursor()
        cursor.execute("SELECT title FROM dokumente AS doc INNER JOIN datasources AS ds ON doc.datasource = ds.id "
                       "WHERE ds.name = ?", (datasource.name,))
        return cursor.fetchall()



    def addDatasource(self, datasource):
        if self.datasourceExists(datasource.name):
           print("Es existiert bereits eine Webseite mit diesem Namen.")
           return False

        cursor = self.connection.cursor()

        dattasourceToInsert = (None, datasource.name, datasource.url)
        cursor.execute("INSERT INTO datasources VALUES(?,?,?)", dattasourceToInsert)

        r = cursor.execute("SELECT id FROM datasources AS ds WHERE ds.name = ?", (datasource.name,)).fetchone()
        datasourceId = int(r[0])

        for identifier in datasource.identifiers:
            self._addInnerIdentifier(datasourceId, identifier, isTopIdentifier=True)

        return True


    def _addInnerIdentifier(self, datasourceId, identifier, isTopIdentifier):
        cursor = self.connection.cursor()

        if identifier.innerIdentifier is None:
            cursor.execute("INSERT INTO html_identifier(tag, class, type, datasource, innerIdentifier, isTopIdentifier) "
                           "VALUES (?,?,?,?,?,?)",
                           (identifier.tag, identifier.class_, identifier.type_.value, datasourceId, None, isTopIdentifier))
            r = cursor.execute("SELECT last_insert_rowid()").fetchone()
            identifierId = int(r[0])
            return identifierId
        else:
            cursor.execute("INSERT INTO html_identifier(tag, class, type, datasource, innerIdentifier, isTopIdentifier) "
                           "VALUES (?,?,?,?,?,?)",
                           (identifier.tag, identifier.class_, identifier.type_.value, datasourceId,
                            self._addInnerIdentifier(datasourceId, identifier.innerIdentifier, isTopIdentifier=False),
                            isTopIdentifier))


    def addDocument(self, document, datasource):
        #TODO: umbauen, sodass mehrere Texte gleichzeitig eingefügt werden können
        if self.documentExists(document.title, datasource.name):
            print("Ein Gesetzestext mit dem Titel " + document.title + " existert bereits.")
            return False

        cursor = self.connection.cursor()
        r = cursor.execute("SELECT id FROM datasources AS ds WHERE ds.name = ?", (datasource.name,)).fetchone()
        if r is None:
            print("Eine Webseite mit diesem Namen existiert nicht. Fügen Sie den Gesetzestext einer exsitierenden "
                  "Webseite hinzu")
            return False

        datasourceId = int(r[0])

        tupleToInsert = (None, datasourceId, document.datasourceType.value, document.url, document.title, document.date, document.filepath, )
        cursor.execute("INSERT INTO dokumente VALUES(?,?,?,?,?,?,?)", tupleToInsert)
        return True


    def getDatasource(self, name):
        if not self.datasourceExists(name):
            print("Keine Webseite mit diesem Namen gefunden.")
            return None

        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, url FROM datasources WHERE name = ?", (name,))
        r1 = cursor.fetchone()

        cursor.execute("SELECT tag, class, type, innerIdentifier, isTopIdentifier FROM html_identifier "
                       "WHERE datasource = ? AND isTopIdentifier = 1", (r1[0],))
        r2 = cursor.fetchall()
        identifiers = []
        for r in r2:
            identifier = HtmlIdentifier(r[0], r[1], IdentifierType(r[2]))
            self._appendInnerIdentifier(identifier, innerIdentifierId=r[3])
            identifiers.append(identifier)

        datasource = Datasource(r1[1], r1[2], identifiers)

        return datasource


    def _appendInnerIdentifier(self, identifier, innerIdentifierId):
        if innerIdentifierId is None:
            return

        cursor = self.connection.cursor()

        cursor.execute("SELECT tag, class, type, innerIdentifier FROM html_identifier WHERE id = ?", (innerIdentifierId,))
        r=cursor.fetchone()

        nextInnerIdentifierId = r[3]
        innerIdentifier = HtmlIdentifier(r[0], r[1], IdentifierType(r[2]))
        identifier.InnerIdentifier = innerIdentifier
        if innerIdentifierId is None:
            return
        else:
            self._appendInnerIdentifier(innerIdentifier,nextInnerIdentifierId)


    def getDocuments(self, datasource):
        texts = []

        cursor = self.connection.cursor()
        cursor.execute("SELECT doc.title, doc.filepath, doc.datasources_type, doc.url, doc.date "
                       "FROM dokumente AS doc INNER JOIN datasources AS ds ON doc.datasource = ds.id "
                       "WHERE ds.name = ?", (datasource.name,))
        rows = cursor.fetchall()

        for r in rows:
            text = Document(r[0], r[1], datasource, r[2], r[3], r[4])
            texts.append(text)

        return texts


    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()



