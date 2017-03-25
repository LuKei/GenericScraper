from flask import Flask, render_template, g, flash, request, url_for, redirect
from DatabaseAccess import DatabaseAccess
from Datasource import Datasource, DatasourceType
from HtmlIdentifier import HtmlIdentifier, HtmlAttribute, IdentifierType
from Scraper import Scraper

app = Flask(__name__)
latestType = IdentifierType.NEXTPAGE.value
datasourcesBeingScraped = []

@app.route("/")
def showMain():
    with DatabaseAccess.lock:
        datasources = getDbAccess().getDatasources()
        return render_template("main.html", datasources=datasources, datasourcesBeingScraped=datasourcesBeingScraped,
                               datsourceTypes=DatasourceType)



@app.route("/datasources/<name>/scrape/")
@app.route("/datasources/<name>/scrape/<datasourceType>")
def scrapeDatasource(name, datasourceType=DatasourceType.UNKNOWN):
    with DatabaseAccess.lock:
        datasource = getDbAccess().getDatasource(datasourceName=name)

    if name in datasourcesBeingScraped:
        Scraper.stopScrapingDatasource(datasource)
        datasourcesBeingScraped.remove(name)
    else:
        datasourceType = DatasourceType[datasourceType]
        Scraper.startScrapingDatasource(datasource, datasourceType)
        datasourcesBeingScraped.append(name)

    return redirect(url_for("showMain"))



@app.route("/addDatasource/", methods=["GET", "POST"])
def addDatasource():
    try:
        if request.method == "POST":
            name = request.form.get("name")
            url = request.form.get("url")
            isUsingAjax =  "isUsingAjax" in request.form

            with DatabaseAccess.lock:
                getDbAccess().addDatasource(Datasource(name, url, isUsingAjax=isUsingAjax))
                getDbAccess().commit()

            return redirect(url_for("showMain"))

        return render_template("addDatasource.html")

    except Exception as e:
        with DatabaseAccess.lock:
            getDbAccess().rollback()
        return render_template("addDatasource.html", error="Error")



@app.route("/viewDatabase/")
def viewDatabase():
    return render_template("viewDatabase.html")



@app.route("/datasources/<name>/identifiers/")
def showHtmlIdentfiers(name):
    with DatabaseAccess.lock:
        datasource = getDbAccess().getDatasource(name)

    identifiersDict = {}
    for type in IdentifierType:
        identifiers = []
        identifier = datasource.getOutermostIdentifier(type)
        while identifier is not None:
            identifiers.append(identifier)
            identifier = identifier.innerIdentifier
        identifiersDict[type] = identifiers

    return render_template("htmlIdentifiers.html", datasource=datasource, types=IdentifierType, identifiersDict=identifiersDict)

@app.route("/datasources/<name>/addIdentifier/", methods=["GET", "POST"])
@app.route("/datasources/<name>/addIdentifier/<int:defaultType>", methods=["GET", "POST"])
def addHtmlIdentifier(name, defaultType=-1):
    global latestType
    try:
        if request.method == "POST":
            tagName = request.form.get("tagName")
            class_ = request.form.get("class_")
            type_ = IdentifierType[request.form.get("type_")]
            attr1 = HtmlAttribute(request.form.get("attr1Name"), request.form.get("attr1Val"), "attr1exactMatch" in request.form)
            attr2 = HtmlAttribute(request.form.get("attr2Name"), request.form.get("attr2Val"), "attr2exactMatch" in request.form)
            attr3 = HtmlAttribute(request.form.get("attr3Name"), request.form.get("attr3Val"), "attr3exactMatch" in request.form)
            attr4 = HtmlAttribute(request.form.get("attr4Name"), request.form.get("attr4Val"), "attr4exactMatch" in request.form)
            attr5 = HtmlAttribute(request.form.get("attr5Name"), request.form.get("attr5Val"), "attr5exactMatch" in request.form)
            attrs = []
            if attr1.name != "":
                attrs.append(attr1)
            if attr2.name != "":
                attrs.append(attr2)
            if attr3.name != "":
                attrs.append(attr3)
            if attr4.name != "":
                attrs.append(attr4)
            if attr5.name != "":
                attrs.append(attr5)

            htmlIdentifier = HtmlIdentifier(tagName, class_, type_, attrs)

            with DatabaseAccess.lock:
                getDbAccess().addIdentifierToDatasource(name, htmlIdentifier)
                getDbAccess().commit()

            latestType = type_.value
            return redirect(url_for("showMain"))

        if defaultType == -1:
            defaultType = latestType
        with DatabaseAccess.lock:
            return render_template("addIdentifier.html", datasource=getDbAccess().getDatasource(name), types=IdentifierType, defaultType=defaultType)

    except Exception as e:
        with DatabaseAccess.lock:
            getDbAccess().rollback()
            return render_template("addIdentifier.html", datasource=getDbAccess().getDatasource(name), types=IdentifierType, error="Error")



@app.route("/datasources/<name>/removeIdentifiers/<int:type>", methods=["GET"])
def removeHtmlIdentifiers(name, type):
    with DatabaseAccess.lock:
        getDbAccess().removeIdentifiers(name, type)
        getDbAccess().commit()
    return redirect(url_for("showMain"))


def getDbAccess():
    if not hasattr(g, "dbAccess"):
        g.dbAccess = DatabaseAccess()
    return g.dbAccess


@app.teardown_appcontext
def closeDbAccess(error):
    if hasattr(g, 'dbAccess'):
        g.dbAccess.close()



if __name__ == "__main__":
    app.run(debug=True)