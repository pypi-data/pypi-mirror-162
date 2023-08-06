# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rdf_cty_ccy',
 'rdf_cty_ccy.common',
 'rdf_cty_ccy.graph',
 'rdf_cty_ccy.model',
 'rdf_cty_ccy.query',
 'rdf_cty_ccy.rdfdata']

package_data = \
{'': ['*']}

install_requires = \
['PyMonad>=2.4.0,<3.0.0',
 'rdflib>=6.1.1,<7.0.0',
 'requests>=2.28.1,<3.0.0',
 'simple-memory-cache>=1.0.0,<2.0.0']

entry_points = \
{'console_scripts': ['build_onto = rdf_cty_ccy.common.build_onto:builder']}

setup_kwargs = {
    'name': 'rdf-cty-ccy',
    'version': '0.1.6',
    'description': 'Provides the FIBO and OMG Country and Currency Ontology in a queryable form.',
    'long_description': '# RDF Country and Currency Graph Library\n\nThis library builds an RDF graph of country and currency codes based on the following ontologies:\n\n+ https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/\n+ https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/\n\nBoth of these graphs are in Turtle format and are used extensively in the [FIBO ontologies](https://github.com/edmcouncil/fibo)\n\nThe Library is designed to support querying these triples in 3 modes:\n\n+ Using the Python RDFLib library.  The graph is queried using the RDFLib triples mode.  Returns RDF triples.\n+ Using a SPARQL query.  Returns an RDFLib SPARQL result.\n+ Via an OO query approach, which returns country and currency objects.\n\n# Building\n\nThe TTL files are extracted from the ontology locations (FIBO and OMG) and written to `rdf_cty_ccy/rdfdata`.  To re-get and re-build the ttl files, run the Makefile.\n\nThe Country and Currency ontologies are sourced from the following locations:\n\n+ [Currency Codes](https://spec.edmcouncil.org/fibo/ontology/master/2022Q1/FND/Accounting/ISO4217-CurrencyCodes/)\n+ [Country Codes](https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/)\n\n\n```shell\nmake build_cty_ccy_onto\n```\n\n\n# Usage\n\n## RDFLib Triples Mode\n\nThe triples are read into an inmemory RDFLib graph.  Therefore, using the rdflib.triples query format is supported.\n\nThe module `rdf_cty_ccy.graph.rdf_prefix` provides shorthand prefixes for the various RDF prefixes using in the ontologies.\n\n```python\nfibo_fnd_acc_cur = Namespace(\'https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/\')\nfibo_fnd_acc_4217 = Namespace(\'https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/\')\nfibo_fnd_utl_av = Namespace("https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/")\nlcc_3166_1 = Namespace(\'https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/\')\nlcc_cr = Namespace(\'https://www.omg.org/spec/LCC/Countries/CountryRepresentation/\')\nlcc_lr = Namespace("https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/")\n```\n\nTherefore `rdf_prefix.lcc_3166_1.NZL` is equivalent to the URI `https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL`\n\nThe RDFLib triples query produces a list of RDF triples which match the triples provided.  (See the docs at rdflib)[https://rdflib.readthedocs.io/en/stable/intro_to_graphs.html#basic-triple-matching].\n\n```python\nfrom rdf_cty_ccy.graph import graph, graph_query\nfrom rdf_cty_ccy.graph import rdf_prefix as P\n\nresult = graph_query.query((None, P.lcc_lr.hasTag, Literal("NZL", datatype=XSD.string)))\n\ns, _, _ = result[0]\n\ns == P.lcc_3166_1.NZL\n```\n\n\n## SPARQL Mode\n\n## Python Objects Mode\n\nThe graph can be queried using a python API interface; from the module `rdf_cty_ccy.query.query`.  It returns a `Country` object which has the following properties (note that `URIRef` and `Literal` comes from RDFLib:\n\n+ `country_uri`: URIRef \n+ `identifies`: URIRef\n+ `label`: Literal\n+ `currency`: Currency:\n  + `currency_uri`: URIRef\n  + `identifies`: URIRef\n  + `label`: Literal\n  \n\n```python\nfrom rdf_cty_ccy.query import query as Q\n\ncountry = Q.by_country_code(code=\'NZL\')\n\ncountry.country_uri             # => rdflib.term.URIRef(\'https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL\')\nstr(country.country_uri)        # => \'https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL\'\n```\n\nProvide the currency filter to obtain the currency properties for the country.\n\n```python\ncountry = Q.by_country_code(code=\'NZL\', filters=[Q.Filter.WithCurrency])\n\ncountry.currency.currency_uri   # => rdflib.term.URIRef(\'https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/NZD\')\n\n```\n\nYou can also query by the country URI (as a string) as follow:\n\n```python\ncountry = Q.by_country_uri(uri=\'https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/NZL\')\n```\n\n',
    'author': 'Col Perks',
    'author_email': 'wild.fauve@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wildfauve/rdf_cty_ccy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
