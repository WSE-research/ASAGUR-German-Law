# plugin for law chain project
# the plugin creates links between enteties if text has a reference to another entity
# input: all TTL files in a folder (in_folder)
# output: new TTL file for each input file (out_folder)

import re
import pathlib

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS

from pyparsing import Word, alphanums, nums, ZeroOrMore, Regex, Literal, Optional
from pyparsing import pyparsing_unicode


alphas = pyparsing_unicode.Latin1.alphas

inner_test = [
    'Die §§ 16 bis 19 Absatz 1 und 2 gelten entsprechend',
    'Abgabe nach § 9 Absatz 1 oder § 10 Absatz 1 und 4 des Jugendschutzgesetzes verboten ist',
]

Gesetz = Regex(r'des.*?[Gg]esetzes\b') # starting with article non-greedy regex
Ordnung = Regex(r'der.*?[Oo]rdnung\b')
Buch = Regex(r'des.*?[Bb]uch\b') | Regex(r'des.*?[Bb]uchs\b') | Regex(r'des.*?[Bb]uches\b')

OuterRef = Gesetz | Ordnung | Buch

Connective = Literal('bis') | Literal('und') | Literal('oder')

Buchstabe = (Literal('Buchstabe') | Literal('lit.')) + Word(alphanums)

Number = (Literal('Nummer') | Literal('Nr.')) + Word(alphanums) + Optional(Buchstabe)
Numbers = Number + ZeroOrMore(Connective + Number)

Satz = Literal('Satz') + Word(nums) + Optional(Number)
Satze = Satz + ZeroOrMore(Connective + Satz)

Absatz = (Literal('Absatz') | Literal('Abs.')) + Word(alphanums) + Optional(Numbers | Satze) + Optional(OuterRef)
Absatze = Absatz + ZeroOrMore(Connective + (Absatz | Regex(r'\d\a*')))

assert ' '.join(list(Absatze.scanString(inner_test[1]))[1][0]) == 'Absatz 1 und 4'

Par = Word(alphanums) + ZeroOrMore(Absatze) + Optional(OuterRef)
Paragraph = Literal('§') + Par
PPar = Literal('§§') + Par
Paragraphs = (Paragraph + ZeroOrMore(Connective + Optional(Literal('des')) + Paragraph)) | (PPar + ZeroOrMore(Connective + Par))

assert ' '.join(list(Paragraphs.scanString(inner_test[1]))[0][0]) == '§ 9 Absatz 1 oder § 10 Absatz 1 und 4 des Jugendschutzgesetzes'

CrossRef = Paragraphs | Absatze | Numbers | Satze


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
    

def normalize(text: str) -> str:
    return text.replace('Absatz', 'Abs.')


def step(in_folder: str, out_folder: str) -> None:
    for file_name in pathlib.Path(in_folder).glob('*.ttl'):
        print(f'  Processing {file_name}')
            
        g = Graph()
        g.parse(file_name)

        document = build_n_run(g, '?value a dtd:dokumente', 1)

        amtabk = build_n_run(g, f'{document} dtd:has_norm/dtd:has_metadaten/dtd:has_amtabk/dtd:has_Value ?value', 1)

        absatze = build_n_run(g, f'?value a dtd:P .')
        
        for i in absatze:
            abs_text = build_n_run(g, f'{i} dtd:has_Value ?value .', 1)
            
            for result in Paragraphs.scanString(abs_text):
                ref = [i for i in result if i]
                ref = amtabk + ' ' + normalize(' '.join(ref[0]))
                linked = build_n_run(g, f'?value rdfs:label "{ref}"')

                for link in linked:
                    g.add((URIRef(i), URIRef('http://www.w3.org/ns/org#linkedTo'), URIRef(link)))

        g.serialize(
                destination=f'{out_folder}/{file_name.stem}.ttl',
                format='turtle')
        

class Plugin:

    @staticmethod
    def get_name() -> str:
        return 'generate_cross_refernces'
    
    @staticmethod
    def process(in_folder: str, out_folder: str):
        step(in_folder, out_folder)


# print(f'Input folder: {in_dir}')
# print(f'Output folder: {out_dir}')
# print(f'Starting conversion...')
# step000(in_dir, out_dir)