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


class IdentifierType(Enum):
    NEXTPAGE = 1
    LISTITEM = 2
    DOWNLOADLINK = 3
    LEGALTEXTTITLE = 4
    LEGALTEXTCONTENT = 5
    NONE = 6
