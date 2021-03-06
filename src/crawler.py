#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rdflib
import requests
import sys
import json

from rdflib import URIRef, Graph, plugin
from rdflib.namespace import DCTERMS, RDF, RDFS
from rdflib.serializer import Serializer

from datetime import datetime

# MASTER_NODE = "https://geoconnex.ca/id/LOD_Node/CAN_Hydro_LOD_Node"
MASTER_NODE = "https://cida-test.er.usgs.gov/chyld-pilot/info/LOD_Node/US_Hydro_LOD_Node"
# CONNECTED_PREDICATE = URIRef("https://geoconnex.ca/id/properties/connectedTo")
CONNECTED_PREDICATE = URIRef("https://geoconnex.ca/id/connectedTo")

# If you are not sure what format your file will be, 
# you can use rdflib.util.guess_format() which will 
# guess based on the file extension.

nodes = []

def main():
    crawl()

def crawl():
    """begin harvesting by finding connected nodes"""
    g = rdflib.Graph()
    # g.parse(MASTER_NODE, format='JSON-LD')
    g.parse(MASTER_NODE)

    print("\n--- printing namespaces ---\n")
    ns = g.namespaces()
    for n in ns:
        print(n)

    connected_nodes = harvest_nodes(g)

    # Temporary hack until GSIP is updated with the correct
    # node URL https://cida-test.er.usgs.gov/chyld-pilot/info/LOD_Node/US_Hydro_LOD_Node

    # connected_nodes = ['https://cida-test.er.usgs.gov/chyld-pilot/info/LOD_Node/US_Hydro_LOD_Node']

    print("\n--- printing connected linked open data nodes ---\n")
    for i, node in enumerate(connected_nodes, start=1):
        print("{}: {}\n".format(i, node))

        g = rdflib.Graph()
        try:
            r = g.parse(node)
        except:
            print(r)
            print("An error occurred whilst parsing the target resource!\n")
            continue

        harvest_triples(g)
        
    return json.dumps({'timestamp': datetime.now().timestamp(), 'nodes': connected_nodes})

def harvest_nodes(node):
    """harvest connected nodes"""
    
    for lnode in node.objects(predicate=CONNECTED_PREDICATE):
        if lnode not in nodes:
            nodes.append(lnode)

    return nodes

def harvest_triples(graph):
    """harvest triples from a given node"""
    # print("\ngraph has %s statements" % len(graph))
    
    # print("\n--- printing raw triples ---\n")
    # for s, p, o in graph:
    #     print((s, p, o))

    # print("\n--- printing N3 triples ---\n")
    # n = graph.serialize(format="n3")
    # print(n.decode())

    # for s in graph.subjects(predicate=URIRef('http://schema.org/subjectOf'), object=rdflib.term.Literal('application/rdf+xml')):
    for s in graph.objects(predicate=URIRef('http://schema.org/subjectOf')):

        if (s, RDF.type, URIRef('https://opengeospatial.github.io/SELFIE/DataNode_FeatureLinkSet')) in graph:
        
            g = rdflib.Graph()

            g.parse(s)
        
            harvest_feature_relations(g)

            break

def harvest_feature_relations(graph):
    """harvest feature relations and store them"""
    
    n = graph.serialize(format="n3")

    print("\n--- printing N3 triples ---\n")
    print(n.decode())
    
    # Write triples to file in n3 format
    f = open('data.n3', 'w')
    f.write(n.decode())
    f.close()

    # Post triple to triple store
    # try:
    #     url = 'http://127.0.0.1:9999/blazegraph/sparql'
    #     payload = open('data.n3')
    #     headers = {'content-type': 'text/n3', 'Accept-Charset': 'UTF-8'}
    #     r = requests.post(url, data=payload, headers=headers)

    #     print('\n' + r.content.decode() + '\n')
    # except requests.exceptions.RequestException as e:  # This is the correct syntax
    #     print(e)
    #     sys.exit(1)

def validate_triples(triple):
    """validate triple"""
    for subj, pred, obj in triple:
        if (subj, pred, obj) not in triple:
            raise Exception("Invalid triple!")
        else:
            return True

if __name__== "__main__":
    main()