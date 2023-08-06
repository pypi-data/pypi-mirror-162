"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.rdf.namespace import EJERICO

class IdentifierImpl(object):

    def __init__(self):
        self.system = None
        self.code = None

    def toString(self):
        return "{}:{}".format(self.system if self.system is not None else EJERICO, self.code)
    
    def fromString(string):
        p = string.split(':')
        if len(p) > 1:
            self.system = p[0]
            self.code = ''.join(p[1:])
        else:
            self.system = "unknnown"
            self.code = string

    @classmethod
    def createFromString(cls, string):
        my_self = cls()
        p = string.split(':')
        if len(p) > 1:
            my_self.system = p[0]
            my_self.code = ''.join(p[1:])
        else:
            my_self.system = "unknnown"
            my_self.code = string