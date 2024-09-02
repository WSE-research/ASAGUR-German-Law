# plugin for German law ontology project
# the plugin creates labels for absatz
# input: all TTL files in a folder (in_folder)
# output: new TTL file for each input file (out_folder)

import re
import pathlib

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS


def build_sparql(where: str, limit: int=None) -> str:
    query = [
        'SELECT DISTINCT ?value WHERE {',
        re.sub('\S+#', 'dtd:', where),
        f'}} LIMIT {limit}' if limit else '}',
    ]
    return '\n'.join(query)


def run_sparql(g: Graph, sparql: str, var_name: str, limit:int=None):
    result_ = g.query(sparql)
    
    result = []
    for row in result_:
        result.append(str(row[var_name]))
    
    if limit and limit == 1:
        return result[0]
    else:
        return result
    
    
def build_n_run(g: Graph, where: str, limit:int=None):
    try:
        return run_sparql(g, build_sparql(where, limit), 'value', limit)
    except:
        return None
    

def step(in_folder: str, out_folder: str) -> None:
    for x, file_name in enumerate(pathlib.Path(in_folder).glob('*.ttl')):
        print(f'Processing {file_name}...')
            
        g = Graph()
        g.parse(file_name)

        amtabk = build_n_run(g, f'{document} dtd:has_norm/dtd:has_metadaten/dtd:has_amtabk/dtd:has_Value ?value', 1)
        if not amtabk:
            continue

        norms = build_n_run(g, f'?value a dtd:norm .')
        if not norms:
            continue

        document = build_n_run(g, '?value a dtd:dokumente', 1)

        for norm in norms:
            enbez = build_n_run(g, f'{norm} dtd:has_metadaten/dtd:has_enbez/dtd:has_Value ?value', 1)
            
            absatze = build_n_run(g, f'{norm} dtd:has_textdaten/dtd:has_text/dtd:has_Content/dtd:has_P ?value .')

            if absatze:
                par_n += len(absatze)

            if not enbez or '§' not in enbez:
                continue

            g.add((URIRef(norm), RDFS.label, Literal(f'{amtabk} {enbez}')))
                
            absatze = build_n_run(g, f'{norm} dtd:has_textdaten/dtd:has_text/dtd:has_Content/dtd:has_P ?value .')
            
            for i in absatze:
                abs_text = build_n_run(g, f'{i} dtd:has_Value ?value .', 1)
                abs_nr = re.findall('^\(([1-9][^\s]*?)\)', abs_text)
                
                if abs_nr:
                    absatz = f'{amtabk} {enbez} Abs. {abs_nr[0]}'
                    g.add((URIRef(i), RDFS.label, Literal(absatz)))

        g.serialize(
                destination=f'{out_folder}/{file_name.stem}.ttl',
                format='turtle')


class Plugin:
    @staticmethod
    def get_name() -> str:
        return 'create_labels'
    
    @staticmethod
    def process(in_folder: str, out_folder: str):
        step(in_folder, out_folder)
