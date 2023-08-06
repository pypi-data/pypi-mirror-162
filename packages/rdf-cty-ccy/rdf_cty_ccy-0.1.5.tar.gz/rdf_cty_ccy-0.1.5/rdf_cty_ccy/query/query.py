from typing import List, Optional

from rdflib import Literal, URIRef, XSD
import rdflib.plugins.sparql.processor

from rdf_cty_ccy.graph import graph_query
from rdf_cty_ccy.common import fn, monad
from rdf_cty_ccy.model import model


class Filter:
    WithCurrency = 'withCurrency'


def by_country_code(code: str, filters: List[Optional[Filter]] = []) -> Optional[model.Country]:
    """
    Takes an ISO3166 Alpha-3 country code and returns a single country/currency result.
    If there are no results, None is returned.  If a code as string was not provided, None is returned.

    :param code: A single ISO3166 3 Alpha country code
    :param filters: An Optional List of filters directing what should be returned; from the Filter enum
    :return: Country object with associated Currency
    """
    if not isinstance(code, str):
        return None
    lit = convert_literal(code)
    if lit.is_left():
        return None
    return build(model.Country(), find_by_code(cty_tag_maximal_query, lit.value), filters)


def by_country_uri(uri: str, filters: List[Optional[Filter]] = []) -> Optional[model.Country]:
    if not isinstance(uri, str):
        return None
    uriref = convert_uri(uri)
    if uriref.is_left():
        return None
    return build(model.Country(country_uri=uriref.value), find_by_uri(cty_uri_maximal_query, uriref.value), filters)


@monad.monadic_try()
def convert_literal(lit):
    return Literal(lit, datatype=XSD.string)


@monad.monadic_try()
def convert_uri(uri):
    return URIRef(uri)


def find_by_code(query_fn, lit_code):
    return [r for r in graph_query.sparql(query_fn(lit_code))]


def find_by_uri(query_fn, uri):
    return [r for r in graph_query.sparql(query_fn(uri))]


def build(country: model.Country,
          result: rdflib.query.ResultRow,
          filters: List[Optional[Filter]]) -> Optional[model.Country]:
    if not result:
        return None

    cty = fn.first(result)

    if not country.country_uri:
        country.country_uri = cty.cty

    country.identifies = cty.cty_identifies
    country.code_type = cty.codeset
    country.label = cty.cty_label

    if Filter.WithCurrency in filters:
        if len(result) == 1:
            ccy = build_ccy(cty)
            country.currency = ccy
            country.currencies = [ccy]
        else:
            country.currencies = list(map(build_ccy, result))
    return country


def build_ccy(result) -> model.Currency:
    return model.Currency(currency_uri=result.ccy_code_uri,
                          identifies=result.ccy_identifies,
                          label=result.ccy_label)


def cty_tag_maximal_query(cty_tag: Literal) -> rdflib.plugins.sparql.processor.SPARQLResult:
    return """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX lcc-lr: <https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/>
    PREFIX lcc-cr: <https://www.omg.org/spec/LCC/Countries/CountryRepresentation/>

    SELECT ?cty ?cty_identifies ?cty_label ?codeset ?ccy_identifies ?ccy_code_uri ?ccy_label
    WHERE {{
      ?cty lcc-lr:hasTag {cty_tag} ;
           rdfs:label ?cty_label ; 
           lcc-lr:isMemberOf ?codeset ;
           lcc-lr:identifies ?cty_identifies .
      ?ccy_identifies lcc-cr:isUsedBy ?cty_identifies .
      ?ccy_code_uri lcc-lr:identifies ?ccy_identifies ;
                   rdfs:label ?ccy_label  
    }}
    """.format(cty_tag=cty_tag.n3())


def cty_uri_maximal_query(cty_uri: URIRef) -> rdflib.plugins.sparql.processor.SPARQLResult:
    return """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX lcc-lr: <https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/>
    PREFIX lcc-cr: <https://www.omg.org/spec/LCC/Countries/CountryRepresentation/>

    SELECT ?cty ?cty_identifies ?codeset ?cty_label ?ccy_identifies ?ccy_code_uri ?ccy_label
    WHERE {{
      {cty_uri} rdfs:label ?cty_label ; 
           lcc-lr:isMemberOf ?codeset ;
           lcc-lr:identifies ?cty_identifies .
      ?ccy_identifies lcc-cr:isUsedBy ?cty_identifies .
      ?ccy_code_uri lcc-lr:identifies ?ccy_identifies ;
                   rdfs:label ?ccy_label  
    }}
    """.format(cty_uri=cty_uri.n3())
