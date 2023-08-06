
"""TODO doc"""

import os
import sys
import re
import hashlib

import logging

from functools import partial 

from ejerico.sdk.annotations import singleton

__all__ = []

def _most_silly_method(self, default):
    return default()

def _most_silly_function(default):
    return default
    
class Namespace(str):

    def __init__(self, namespace):
        self._namespace = namespace.lower()

    def qname(self, name):
        value = None
        if name is not None: 
            value = "{}:{}".format(self._namespace, str(name)) 
        return value

    def __getattr__(self, name):
        if name.startswith("_"): 
            raise AttributeError
        else:
            return self.qname(name)

    def __repr__(self):
        return self._namespace


@singleton
class NamespaceManager():
    def registerNamespace(self, namespace): 
        if isinstance(namespace, Namespace):
            my_module = sys.modules[__name__]
            name = str(namespace).replace('-', '_').upper()
            my_module.__all__.append(name)
            setattr(my_module, name, namespace)
        else:
            logging.warning("[NamespaceManager::registerNamespace] namespace must be an instance of Namespace")

    def getNamespace(self, name):
        name = str(name).replace('-', '_').upper()
        my_module = sys.modules[__name__]
        if name in my_module.__all__:
            return getattr(my_module, name)
        else:
            return None
            

#########################################################################################
## built-in namespaces
#########################################################################################

NamespaceManager.instance().registerNamespace(Namespace("ejerico"))
NamespaceManager.instance().registerNamespace(Namespace("socib"))
NamespaceManager.instance().registerNamespace(Namespace("epos"))

NamespaceManager.instance().registerNamespace(Namespace("edmo"))
NamespaceManager.instance().registerNamespace(Namespace("edmerp"))
NamespaceManager.instance().registerNamespace(Namespace("edmed"))
NamespaceManager.instance().registerNamespace(Namespace("edios"))

NamespaceManager.instance().registerNamespace(Namespace("orcid"))
NamespaceManager.instance().registerNamespace(Namespace("researchgate"))

NamespaceManager.instance().registerNamespace(Namespace("wmo"))
NamespaceManager.instance().registerNamespace(Namespace("coriolis"))
NamespaceManager.instance().registerNamespace(Namespace("ices"))

NamespaceManager.instance().registerNamespace(Namespace("doi"))

NamespaceManager.instance().registerNamespace(Namespace("emodnet-physics"))
NamespaceManager.instance().registerNamespace(Namespace("emodnet-biology"))

NamespaceManager.instance().registerNamespace(Namespace("cmems"))
NamespaceManager.instance().registerNamespace(Namespace("ifremer"))
NamespaceManager.instance().registerNamespace(Namespace("seadatanet"))

NamespaceManager.instance().registerNamespace(Namespace("obps"))
NamespaceManager.instance().registerNamespace(Namespace("oceandocs"))

NamespaceManager.instance().registerNamespace(Namespace("github"))
NamespaceManager.instance().registerNamespace(Namespace("ramadda"))
