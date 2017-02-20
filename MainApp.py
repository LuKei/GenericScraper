from flask import Flask, render_template, g, flash, request, url_for, redirect
from DatabaseAccess import DatabaseAccess
from Datasource import Datasource, DatasourceType
from HtmlIdentifier import HtmlIdentifier, HtmlAttribute, IdentifierType
import os

app = Flask(__name__)



@app.route("/")
def showMain():
    return render_template("main.html", datasources=getDbAccess().getDatasources())



@app.route("/addDatasource/", methods=["GET", "POST"])
def addDatasource():
    try:
        if request.method == "POST":
            name = request.form.get("name")
            url = request.form.get("url")
            isUsingAjax =  "isUsingAjax" in request.form

            getDbAccess().addDatasource(Datasource(name, url, isUsingAjax=isUsingAjax))
            getDbAccess().commit()

            return redirect(url_for("showMain"))

        return render_template("addDatasource.html")

    except Exception as e:
        getDbAccess().rollback()
        return render_template("addDatasource.html", error="Error")



@app.route("/viewDatabase/")
def viewDatabase():
    return render_template("viewDatabase.html")



@app.route("/datasources/<name>/identifiers/")
def showHtmlIdentfiers(name):
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
def addHtmlIdentifier(name):
    try:
        if request.method == "POST":
            tagName = request.form.get("tagName")
            class_ = request.form.get("class_")
            type_ = IdentifierType[request.form.get("type_")]
            attr1 = HtmlAttribute(request.form.get("attr1Name"), request.form.get("attr1Val"))
            attr2 = HtmlAttribute(request.form.get("attr2Name"), request.form.get("attr2Val"))
            attr3 = HtmlAttribute(request.form.get("attr3Name"), request.form.get("attr3Val"))
            attr4 = HtmlAttribute(request.form.get("attr4Name"), request.form.get("attr4Val"))
            attr5 = HtmlAttribute(request.form.get("attr5Name"), request.form.get("attr5Val"))
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

            getDbAccess().addIdentifierToDatasource(name, htmlIdentifier)
            getDbAccess().commit()

            return redirect(url_for("showMain"))

        return render_template("addIdentifier.html", datasource=getDbAccess().getDatasource(name), types=IdentifierType)

    except Exception as e:
        getDbAccess().rollback()
        return render_template("addIdentifier.html", datasource=getDbAccess().getDatasource(name), types=IdentifierType, error="Error")



def getDbAccess():
    if not hasattr(g, 'dbAccess'):
        g.dbAccess = DatabaseAccess(os.path.expanduser(r"~\Desktop\ScraperDb"))
    return g.dbAccess



@app.teardown_appcontext
def closeDbAccess(error):
    if hasattr(g, 'dbAccess'):
        g.dbAccess.close()



if __name__ == "__main__":
    app.run(debug=True)