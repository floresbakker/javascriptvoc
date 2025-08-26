# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 18:40:53 2023

@author: Flores Bakker

The Javascript2RDF script to parse arbitrary Javascript code into a RDF-based model of the corresponding Abstract Syntax Tree.

Usage: 

1. Processing javascript
    
A. Processing raw javascript code
In the command prompt, run 'python Javascript2RDF.py --code "<insert some javascript code>" --format ttl

B. Processing a javascript file
In the command prompt, run 'python Javascript2RDF.py input\test.js --format ttl'

2. Getting output
In the output of the command prompt, copy your RDF-based generated abstract syntax tree.

"""

import argparse
import esprima
from typing import Any, Dict, List
from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, XSD


counters: Dict[str, int] = {}  # global counters for node types


def normalize(node: Any) -> Dict[str, Any]:
    """Ensure we always have a plain dict."""
    if hasattr(node, "toDict"):
        return node.toDict()
    if isinstance(node, dict):
        return node
    return node


def is_ast_node(v: Any) -> bool:
    v = normalize(v)
    return isinstance(v, dict) and "type" in v


def scalar_props(node: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in node.items():
        if k in {"type", "range", "loc"}:
            continue
        v = normalize(v)
        if is_ast_node(v):
            continue
        if isinstance(v, list) and any(is_ast_node(i) for i in v):
            continue
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
    return out


def node_uri(base_ns: Namespace, node_type: str) -> URIRef:
    """Generate semantic IRI for a node type."""
    global counters
    counters.setdefault(node_type, 0)
    counters[node_type] += 1
    return URIRef(str(base_ns) + f"{node_type}/{counters[node_type]}")


def add_rdf_list(g: Graph, items: List[URIRef]) -> URIRef:
    if not items:
        return RDF.nil
    head = BNode()
    current = head
    for i, item in enumerate(items):
        g.add((current, RDF.first, item))
        if i == len(items) - 1:
            g.add((current, RDF.rest, RDF.nil))
        else:
            nxt = BNode()
            g.add((current, RDF.rest, nxt))
            current = nxt
    return head


def add_node(g: Graph, js: Namespace, base_ns: Namespace, node: Any) -> URIRef:
    node = normalize(node)
    node_type = node["type"]

    s = node_uri(base_ns, node_type)

    # type
    g.add((s, RDF.type, js.term(node_type)))
    g.add((s, RDFS.label, Literal(node_type)))

    # scalar props
    for k, v in scalar_props(node).items():
        pred = js.term(k)
        if isinstance(v, bool):
            lit = Literal(v)
        elif isinstance(v, int):
            lit = Literal(v, datatype=XSD.integer)
        elif isinstance(v, float):
            lit = Literal(v, datatype=XSD.double)
        else:
            lit = Literal(v)
        g.add((s, pred, lit))

    # child nodes
    for key, value in node.items():
        if key in {"type", "range", "loc"}:
            continue
        value = normalize(value)
        pred = js.term(key)
        if is_ast_node(value):
            child_uri = add_node(g, js, base_ns, value)
            g.add((s, pred, child_uri))
        elif isinstance(value, list) and any(is_ast_node(v) for v in value):
            child_uris = []
            for child in value:
                if is_ast_node(child):
                    child_uri = add_node(g, js, base_ns, child)
                    child_uris.append(child_uri)
            list_node = add_rdf_list(g, child_uris)
            g.add((s, pred, list_node))

    return s


def convert_js_to_rdf(code: str, base: str, vocab: str) -> Graph:
    g = Graph()
    base_ns = Namespace(base if base.endswith(("/", "#")) else base + "/")
    js = Namespace(vocab if vocab.endswith(("/", "#")) else vocab + "#")

    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("js", js)

    ast = esprima.parseScript(code, loc=True, range=True)
    ast_dict = normalize(ast)

    add_node(g, js, base_ns, ast_dict)
    return g


def main():
    ap = argparse.ArgumentParser(description="JavaScript AST to RDF triples (Esprima)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("input", nargs="?", help="Path to JavaScript source file")
    src.add_argument("--code", help="Raw JavaScript code")

    ap.add_argument("-o", "--output", help="Output file (default stdout)")
    ap.add_argument("--format", default="turtle", choices=["turtle", "ttl", "nt", "ntriples", "xml", "json-ld", "trig", "nq"])
    ap.add_argument("--base", default="https://example.org/code/ast/")
    ap.add_argument("--vocab", default="https://www.javascript.fin.rijksweb.nl/model/def/")

    args = ap.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            code = f.read()
    else:
        code = args.code or ""

    g = convert_js_to_rdf(code, args.base, args.vocab)

    fmt = "turtle" if args.format == "ttl" else "nt" if args.format == "ntriples" else args.format
    data = g.serialize(format=fmt)

    if args.output:
        with open(args.output, "wb") as f:
            f.write(data)
    else:
        try:
            print(data.decode("utf-8"))
        except AttributeError:
            print(data)


if __name__ == "__main__":
    main()
