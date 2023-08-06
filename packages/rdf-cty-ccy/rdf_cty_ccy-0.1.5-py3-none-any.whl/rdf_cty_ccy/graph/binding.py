from .rdf_prefix import *

def bind(g):
    g.bind('skos', skos)
    g.bind('owl', owl)
    g.bind('fibo-fnd-acc-cur', fibo_fnd_acc_cur)
    g.bind('fibo-fnd-utl-av',  fibo_fnd_utl_av)
    g.bind('fibo-fnd-acc-4217', fibo_fnd_acc_4217)
    g.bind('lcc-3166-1', lcc_3166_1)
    g.bind('lcc-cr', lcc_cr)
    g.bind('lcc-lr', lcc_lr)
    g.bind('sfo-cmn-ind-cur', sfo_cmn_ind_cur)
    return g
