# plugin for german law ontology project
# the plugin adds types for known classes and
# changes some binary classes to boolean true/false
# input: all TTL files in a folder (in_folder)
# output: new TTL file for each (out_folder)

import re
import pathlib

from collections import defaultdict as ddict

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import FOAF, RDF, RDFS, XSD


LITERAL_TRANSFORMS = [
    {
        'entity_type': 'urn:asagur#ausfertigung-datum',
        'predicate': 'urn:asagur#has_Value',
        'type': XSD.date,
        'action': 'change_type',
    },
    # {
    #     'predicate': 'urn:asagur#has_Height',
    #     'type': XSD.integer,
    #     'action': 'change_type',
    # },
    {
        'predicate': 'dtd:has_builddate',
        'type': XSD.date,
        'action': 'convert_to_date',
    },
    {
        'predicate': 'urn:asagur#has_manuell',
        'object': 'urn:asagur#ja',
        'action': 'replace_object',
        'value': 'true',
        'type': XSD.boolean,
    },
    {
        'predicate': 'urn:asagur#has_manuell',
        'object': 'urn:asagur#nein',
        'action': 'replace_object',
        'value': 'false',
        'type': XSD.boolean,
    },
]


def convert_to_datetime(value: str) -> str:
    value = [i+j for i, j in zip(value[::2], value[1::2])]
    return f'{value[0]}{value[1]}-{value[2]}-{value[3]}T{value[4]}:{value[5]}:{value[6]}'
    

def step(in_folder: str, out_folder: str) -> None:
    for file_name in pathlib.Path(in_folder).glob('*.ttl'):
        print(f'Processing {file_name}')
            
        g = Graph()
        g.parse(file_name)

        for i in LITERAL_TRANSFORMS:
            if i['action'] == 'change_type':
                entities = list(g.subjects(RDF.type, URIRef(i['entity_type']), True))
                
                for entity in entities:                        
                    for s, p, o in g.triples((entity, URIRef(i['predicate']), None)):
                        g.remove((s, p, o))
                        g.add((s, URIRef(i['predicate']), Literal(str(o), datatype=i['type'])))

            elif i['action'] == 'convert_to_date':
                spo = []

                for s, p, o in g.triples((None, URIRef('urn:asagur#has_builddate'), None)):
                    spo.append((s, p, o))

                for one in spo:
                    g.remove(one)
                    
                for s, p, o in spo:
                    o = Literal(convert_to_datetime(o), datatype=XSD.dateTime)
                    g.add((s, p, o))

            elif i['action'] == 'replace_object':
                spo = []

                for s, p, o in g.triples((None, URIRef(i["predicate"]), URIRef(i["object"]))):
                    spo.append((s, p, o))

                for one in spo:
                    g.remove(one)
                    
                for s, p, o in spo:
                    o = Literal(i['value'], datatype=i['type'] if 'type' in i else None)
                    g.add((s, p, o))

        g.serialize(
            destination=f'{out_folder}/{file_name.stem}.ttl',
            format='turtle')


class Plugin:
    @staticmethod
    def get_name() -> str:
        return 'add_types'
    
    @staticmethod
    def process(in_folder: str, out_folder: str):
        step(in_folder, out_folder)