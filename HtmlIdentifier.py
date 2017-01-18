from enum import Enum


class HtmlIdentifier:

    def __init__(self, tag, class_, type=None):
        self.tag = tag
        self.class_ = class_
        if type is None:
            self.type = IdentifierType.NONE
        self.type = type


class IdentifierType(Enum):
    NEXTPAGE = 1
    LISTITEM = 2
    DOWNLOADLINK = 3
    LEGALTEXTTITLE = 4
    LEGALTEXTCONTENT = 5
    NONE = 6
