# plugin for German law ontology project
# the plugin merges all single laws in one graph
# input: all TTL files in a folder (in_folder)
# output: new german_law.ttl file (out_folder)

import pathlib

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS


def step(in_folder: str, out_folder: str) -> None:
    g = Graph()

    for x, file_name in enumerate(pathlib.Path(in_folder).glob('*.ttl')):
        print(f'Processing {file_name}...')            
        g.parse(file_name)

    g.serialize(
            destination=f'{out_folder}/german_laws.ttl',
            format='turtle')


class Plugin:
    @staticmethod
    def get_name() -> str:
        return 'merge'
    
    @staticmethod
    def process(in_folder: str, out_folder: str):
        step(in_folder, out_folder)
