from docassemble.l4.relevance import *
import networkx as nx
import pydot

scasp = open('docassemble/l4/data/static/r34.pl','r')
scaspc = scasp.read()
scasp.close()
graph = build_graph(scaspc)
dot = nx.nx_pydot.to_pydot(graph)
dot.write('test.dot')

