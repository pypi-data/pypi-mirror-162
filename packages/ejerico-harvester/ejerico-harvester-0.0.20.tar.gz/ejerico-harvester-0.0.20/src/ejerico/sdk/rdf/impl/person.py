"""TODO doc"""

import sys
import logging
import re 

from functools  import reduce 

from rdflib import plugin
from rdflib import Graph, Literal, URIRef
from rdflib import RDF, FOAF, XSD, SDO
from rdflib.store import Store, VALID_STORE

from ejerico.sdk.utils import format_email
from ejerico.sdk.utils import ORCIDResolver

from ejerico.sdk.rdf.namespace import ORCID

class PersonImpl(object):

    def __init__(self):
        object.__init__(self)
        self.address = None
        self.affiliation = None
        self.email = None
        self.familyName = None
        self.givenName = None
        self.name = None
        self.nationality = None
        self.phone = None
        self.qualification = None
        self.url = None
    
    def prepare(self):
        logging.debug("[Person::prepare] entering method")

        for i in range(len(self.alias)):
            match = re.match(RE_NAME_EMAIL_PATTERN, self.alias[i])
            if match:
                self.alias.append(match.group("email"))
                self.alias[i] = match.group("name") if self.name is None else self.name
                self.email = match.group("email") if entity.email is None else entity.email

        if self.email is not None:
            self.email = format_email(self.email)
            for e in [self.email, "mailto:{}".format(self.email) if "mailto:" not in self.email else self.email]:
                if e not in self.alias: self.alias.append(e)
        
        if self.familyName and self.givenName:
            self.name = self.name if self.name is not None else "{} {}".format(self.familyName, self.givenName)
            self.familyName = self.givenName = None

        if self.name is not None:
            self.name = self.name.strip() 
            self.name = None if '' == self.name else self.name 

        is_orcidID =  reduce(lambda x,y: x or "orcid.org" in y, self.alias, False)
        if not is_orcidID and self.name:
            orcidID = ORCIDResolver.instance().resolve(self.email) if self.email is not None else None
            orcidID = orcidID or ORCIDResolver.instance().resolve(self.name) if self.name is not None else None
            orcidID = orcidID or ORCIDResolver.instance().resolve({"family-name": self.familyName, "given-names": self.givenName}) 
            if orcidID is not None:
                logging.warning("[PersonImpl] found ORCID <{}>: {}".format(self.name, orcidID))
                personID = orcidID.split('/')[-1] if "http" in orcidID else orcidID

                self.alias = [a for a in self.alias if not self.isInternalURI(a)]

                self.id = self.base().buildURI(ORCID, personID)
                self.alias.append(self.base().buildSourceURI(ORCID, personID))
                self.alias.append(orcidID)
                if self.email is not None: self.alias.append("mailto:{}".format(self.email))
                
                self._always_save_me = True
            else:
                uri = self._graph.findURIByName(self.name, entity_type=self.base(), return_score=True)
                if uri is not None:
                    logging.warning("[PersonImpl] found <{}>: {}".format(self.name, uri))
                    self.id = uri

RE_NAME_EMAIL_PATTERN = re.compile("^(?P<name>[áàéèíìóòúùäöü\w\d.-_ ]+){1}([\W])+(<)(?P<email>[\w\d\W]+)+(>)$", re.UNICODE)               