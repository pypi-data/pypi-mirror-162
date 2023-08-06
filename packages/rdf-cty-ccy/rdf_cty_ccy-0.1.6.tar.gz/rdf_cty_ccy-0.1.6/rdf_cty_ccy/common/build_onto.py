import argparse
import requests
import os
import pickle

from rdf_cty_ccy.graph import graph

ccy_url = "https://spec.edmcouncil.org/fibo/ontology/master/2022Q1/FND/Accounting/ISO4217-CurrencyCodes/"
cty_url = "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/"

ccy_temp = "rdf_cty_ccy/rdfdata/ccy.rdf"
cty_temp = "rdf_cty_ccy/rdfdata/cty.rdf"

cty_ttl_loc = "rdf_cty_ccy/rdfdata/ISO3166-1-CountryCodes.ttl"
ccy_ttl_loc = "rdf_cty_ccy/rdfdata/ISO4217-CurrencyCodes.ttl"
ccy_ext_ttl_loc = "rdf_cty_ccy/rdfdata/sfo-currency-extensions.ttl"

ccy_rdf_pickle = "rdf_cty_ccy/rdfdata/ISO3166-1-CountryCodes.p"
cty_rdf_pickle = "rdf_cty_ccy/rdfdata/ISO4217-CurrencyCodes.p"

full_graph_rdf_pickle = "rdf_cty_ccy/rdfdata/cty-ccy-rdf.p"

def builder(args=None):
    """
    Examples:
          poetry run build_onto --loc rdf_cty_ccy/rdfdata/
    """

    parser = argparse.ArgumentParser(description='Downloads CCY and CTY ontologies and builds as TTL')
    parser.add_argument('--loc', type=str, nargs='?', default="rdf_cty_ccy/rdfdata/",
                        help='Location for the TTL files')

    if not args:
        args = parser.parse_args()

    ccy_result = create_ttl(url=ccy_url, temp=ccy_temp, ttl_out=ccy_ttl_loc, pickle_out=ccy_rdf_pickle)
    cty_result = create_ttl(url=cty_url, temp=cty_temp, ttl_out=cty_ttl_loc, pickle_out=cty_rdf_pickle)
    create_pickled_rdf(pickle_out=full_graph_rdf_pickle)
    pass


def create_ttl(url, temp, ttl_out, pickle_out):
    print("Building: {url} to {ttl}".format(url=url, ttl=ttl_out))
    result = requests.get(url)
    with open(temp, 'w') as f:
        f.write(result.text)

    g = graph.rdf_graph()
    g.parse(temp)
    write_to_ttl(g, format="turtle", file=ttl_out)
    os.remove(temp)
    print("Result: OK")
    return "OK"

def write_to_ttl(g, format="turtle", file=None):
    if format == "turtle":
        txt = g.serialize(format=format)
    else:
        txt = g.serialize(format="json-ld", indent=4)
    if file:
        with open(file, 'w') as f:
            f.write(txt)

def create_pickled_rdf(pickle_out):
    print("Creating Pickled RDF: to {pickle}".format(pickle=pickle_out))
    g = graph.load_from_ttl()
    write_to_pickle(g, pickle_out)
    print("Result: OK")
    pass

def write_to_pickle(g, file):
    f = open(file, 'wb')
    pickle.dump(g, f)
    f.close()
    pass
