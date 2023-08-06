from typing import List
from dataclasses import dataclass, field
from rdflib import URIRef, Literal

@dataclass
class Currency:
    """
    <https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/NZD>
      a owl:NamedIndividual, fibo-fnd-acc-cur:CurrencyIdentifier ;
      rdfs:label "NZD" ;
      skos:definition "the currency identifier for New Zealand Dollar"@en ;
      lcc-lr:denotes <https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/NewZealandDollar> ;
      lcc-lr:hasTag "NZD" ;
      lcc-lr:identifies <https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/NewZealandDollar> ;
      lcc-lr:isMemberOf <https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/ISO4217-CodeSet> .
    """
    currency_uri: URIRef
    identifies: URIRef
    label: Literal


@dataclass
class Country:
    """
    <https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL>
      a owl:NamedIndividual, lcc-cr:Alpha3Code ;
      skos:definition "Alpha-3 country code for New Zealand" ;
      rdfs:label "NZL" ;
      lcc-lr:hasTag "NZL"^^xsd:string ;
      lcc-lr:denotes <https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NewZealand> ;
      lcc-lr:identifies <https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NewZealand> ;
      lcc-lr:isMemberOf <https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/ISO3166-1-Alpha3-CodeSet> ;
      rdfs:isDefinedBy <https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/> .
    """
    country_uri: URIRef = None
    identifies: URIRef = None
    label: Literal = None
    code_type: URIRef = None
    currency: Currency = None
    currencies: List[Currency] = field(default_factory=list)

    def has_single_currency(self):
        return len(self.currencies) == 1
