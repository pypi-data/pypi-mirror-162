"""TODO doc"""

import sys 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

class WebPageImpl(object):

    def __init__(self):
        object.__init__(self)
        self.abstract = None
        self.created = None
        self.creator = None
        self.contributor = None
        self.description = None
        self.keywords = None
        self.is_part_of = None
        self.language = None
        self.license = None
        self.mimetype = None
        self.owner = None
        self.published = None
        self.publisher = None
        self.project = None
        self.spatial = None
        self.temporal = None
        self.title = None
        self.url = None

