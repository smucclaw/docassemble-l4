# This is a program that takes an scasp source file written using our lpdat
# implementation in s(CASP), and a query for something that may or may not
# legally hold, and returns a list of predicates that could be relevant to
# answering that question.

# Note that it will not work on other scasp code that does not use the lpdat
# implementation, as it is aware of the semantics of the defeasibility system
# used in our lpdat implementation, and takes shortcuts on that basis.

# To use this code, call relevant_to(scasp_code,query) where the query is
# the conclusion that may or may not legally hold. It will return a set of
# strings that describe the input terms to the scasp code that are relevant
# to answering that question.

import networkx as nx
import docassemble.scasp.scaspparser as sp
import pyparsing
import string
import re

def relevant_to(scasp_code,query):
    dg = build_graph(scasp_code)
    relevant = nx.descendants(dg,generalize(sp.term.parseString(query,True)))
    leaves = set()
    for r in relevant:
        if not nx.descendants(dg,r):
            leaves.add(r)
    return leaves

def build_graph(scasp_code):
    parse = sp.program.ParseString(scasp_code,True)
    dg = nx.DiGraph()
    # Add all of the rules that conclude anything and their conclusions as nodes,
    # with an edge from the conclusion to the rule.
    rules = entity_search(parse,'rule')
    for r in rules:
        conclusion = r['conclusion'][0]
        if conclusion['functor']['base atom'] not in ['opposes','compromised','disqualified','defeated_by_closure','legally_holds','defeated','rebutted_by','refuted_by','unsafe_rebutted_by','defeated_by_rebuttal','defeated_by_refutation','defeated_by_disqualification']:
            if conclusion['functor']['base atom'] == 'according_to':
                conclusion_node = generalize(conclusion['arguments'][1][0])
                rule_node = conclusion['arguments'][0][0]['functor']['base atom']
                condition_target = rule_node
                dg.add_node(rule_node)
                dg.add_node(conclusion_node)
                dg.add_edge(conclusion_node,rule_node)
            else:
                conclusion_node = generalize(conclusion)
                condition_target = conclusion_node
                dg.add_node(conclusion_node)

            # Add conditions and edges to the condition target.
            conditions = entity_search(r,'conditions')[0]
            for c in conditions:
                    if generalize(c):
                        if 'term' in c:
                            target = c
                        elif 'negation as failure' in c:
                            target = c['negation as failure']
                        if target['term']['functor']['base atom'] == 'according_to':
                            dg.add_node(generalize(c['term']['arguments'][1]))
                            dg.add_edge(condition_target,generalize(c['term']['arguments'][1]))
                        else:
                            dg.add_node(generalize(c))
                            dg.add_edge(condition_target,generalize(c))
                

    # Add all the defeating relationships as edges.
    facts = entity_search(parse,'fact')
    for f in facts:
        if 'base atom' in f['term']['functor']:
            if f['term']['functor']['base atom'] == 'overrides':
                if 'term' in f['term']['arguments'][0] and 'term' in f['term']['arguments'][2]:        
                    dg.add_edge(f['term']['arguments'][2]['term']['functor']['base atom'],f['term']['arguments'][0]['term']['functor']['base atom'])
    dg.graph['graph']={'rankdir':'LR'}
    return dg

def generalize(argument):
    term = generalize_scasp_term(argument)
    if term:
        return generalize_scasp_variables(term)
    else:
        return None

def generalize_scasp_term(input_term):
    if 'variable' in input_term:
        output = input_term['variable']
    elif 'silent variable' in input_term:
        output = "_"
    elif 'negation as failure' in input_term:
        output = generalize_scasp_term(input_term['negation as failure'])
    elif 'term' in input_term:
        output = generalize_scasp_term(input_term['term'])
    elif 'functor' in input_term:
        if 'base atom' in input_term['functor']:
            output = input_term['functor']['base atom']
        elif 'negative atom' in input_term['functor']:
            output = input_term['functor']['negative atom']['base atom']
        if 'arguments' in input_term:
            output += "("
            for a in input_term['arguments']:
                output += generalize_scasp_term(a)
                output += ","
            output += ")"
    elif 'constraint' in input_term:
        return None
    else:
        raise Exception("Unexpected term type in generalization.")
    return output.replace(",)",")")

def generalize_scasp_variables(argument):
    var_index = 0
    var_dict = {}
    # Count variables in the reformatted statement
    variable_pattern = re.compile(r"([A-Z][^\(\)\<\%\,]*)")
    matches = variable_pattern.findall(argument)
    # Go through the variables
    for i in range(len(matches)):
        if matches[i] in var_dict:
            replacement = var_dict[matches[i]]
        else:
            replacement = string.ascii_uppercase[var_index]
            var_dict[matches[i]] = replacement
            var_index = var_index + 1
    output = argument
    for k,v in var_dict.items():
        output = output.replace("(" + k + ")","(" + v + ")")
        output = output.replace("," + k + ")","," + v + ")")
        output = output.replace("(" + k + ",","(" + v + ",")
        output = output.replace("," + k + ",","," + v + ",")
    return output


def entity_search(l,target):
    results = []
    if target in l:
        results.append(l[target])
    for i in range(len(l)):
        if isinstance(l[i-1],pyparsing.ParseResults) and target in l[i-1]:
            results.append(l[i-1][target])
        if isinstance(l[i-1],pyparsing.ParseResults):
            child_search = entity_search(l[i-1],target)
            if len(child_search):
                results += child_search
    return results