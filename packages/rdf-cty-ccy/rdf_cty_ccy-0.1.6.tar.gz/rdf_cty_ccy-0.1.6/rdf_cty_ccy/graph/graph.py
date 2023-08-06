from rdflib import Graph
from simple_memory_cache import GLOBAL_CACHE
from pathlib import Path
import pickle

base_path = Path(__file__).parent

from . import binding

graph_cache = GLOBAL_CACHE.MemoryCachedVar('graph_cache')

from_pickle = True

currency_code_triples = (base_path / "../rdfdata/ISO3166-1-CountryCodes.ttl").resolve()
full_graph_rdf_pickle = (base_path / "../rdfdata/cty-ccy-rdf.p").resolve()
country_code_triples = (base_path / "../rdfdata/ISO4217-CurrencyCodes.ttl").resolve()
sfo_currency_extensions = (base_path / '../rdfdata/sfo-currency-extensions.ttl').resolve()

def graph():
    return graph_cache.get()

def invalidate_cache():
    graph_cache.invalidate()
    pass

@graph_cache.on_first_access
def build_graph():
    if from_pickle:
        return load_graph_from_pickle()

    return load_from_ttl()

def load_from_ttl():
    g = initgraph()
    g.parse(currency_code_triples)
    g.parse(country_code_triples)
    g.parse(sfo_currency_extensions)
    return g


def load_graph_from_pickle():
    f = open(full_graph_rdf_pickle, 'rb')
    g = pickle.load(f)
    f.close()
    return g

def initgraph() -> Graph:
    return binding.bind(rdf_graph())

def rdf_graph():
    return Graph()