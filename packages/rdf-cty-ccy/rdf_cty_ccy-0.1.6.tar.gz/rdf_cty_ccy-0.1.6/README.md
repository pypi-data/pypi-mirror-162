# RDF Country and Currency Graph Library

This library builds an RDF graph of country and currency codes based on the following ontologies:

+ https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/
+ https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/

Both of these graphs are in Turtle format and are used extensively in the [FIBO ontologies](https://github.com/edmcouncil/fibo)

The Library is designed to support querying these triples in 3 modes:

+ Using the Python RDFLib library.  The graph is queried using the RDFLib triples mode.  Returns RDF triples.
+ Using a SPARQL query.  Returns an RDFLib SPARQL result.
+ Via an OO query approach, which returns country and currency objects.

# Building

The TTL files are extracted from the ontology locations (FIBO and OMG) and written to `rdf_cty_ccy/rdfdata`.  To re-get and re-build the ttl files, run the Makefile.

The Country and Currency ontologies are sourced from the following locations:

+ [Currency Codes](https://spec.edmcouncil.org/fibo/ontology/master/2022Q1/FND/Accounting/ISO4217-CurrencyCodes/)
+ [Country Codes](https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/)


```shell
make build_cty_ccy_onto
```


# Usage

## RDFLib Triples Mode

The triples are read into an inmemory RDFLib graph.  Therefore, using the rdflib.triples query format is supported.

The module `rdf_cty_ccy.graph.rdf_prefix` provides shorthand prefixes for the various RDF prefixes using in the ontologies.

```python
fibo_fnd_acc_cur = Namespace('https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/')
fibo_fnd_acc_4217 = Namespace('https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/')
fibo_fnd_utl_av = Namespace("https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/")
lcc_3166_1 = Namespace('https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/')
lcc_cr = Namespace('https://www.omg.org/spec/LCC/Countries/CountryRepresentation/')
lcc_lr = Namespace("https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/")
```

Therefore `rdf_prefix.lcc_3166_1.NZL` is equivalent to the URI `https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL`

The RDFLib triples query produces a list of RDF triples which match the triples provided.  (See the docs at rdflib)[https://rdflib.readthedocs.io/en/stable/intro_to_graphs.html#basic-triple-matching].

```python
from rdf_cty_ccy.graph import graph, graph_query
from rdf_cty_ccy.graph import rdf_prefix as P

result = graph_query.query((None, P.lcc_lr.hasTag, Literal("NZL", datatype=XSD.string)))

s, _, _ = result[0]

s == P.lcc_3166_1.NZL
```


## SPARQL Mode

## Python Objects Mode

The graph can be queried using a python API interface; from the module `rdf_cty_ccy.query.query`.  It returns a `Country` object which has the following properties (note that `URIRef` and `Literal` comes from RDFLib:

+ `country_uri`: URIRef 
+ `identifies`: URIRef
+ `label`: Literal
+ `currency`: Currency:
  + `currency_uri`: URIRef
  + `identifies`: URIRef
  + `label`: Literal
  

```python
from rdf_cty_ccy.query import query as Q

country = Q.by_country_code(code='NZL')

country.country_uri             # => rdflib.term.URIRef('https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL')
str(country.country_uri)        # => 'https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL'
```

Provide the currency filter to obtain the currency properties for the country.

```python
country = Q.by_country_code(code='NZL', filters=[Q.Filter.WithCurrency])

country.currency.currency_uri   # => rdflib.term.URIRef('https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/NZD')

```

You can also query by the country URI (as a string) as follow:

```python
country = Q.by_country_uri(uri='https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL')
```

