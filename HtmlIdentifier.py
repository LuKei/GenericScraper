from enum import Enum


class HtmlIdentifier:

    def __init__(self, tag, class_=None, type_=None, innerIdentifier=None):
        self.tag = tag
        self.class_ = class_
        self.type_ = type_
        if type_ is None:
            self.type_ = IdentifierType.NONE
        self.innerIdentifier = innerIdentifier
        if not innerIdentifier is None:
            innerIdentifier.type_ = self.type_


    def addInnermostIdentifier(self, identifier):

        identifier.type_ = self.type_

        if self.innerIdentifier is None:
            self.innerIdentifier = identifier
        else:
            self.innerIdentifier.addInnermostIdentifier(identifier)


class IdentifierType(Enum):
    NEXTPAGE = 1
    LISTITEM = 2
    DOWNLOADLINK = 3
    DOCUMENTTITLE = 4
    DOCUMENTSUBTITLE = 5
    LEGALTEXTCONTENT = 6
    DATEIDENTIFIER = 7
    NONE = 99
