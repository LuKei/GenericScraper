import sqlite3
import os
from Datasource import Datasource
from Document import Document
from HtmlIdentifier import HtmlIdentifier, IdentifierType, HtmlAttribute
import threading

class DatabaseAccess:

    defaultDbPath = os.path.expanduser("~\Desktop\\")
    lock = threading.Lock()

    def __init__(self, filePath=defaultDbPath, filename="ScraperDb"):
        self.filePath = filePath
        self.filename = filename
        self.connection = sqlite3.connect(filePath + filename + ".db",check_same_thread=False)
        cursor = self.connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS datasource(id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL,"
                       "is_using_ajax BOOLEAN NOT NULL)")

        cursor.execute("CREATE TABLE IF NOT EXISTS datasources_type(id INTEGER PRIMARY KEY, name TEXT NOT NULL)")

        cursor.execute("CREATE TABLE IF NOT EXISTS document(id INTEGER PRIMARY KEY, datasource INTEGER NOT NULL, "
                       "datasources_type INTEGER, url TEXT NOT NULL, title TEXT NOT NULL, date DATETIME,"
                       "filepath TEXT, FOREIGN KEY (datasource) REFERENCES datasource(id),"
                       "FOREIGN KEY (datasources_type) REFERENCES datasources_type(id))")

        cursor.execute("CREATE  TABLE  IF NOT EXISTS html_identifier(id INTEGER PRIMARY KEY, tag_name TEXT NOT NULL, "
                       "class TEXT, type INTEGER NOT NULL, datasource INTEGER NOT NULL, "
                       "innerIdentifier INTEGER, isTopIdentifier BOOLEAN NOT NULL,"
                       "FOREIGN KEY (datasource) REFERENCES datasource(id))")

        cursor.execute("CREATE TABLE IF NOT EXISTS html_attribute(id INTEGER PRIMARY KEY, name TEXT NOT NULL, value TEXT NOT NULL,"
                       "exact_match BOOLEAN NOT NULL, html_identifier INTEGER NOT NULL, "
                       "FOREIGN KEY (html_identifier) REFERENCES html_identifier(id))")



    def datasourceExists(self, datasourceName):
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM datasource WHERE name = ?", (datasourceName,))
            r = cursor.fetchone()
            if r is None:
                return False
            return True



    def documentExists(self, title, datasourceName):
            cursor = self.connection.cursor()
            cursor.execute("SELECT doc.id FROM document AS doc INNER JOIN datasource AS ds ON doc.datasource = ds.id "
                           "WHERE doc.title = ? AND ds.name = ?", (title,datasourceName))
            r = cursor.fetchone()
            if r is None:
                return False
            return True



    def addDatasource(self, datasource):
            if self.datasourceExists(datasource.name):
               print("Es existiert bereits eine Webseite mit diesem Namen.")
               return False

            cursor = self.connection.cursor()

            dattasourceToInsert = (None, datasource.name, datasource.url, datasource.isUsingAjax)
            cursor.execute("INSERT INTO datasource VALUES(?,?,?,?)", dattasourceToInsert)

            r = cursor.execute("SELECT id FROM datasource AS ds WHERE ds.name = ?", (datasource.name,)).fetchone()
            datasourceId = int(r[0])

            if datasource.identifiers is not None:
                for identifier in datasource.identifiers:
                    self._addIdentifierRec(datasourceId, identifier, isTopIdentifier=True)

            return True



    def addIdentifierToDatasource(self, datasourceName, htmlIdentifier):
            if not self.datasourceExists(datasourceName):
                print("Eine Datasource mit diesem Namen existiert nicht")
                return False

            cursor = self.connection.cursor()

            r = cursor.execute("SELECT id FROM datasource WHERE name = ?", (datasourceName,)).fetchone()
            datasourceId = r[0]

            r = cursor.execute("SELECT id FROM html_identifier WHERE datasource = ? AND type= ?",
                               (datasourceId, htmlIdentifier.type_.value)).fetchall()
            hasIdentifier = len(r) > 0

            self._addInnermostIdentifier(datasourceId, htmlIdentifier, isTopIdentifier=not hasIdentifier)



    def _addIdentifierRec(self, datasourceId, identifier, isTopIdentifier):
            cursor = self.connection.cursor()

            if identifier.innerIdentifier is None:
                cursor.execute("INSERT INTO html_identifier(tag_name, class, type, datasource, innerIdentifier, isTopIdentifier) "
                               "VALUES (?,?,?,?,?,?)",
                               (identifier.tagName, identifier.class_, identifier.type_.value, datasourceId, None, isTopIdentifier))
                r = cursor.execute("SELECT last_insert_rowid()").fetchone()
                identifierId = int(r[0])

                self._addHtmlAttributes(identifier.additionalAttributes, identifierId)

                return identifierId
            else:
                cursor.execute("INSERT INTO html_identifier(tag_name, class, type, datasource, innerIdentifier, isTopIdentifier) "
                               "VALUES (?,?,?,?,?,?)",
                               (identifier.tagName, identifier.class_, identifier.type_.value, datasourceId,
                                self._addIdentifierRec(datasourceId, identifier.innerIdentifier, isTopIdentifier=False),
                                isTopIdentifier))

                r = cursor.execute("SELECT last_insert_rowid()").fetchone()
                identifierId = int(r[0])

                self._addHtmlAttributes(identifier.additionalAttributes, identifierId)

                return identifierId



    def _addInnermostIdentifier(self, datasourceId, identifier, isTopIdentifier):
            cursor = self.connection.cursor()

            cursor.execute("INSERT INTO html_identifier(tag_name, class, type, datasource, innerIdentifier, isTopIdentifier) "
                           "VALUES (?,?,?,?,?,?)",
                           (identifier.tagName, identifier.class_, identifier.type_.value, datasourceId, None, isTopIdentifier))
            newInnermostIdentifierId = int(cursor.execute("SELECT last_insert_rowid()").fetchone()[0])

            self._addHtmlAttributes(identifier.additionalAttributes, newInnermostIdentifierId)

            if not isTopIdentifier:
                #Verlinkung des alten innersten identifier auf den neuen innersten identifier
                cursor.execute("SELECT id FROM html_identifier WHERE datasource = ? AND isTopIdentifier = ? AND type = ?",
                               (datasourceId, True, identifier.type_.value))
                oldInnermostIdentifierId = cursor.fetchone()[0]
                while True:
                    cursor.execute("SELECT innerIdentifier FROM html_identifier WHERE id = ?", (oldInnermostIdentifierId,))
                    r = cursor.fetchone()
                    if r[0] is not None:
                        oldInnermostIdentifierId = r[0]
                    else:
                        break

                cursor.execute("UPDATE html_identifier SET innerIdentifier = ? WHERE id = ?",
                               (newInnermostIdentifierId, oldInnermostIdentifierId))



    def _addHtmlAttributes(self, attributes, identifierId):
            cursor = self.connection.cursor()

            if attributes is not None:
                for attribute in attributes:
                    cursor.execute("INSERT INTO html_attribute(name, value, exact_match, html_identifier) VALUES (?,?,?,?)",
                                   (attribute.name, attribute.value, attribute.exactmatch, identifierId))



    def addDocument(self, document, datasource):
            if self.documentExists(document.title, datasource.name):
                print("Ein Gesetzestext mit dem Titel " + document.title + " existert bereits.")
                return -1

            cursor = self.connection.cursor()
            r = cursor.execute("SELECT id FROM datasource AS ds WHERE ds.name = ?", (datasource.name,)).fetchone()
            if r is None:
                print("Eine Webseite mit diesem Namen existiert nicht. Fügen Sie den Gesetzestext einer exsitierenden "
                      "Webseite hinzu")
                return -1

            datasourceId = int(r[0])

            tupleToInsert = (None, datasourceId, document.datasourceType.value, document.url, document.title, document.date, document.filepath)
            cursor.execute("INSERT INTO document VALUES(?,?,?,?,?,?,?)", tupleToInsert)
            r = cursor.execute("SELECT last_insert_rowid()").fetchone()
            documentId = int(r[0])
            return documentId


    def setDocumentFilePath(self, documentId, filePath):
            cursor = self.connection.cursor()
            cursor.execute("UPDATE document SET filepath = ? WHERE id = ?", (filePath, documentId))


    def getDatasource(self, datasourceName):
            if not self.datasourceExists(datasourceName):
                print("Keine Webseite mit diesem Namen gefunden.")
                return None

            cursor = self.connection.cursor()
            cursor.execute("SELECT id, name, url, is_using_ajax FROM datasource WHERE name = ?", (datasourceName,))
            datasourceRow = cursor.fetchone()

            cursor.execute("SELECT id, tag_name, class, type, innerIdentifier, isTopIdentifier FROM html_identifier "
                           "WHERE datasource = ? AND isTopIdentifier = 1", (datasourceRow[0],))
            identifierRows = cursor.fetchall()
            identifiers = []
            for identifierRow in identifierRows:
                identifier = HtmlIdentifier(identifierRow[1], identifierRow[2], IdentifierType(identifierRow[3]))
                identifier.additionalAttributes = self._getHtmlAttributes(identifierId=identifierRow[0])
                self._appendIdentifierRec(identifier, innerIdentifierId=identifierRow[4])
                identifiers.append(identifier)

            datasource = Datasource(datasourceRow[1], datasourceRow[2], identifiers, datasourceRow[3])

            return datasource

    def getDatasources(self):
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM datasource")
            nameRows = cursor.fetchall()

            if len(nameRows) > 0:
                datasources = []
                for row in nameRows:
                    datasources.append(self.getDatasource(row[0]))

                return datasources

            return []



    def _appendIdentifierRec(self, identifier, innerIdentifierId):
            if innerIdentifierId is None:
                return

            cursor = self.connection.cursor()

            cursor.execute("SELECT tag_name, class, type, innerIdentifier FROM html_identifier WHERE id = ?", (innerIdentifierId,))
            r=cursor.fetchone()

            nextInnerIdentifierId = r[3]
            innerIdentifier = HtmlIdentifier(r[0], r[1], IdentifierType(r[2]))
            innerIdentifier.additionalAttributes = self._getHtmlAttributes(identifierId=innerIdentifierId)
            identifier.innerIdentifier = innerIdentifier
            if innerIdentifierId is None:
                return
            else:
                self._appendIdentifierRec(innerIdentifier, nextInnerIdentifierId)


    def _getHtmlAttributes(self, identifierId):
            cursor = self.connection.cursor()

            attributes = []

            cursor.execute("SELECT name, value, exact_match FROM html_attribute WHERE html_identifier = ?", (identifierId,))
            attributeRows = cursor.fetchall()

            for attributeRow in attributeRows:
                attributes.append(HtmlAttribute(attributeRow[0], attributeRow[1], attributeRow[2]))

            return attributes

    def getDocument(self, title, datasource):
            if not self.documentExists(title, datasource.name):
                return None

            cursor = self.connection.cursor()
            cursor.execute("SELECT doc.title, doc.filepath, doc.datasources_type, doc.url, doc.date "
                           "FROM document AS doc INNER JOIN datasource AS ds ON doc.datasource = ds.id "
                           "WHERE doc.title = ? AND ds.name = ?", (title, datasource.name))
            r = cursor.fetchone()
            return Document(r[0], r[1], datasource, r[2], r[3], r[4])


    def getDocuments(self, datasource):
            texts = []

            cursor = self.connection.cursor()
            cursor.execute("SELECT doc.title, doc.filepath, doc.datasources_type, doc.url, doc.date "
                           "FROM document AS doc INNER JOIN datasource AS ds ON doc.datasource = ds.id "
                           "WHERE ds.name = ?", (datasource.name,))
            rows = cursor.fetchall()

            for r in rows:
                text = Document(r[0], r[1], datasource, r[2], r[3], r[4])
                texts.append(text)

            return texts

    def removeIdentifiers(self, datasourceName, type):
        cursor = self.connection.cursor()

        cursor.execute("SELECT id FROM html_identifier WHERE datasource = (SELECT id FROM datasource WHERE name = ?)"
                       "AND type=?", [datasourceName, type])
        idRows = cursor.fetchall()

        questionmarks = "?" * len(idRows)
        deleteIdentifiersQuery = "DELETE FROM html_identifier WHERE id IN ({})".format(",".join(questionmarks))
        deleteAttributesQuery = "DELETE FROM html_attribute WHERE html_identifier IN ({})".format(",".join(questionmarks))

        idsTuple = ()
        for row in idRows:
            idsTuple += row

        cursor.execute(deleteIdentifiersQuery, idsTuple)
        cursor.execute(deleteAttributesQuery, idsTuple)


    def removeDocument(self, title, datasource):
            if not self.documentExists(title, datasource.name):
                return

            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM document WHERE title = ? AND "
                           "datasource = (SELECT id FROM datasource WHERE name = ?)", (title, datasource.name))


    def commit(self):
            self.connection.commit()

    def rollback(self):
            self.connection.rollback()

    def close(self):
            self.connection.close()



