from enum import Enum


class HtmlIdentifier:

    def __init__(self, tagName, class_=None, type_=None, additionalAttributes=None):
        self.tagName = tagName
        self.class_ = class_
        if class_ == "":
            self.class_ = None
        self.type_ = type_
        if type_ is None:
            self.type_ = IdentifierType.NONE
        self.additionalAttributes = additionalAttributes
        self.innerIdentifier = None


    def addInnermostIdentifier(self, identifier):

        identifier.type_ = self.type_

        if self.innerIdentifier is None:
            self.innerIdentifier = identifier
        else:
            self.innerIdentifier.addInnermostIdentifier(identifier)



class HtmlAttribute:

    def __init__(self, name, value, exactmatch = True):
        self.name = name
        self.value = value
        self.exactmatch = exactmatch


class IdentifierType(Enum):
    NEXTPAGE = 1
    LISTITEM = 2
    DOWNLOADLINK = 3
    DOCUMENTTITLE = 4
    DOCUMENTSUBTITLE = 5
    LEGALTEXTCONTENT = 6
    DATEIDENTIFIER = 7
    AJAXWAIT = 8
    NONE = 99
