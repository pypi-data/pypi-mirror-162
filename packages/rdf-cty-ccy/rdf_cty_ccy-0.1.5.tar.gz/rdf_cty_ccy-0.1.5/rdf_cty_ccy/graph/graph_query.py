from typing import List, Tuple, Optional, Union

import rdflib.plugins.sparql.processor
from rdflib import Namespace, Literal, URIRef

from . import graph

GraphTripleComponent = Optional[Union[str, Namespace, Literal, URIRef]]
GraphTripleType = Tuple[Optional[GraphTripleComponent], Optional[GraphTripleComponent], Optional[GraphTripleComponent]]

def query(triple: GraphTripleType) -> List[GraphTripleType]:
    triple = transform_triple(triple)
    return list(map(lambda x: x, g().triples(triple)))

def sparql(sparql_q: str) -> rdflib.plugins.sparql.processor.SPARQLResult:
    return g().query(sparql_q)

#
# Helper Functions
#

def transform_triple(triple: GraphTripleType):
    s, p, o = triple
    return to_query_form(s), to_query_form(p), to_query_form(o)

def to_query_form(component: GraphTripleComponent):
    if not component or isinstance(component, URIRef) or isinstance(component, Literal):
        return component
    if isinstance(component, str):
        return Literal(component)
    return URIRef(component)

def g():
    return graph.graph()