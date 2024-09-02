# plugin for law ontology project
# the plugin deletes extra unwanted tags generated from XML
# input: all TTL files in a folder (in_folder)
# output: new TTL file for each input file (out_folder)

import pathlib

from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import FOAF, RDF, RDFS


EXTRA_TAGS = [
    'dtd:has_B',
    'dtd:has_I',
    'dtd:has_BR',
    'dtd:B',
    'dtd:I',
    'dtd:BR',
]
    

def step(in_folder: str, out_folder: str) -> None:
    for file_name in pathlib.Path(in_folder).glob('*.ttl'):
        print(f'Processing {file_name}')
            
        g = Graph()
        g.parse(file_name)

        for i in EXTRA_TAGS:
            query = [
                'DELETE WHERE {',
                f'?s {i} ?o',
                '}',
            ]
            query = '\n'.join(query)
            g.update(query)

            query = [
                'DELETE WHERE {',
                f'?s ?p {i}',
                '}',
            ]
            query = '\n'.join(query)
            g.update(query)

        g.serialize(
            destination=f'{out_folder}/{file_name.stem}.ttl',
            format='turtle')


class Plugin:

    @staticmethod
    def get_name() -> str:
        return 'delete_extra_tags'
    
    @staticmethod
    def process(in_folder: str, out_folder: str):
        step(in_folder, out_folder)