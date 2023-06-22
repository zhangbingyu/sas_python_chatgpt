from collections import defaultdict
import graphviz
import networkx as nx
import json
import itertools

G = nx.Graph()
# responses = """
#     {
#         "blocks": [
#             {
#                 "input": {
#                     "names": ["source_data"],
#                     "variables": [["x", "y"]]
#                 },
#                 "output": {
#                     "names": ["target_data"],
#                     "variables": [["x1", "z"]]
#                 }
#             },
#             {
#                 "input": {
#                     "names": ["target_data"],
#                     "variables": [["z"]]
#                 },
#                 "output": {
#                     "names": ["target_data2"],
#                     "variables": [["z2", "z3", "z4"]]
#                 }
#             },
#             {
#                 "input": {
#                     "names": ["target_data2"],
#                     "variables": [["z3"]]
#                 },
#                 "output": {
#                     "names": ["target_data2"],
#                     "variables": [["z3", "z2"]]
#                 }
#             },
#             {
#                 "input": {
#                     "names": ["target_data", "target_data2"],
#                     "variables": [["z3"], ["y"]]
#                 },
#                 "output": {
#                     "names": ["target_data3"],
#                     "variables": [["x1", "z", "z2", "z3", "z4"]]
#                 }
#             }
#         ]
#     }
# """

def generate_network(data_flow):
    """generate a network graph from content in JSON"""
    blocks = data_flow['blocks']
    node_names = defaultdict(list)
    for block_id, pair in enumerate(blocks):
        # add nodes from input and output data sets
        input_nodes = []
        output_nodes = []
        if not pair["input"]["names"]:
            pair["input"]["names"] = ["Null"]
            pair["input"]["variables"] = [["Null"]]
        for name, variable in zip(pair["input"]["names"], pair["input"]["variables"]):
            if name not in node_names:
                G.add_node((name, block_id), variables = variable)
                node_names[name].append(block_id)
                input_nodes.append((name, block_id))
            else:
                input_nodes.append((name, node_names[name][-1]))

        for name, variable in zip(pair["output"]["names"], pair["output"]["variables"]):
            if name in pair["input"]["names"] and len(node_names[name]) == 1 and node_names[name][-1] == block_id:
                temp_id = block_id + 0.5
            else:
                temp_id = block_id
            G.add_node((name, temp_id),variables=variable)
            node_names[name].append(temp_id)
            output_nodes.append((name, temp_id))
        G.add_edges_from(itertools.product(input_nodes,output_nodes))
    return G

# print(G.edges())
def plot_flowchart(G):
    """plot a graph chart"""
    g = graphviz.Digraph("flow_chart", format="svg", node_attr={"shape": "record"})
    for node, attr in G.nodes().items():
        g.node(str(node), f"{{ {node[0]} | {'Vars: ' + ', '.join(attr['variables'])} }}")
    for edge in G.edges():
        g.edge(str(edge[0]), str(edge[1]))
    return g.pipe(encoding="utf-8")
