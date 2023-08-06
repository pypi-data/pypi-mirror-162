"""TODO doc"""

import sys
import logging 

from functools import reduce

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.utils import format_email
from ejerico.sdk.utils import SEADATANETNameResolver

from ejerico.sdk.rdf.namespace import EDMO

class OrganizationImpl(object):

    def __init__(self):
        object.__init__(self)
        self.address = None
        self.email = None
        self.lei_code = None
        self.name = None
        self.spatial = None
        self.phone = None
        self.url = None
        self.vcard = None

    def prepare(self):
        logging.debug("[Organization::prepare] entering method")

        #if self.email is not None:
        #    self.email = format_email(self.email)
        #    for e in [self.email, "mailto:{}".format(self.email) if "mailto:" not in self.email else self.email]:
        #        if e not in self.alias: self.alias.append(e)

        is_edmoID =  reduce(lambda x,y: x or "edmo.seadatanet.org" in y, self.alias, False)
        if not is_edmoID and self.name:
            edmoID = SEADATANETNameResolver.instance().get_edmoIDByName(self.name)
            if edmoID is not None:
                logging.warning("[OrganizationImpl] found edmo")
            else:
                uri = self._graph.findURIByName(self.name, entity_type=self.base(), return_score=True)
                if uri is not None:
                    logging.warning("[OrganizationImpl] found <{}>: {}".format(self.name, uri))
                    self.id = uri

            