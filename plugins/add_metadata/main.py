# plugin for german law ontology project
# the plugin adds metadata to each law
# input: all TTL files in a folder (in_folder)
# output: new TTL file for each input file (out_folder)

import re
import pathlib
from datetime import datetime

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS, SDO


def now():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


metadata = {  # TODO: add more metadata, move to config file
    'author': 'alexgah',
    'data_created': now(),
}


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
    metadata['data_created'] =  now()

    for file_name in pathlib.Path(in_folder).glob('*.ttl'):
        print(f'Processing {file_name}')
            
        g = Graph()
        g.parse(file_name)

        g.add((URIRef('dtd:metadata'), SDO.author, Literal(metadata['author'])))
        g.add((URIRef('dtd:metadata'), SDO.dateCreated, Literal(metadata['data_created'], datatype=SDO.DateTime)))

        g.serialize(
                destination=f'{out_folder}/{file_name.stem}.ttl',
                format='turtle')


class Plugin:

    @staticmethod
    def get_name() -> str:
        return 'add_metadata'
    
    @staticmethod
    def process(in_folder: str, out_folder: str):
        step(in_folder, out_folder)