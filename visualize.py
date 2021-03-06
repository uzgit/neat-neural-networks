import os
import sys

# For use in contexts where this file is imported from outside this directory.
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from genome import *
from neural_network import *
import graphviz

fontsize = '9'

aggregation_function_label_names = {
    "sum" : "sum",
    "min" : "min",
    "max" : "max",
}

activation_function_label_names = {
    "arctan": "arctan",
    "binary_step": "step",
    "identity": "id",
    "lelu" : "lelu",
    "logistic": "log",
    "relu": "relu",
    "sigmoid" : "sig",
    "softplus": "splus",
    "step" : "step",
    "tanh": "tanh",
}

input_node_attributes = \
    {
        "shape": "circle",
        "fontsize": fontsize,
        "height": "0.2",
        "width": "0.2",
        "color": "red",
    }

hidden_node_attributes = \
    {
        "shape": "circle",
        "fontsize": fontsize,
        "height": "0.2",
        "width": "0.2",
    }

disabled_hidden_node_attributes = \
    {
        "shape": "circle",
        "fontsize": fontsize,
        "height": "0.2",
        "width": "0.2",
        "style": "dashed",
    }

output_node_attributes = \
    {
        "shape": "circle",
        "fontsize": fontsize,
        "height": "0.2",
        "width": "0.2",
        "color": "red",
    }

invisible_edge_attributes = \
    {
        "style" : "invisible",
        "arrowhead" : "none",
    }

def label(node):

    representation = ""
    if isinstance(node, Node):
        representation += str(node.layer)
    representation += "\n" + function_names[node.aggregation_function] + ", " + str(node.bias if node.bias == None else str(round(node.bias, 1)))
    representation += "\n" + function_names[node.activation_function]

    return representation

def draw_genome_active(genome, filename=None):

    assert isinstance(genome, Genome)

    graph = graphviz.Digraph(format="svg")
    input_node_subgraph = graphviz.Digraph("input nodes")
    input_node_subgraph.graph_attr.update(rank="min")

    hidden_node_subgraph = graphviz.Digraph("hidden nodes")
    # hidden_node_subgraph.graph_attr.update(rank="same")

    output_node_subgraph = graphviz.Digraph("output nodes")
    output_node_subgraph.graph_attr.update(rank="max")

    for input_node in [node for node in genome.nodes if node.is_input_node]:
        input_node_subgraph.node(str(input_node.identifier), xlabel=str(input_node.identifier), label=label(input_node), _attributes=input_node_attributes)

    for hidden_node in [node for node in genome.nodes if node.is_enabled and not node.is_input_node and not node.is_output_node]:
        hidden_node_subgraph.node(str(hidden_node.identifier), xlabel=str(hidden_node.identifier), label=label(hidden_node),_attributes=hidden_node_attributes)

    for output_node in [node for node in genome.nodes if node.is_output_node]:
        output_node_subgraph.node(str(output_node.identifier), xlabel=str(output_node.identifier), label=label(output_node), _attributes=output_node_attributes)

    # draw enabled edges
    for edge in [edge for edge in genome.edges if edge.is_enabled]:

        style = "solid"
        color = "black" if edge.weight > 0 else "grey"
        width = str(0.1 + abs(edge.weight / 5.0))

        graph.edge(str(edge.input_node_identifier), str(edge.output_node_identifier),
                   _attributes={"style": style, "color": color, "label": str("%0.2f" % edge.weight), "fontsize" : fontsize})

    input_nodes = [node for node in genome.nodes if node.is_input_node]
    hidden_nodes = [node for node in genome.nodes if not node.is_input_node and not node.is_output_node]
    output_nodes = [node for node in genome.nodes if node.is_output_node]
    if genome.num_hidden_nodes() > 0:

        for input_node in input_nodes:
            for hidden_node in hidden_nodes:
                graph.edge(str(input_node.identifier), str(hidden_node.identifier), _attributes=invisible_edge_attributes)

        for hidden_node in hidden_nodes:
            for output_node in output_nodes:
                graph.edge(str(hidden_node.identifier), str(output_node.identifier), _attributes=invisible_edge_attributes)
    else:
        for input_node in input_nodes:
            for output_node in output_nodes:
                graph.edge(str(input_node.identifier), str(output_node.identifier), _attributes=invisible_edge_attributes)

    graph.subgraph(input_node_subgraph)
    graph.subgraph(hidden_node_subgraph)
    graph.subgraph(output_node_subgraph)

    graph.render(view=True, filename=filename)

def draw_genome_full(genome, filename=None):

    assert isinstance(genome, Genome)

    graph = graphviz.Digraph(format="svg")
    input_node_subgraph = graphviz.Digraph("input nodes")
    input_node_subgraph.graph_attr.update(rank="min")

    hidden_node_subgraph = graphviz.Digraph("hidden nodes")
    # hidden_node_subgraph.graph_attr.update(rank="same")

    output_node_subgraph = graphviz.Digraph("output nodes")
    output_node_subgraph.graph_attr.update(rank="max")

    input_nodes = [node for node in genome.nodes if node.is_input_node]
    for input_node in input_nodes:
        # input_node_subgraph.node(str(input_node.identifier), _attributes=input_node_attributes)
        input_node_subgraph.node(str(input_node.identifier), xlabel=str(input_node.identifier), label=label(input_node),
                                 _attributes=input_node_attributes)

    hidden_nodes = [node for node in genome.nodes if
                    not node.is_input_node and not node.is_output_node and node.is_enabled]
    for hidden_node in hidden_nodes:
        # hidden_node_subgraph.node(str(hidden_node.identifier), _attributes=hidden_node_attributes)
        hidden_node_subgraph.node(str(hidden_node.identifier), xlabel=str(hidden_node.identifier),
                                  label=label(hidden_node), _attributes=hidden_node_attributes)

    disabled_hidden_nodes = [node for node in genome.nodes if
                             not node.is_input_node and not node.is_output_node and not node.is_enabled]
    for disabled_hidden_node in disabled_hidden_nodes:
        hidden_node_subgraph.node(str(disabled_hidden_node.identifier), xlabel=str(disabled_hidden_node.identifier),
                                  label=label(disabled_hidden_node), _attributes=disabled_hidden_node_attributes)

    output_nodes = [node for node in genome.nodes if node.is_output_node]
    for output_node in output_nodes:
        # output_node_subgraph.node(str(output_node.identifier), _attributes=output_node_attributes)
        output_node_subgraph.node(str(output_node.identifier), xlabel=str(output_node.identifier),
                                  label=label(output_node), _attributes=output_node_attributes)

    # draw enabled edges
    for edge in genome.edges:
        style = "solid" if edge.is_enabled else "dashed"
        color = "black" if edge.weight > 0 else "grey"
        width = str(0.1 + abs(edge.weight / 5.0))

        graph.edge(str(edge.input_node_identifier), str(edge.output_node_identifier),
                   _attributes={"style": style, "color": color, "label": str("%0.2f" % edge.weight),
                                "fontsize": fontsize, })

    # draw invisible edges between input nodes, hidden nodes, and output nodes
    input_nodes = [node for node in genome.nodes if node.is_input_node]
    hidden_nodes = [node for node in genome.nodes if not node.is_input_node and not node.is_output_node]
    output_nodes = [node for node in genome.nodes if node.is_output_node]
    if genome.num_hidden_nodes() > 0:

        for input_node in input_nodes:
            for hidden_node in hidden_nodes:
                graph.edge(str(input_node.identifier), str(hidden_node.identifier),
                           _attributes=invisible_edge_attributes)

        for hidden_node in hidden_nodes:
            for output_node in output_nodes:
                graph.edge(str(hidden_node.identifier), str(output_node.identifier),
                           _attributes=invisible_edge_attributes)
    else:
        for input_node in input_nodes:
            for output_node in output_nodes:
                graph.edge(str(input_node.identifier), str(output_node.identifier),
                           _attributes=invisible_edge_attributes)

    graph.subgraph(input_node_subgraph)
    graph.subgraph(hidden_node_subgraph)
    graph.subgraph(output_node_subgraph)

    graph.render(view=True, filename=filename)

def draw_neural_network_active(network, filename=None):

    assert isinstance(network, FeedForwardNeuralNetwork)

    graph = graphviz.Digraph(format="svg")
    input_node_subgraph = graphviz.Digraph("input nodes")
    input_node_subgraph.graph_attr.update(rank="min")

    hidden_node_subgraph = graphviz.Digraph("hidden nodes")
    # hidden_node_subgraph.graph_attr.update(rank="same")

    output_node_subgraph = graphviz.Digraph("output nodes")
    output_node_subgraph.graph_attr.update(rank="max")

    for input_node in network.input_nodes:
        input_node_subgraph.node(str(input_node.identifier), xlabel=str(input_node.identifier), label=label(input_node), _attributes=input_node_attributes)

    for hidden_node in [node for node in network.hidden_nodes if node.layer is not None]:
        hidden_node_subgraph.node(str(hidden_node.identifier), xlabel=str(hidden_node.identifier), label=label(hidden_node),_attributes=hidden_node_attributes)

    for output_node in network.output_nodes:
        output_node_subgraph.node(str(output_node.identifier), xlabel=str(output_node.identifier), label=label(output_node), _attributes=output_node_attributes)

    # draw enabled edges
    for edge in [edge for edge in network.edges]:

        style = "solid"
        color = "black" if edge.weight > 0 else "grey"
        width = str(0.1 + abs(edge.weight / 5.0))

        graph.edge(str(edge.input_node_identifier), str(edge.output_node_identifier),
                   _attributes={"style": style, "color": color, "label": str("%0.2f" % edge.weight), "fontsize" : fontsize})

    input_nodes = [node for node in network.nodes if node.is_input_node]
    hidden_nodes = [node for node in network.nodes if not node.is_input_node and not node.is_output_node]
    output_nodes = [node for node in network.nodes if node.is_output_node]
    if network.num_hidden_nodes() > 0:

        for input_node in input_nodes:
            for hidden_node in hidden_nodes:
                graph.edge(str(input_node.identifier), str(hidden_node.identifier), _attributes=invisible_edge_attributes)

        for hidden_node in hidden_nodes:
            for output_node in output_nodes:
                graph.edge(str(hidden_node.identifier), str(output_node.identifier), _attributes=invisible_edge_attributes)
    else:
        for input_node in input_nodes:
            for output_node in output_nodes:
                graph.edge(str(input_node.identifier), str(output_node.identifier), _attributes=invisible_edge_attributes)

    graph.subgraph(input_node_subgraph)
    graph.subgraph(hidden_node_subgraph)
    graph.subgraph(output_node_subgraph)

    graph.render(view=True, filename=filename)

def draw_neural_network_full_trying_stuff(network, filename=None):

    assert isinstance(network, FeedForwardNeuralNetwork)

    graph = graphviz.Digraph(format="svg")
    input_node_subgraph = graphviz.Digraph("input nodes")
    input_node_subgraph.graph_attr.update(rank="same")

    hidden_node_subgraph = graphviz.Digraph("hidden nodes")
    # hidden_node_subgraph.graph_attr.update(rank="same")

    output_node_subgraph = graphviz.Digraph("output nodes")
    output_node_subgraph.graph_attr.update(rank="same")

    subgraphs = []

    for current_layer in range(network.min_layer, network.max_layer + 1):
        subgraphs.append(graphviz.Digraph("layer {} nodes".format(current_layer)))

        output_node_in_current_layer = any([node.is_output_node for node in network.nodes if node.layer == current_layer])

        if output_node_in_current_layer:
            subgraphs[-1].graph_attr.update(rank="max")
        else:
            subgraphs[-1].graph_attr.update(rank="same")

        for node in [node for node in network.nodes if node.layer == current_layer]:

            if node.is_input_node:
                attributes = input_node_attributes
            elif node.is_output_node:
                attributes = output_node_attributes
            else:
                attributes = hidden_node_attributes

            subgraphs[-1].node(str(node.identifier), xlabel=str(node.identifier), label=label(node), _attributes=attributes)

    inactive_node_subgraph = graphviz.Digraph("inactive nodes")
    for node in [node for node in network.nodes if node.layer == None]:

        if node.is_input_node:
            attributes = input_node_attributes
        elif node.is_output_node:
            attributes = output_node_attributes
        else:
            attributes = hidden_node_attributes

        inactive_node_subgraph.node(str(node.identifier), xlabel=str(node.identifier), label=label(node), _attributes=attributes)

    # draw enabled edges
    for edge in network.edges:

        style = "solid" if edge.is_enabled else "dashed"
        color = "black" if edge.weight > 0 else "grey"
        width = str(0.1 + abs(edge.weight / 5.0))

        graph.edge(str(edge.input_node_identifier), str(edge.output_node_identifier),
                   _attributes={"style":style, "color":color, "label":str("%0.2f" % edge.weight), "fontsize":fontsize,})

    # draw invisible edges between input nodes, hidden nodes, and output nodes
    # input_nodes = [node for node in network.nodes if node.is_input_node]
    # hidden_nodes = [node for node in network.nodes if not node.is_input_node and not node.is_output_node]
    # output_nodes = [node for node in network.nodes if node.is_output_node]
    # if network.num_hidden_nodes > 0:
    #
    #     for input_node in input_nodes:
    #         for hidden_node in hidden_nodes:
    #             graph.edge(str(input_node.identifier), str(hidden_node.identifier), _attributes=invisible_edge_attributes)
    #
    #     for hidden_node in hidden_nodes:
    #         for output_node in output_nodes:
    #             graph.edge(str(hidden_node.identifier), str(output_node.identifier), _attributes=invisible_edge_attributes)
    # else:
    #     for input_node in input_nodes:
    #         for output_node in output_nodes:
    #             graph.edge(str(input_node.identifier), str(output_node.identifier), _attributes=invisible_edge_attributes)

    # graph.subgraph(input_node_subgraph)
    # graph.subgraph(hidden_node_subgraph)
    # graph.subgraph(output_node_subgraph)

    for subgraph in subgraphs:
        graph.subgraph(subgraph)

    graph.render(view=True, filename=filename)

def draw_neural_network_full(network, filename=None):

    assert isinstance(network, FeedForwardNeuralNetwork)

    graph = graphviz.Digraph(format="svg")
    input_node_subgraph = graphviz.Digraph("input nodes")
    input_node_subgraph.graph_attr.update(rank="min")

    hidden_node_subgraph = graphviz.Digraph("hidden nodes")
    # hidden_node_subgraph.graph_attr.update(rank="same")

    output_node_subgraph = graphviz.Digraph("output nodes")
    output_node_subgraph.graph_attr.update(rank="max")

    input_nodes = [node for node in network.nodes if node.is_input_node]
    for input_node in input_nodes:
        # input_node_subgraph.node(str(input_node.identifier), _attributes=input_node_attributes)
        input_node_subgraph.node(str(input_node.identifier), xlabel=str(input_node.identifier), label=label(input_node), _attributes=input_node_attributes)

    hidden_nodes = [node for node in network.nodes if not node.is_input_node and not node.is_output_node and node.is_enabled]
    for hidden_node in hidden_nodes:
        # hidden_node_subgraph.node(str(hidden_node.identifier), _attributes=hidden_node_attributes)
        hidden_node_subgraph.node(str(hidden_node.identifier), xlabel=str(hidden_node.identifier), label=label(hidden_node),_attributes=hidden_node_attributes)

    disabled_hidden_nodes = [node for node in network.nodes if not node.is_input_node and not node.is_output_node and not node.is_enabled]
    for disabled_hidden_node in disabled_hidden_nodes:
        hidden_node_subgraph.node(str(disabled_hidden_node.identifier), xlabel=str(disabled_hidden_node.identifier), label=label(disabled_hidden_node), _attributes=disabled_hidden_node_attributes)

    output_nodes = [node for node in network.nodes if node.is_output_node]
    for output_node in output_nodes:
        # output_node_subgraph.node(str(output_node.identifier), _attributes=output_node_attributes)
        output_node_subgraph.node(str(output_node.identifier), xlabel=str(output_node.identifier), label=label(output_node), _attributes=output_node_attributes)

    # draw enabled edges
    for edge in network.edges:

        style = "solid" if edge.is_enabled else "dashed"
        color = "black" if edge.weight > 0 else "grey"
        width = str(0.1 + abs(edge.weight / 5.0))

        graph.edge(str(edge.input_node_identifier), str(edge.output_node_identifier),
                   _attributes={"style":style, "color":color, "label":str("%0.2f" % edge.weight), "fontsize":fontsize,})

    # draw invisible edges between input nodes, hidden nodes, and output nodes
    input_nodes = [node for node in network.nodes if node.is_input_node]
    hidden_nodes = [node for node in network.nodes if not node.is_input_node and not node.is_output_node]
    output_nodes = [node for node in network.nodes if node.is_output_node]
    if network.num_hidden_nodes > 0:

        for input_node in input_nodes:
            for hidden_node in hidden_nodes:
                graph.edge(str(input_node.identifier), str(hidden_node.identifier), _attributes=invisible_edge_attributes)

        for hidden_node in hidden_nodes:
            for output_node in output_nodes:
                graph.edge(str(hidden_node.identifier), str(output_node.identifier), _attributes=invisible_edge_attributes)
    else:
        for input_node in input_nodes:
            for output_node in output_nodes:
                graph.edge(str(input_node.identifier), str(output_node.identifier), _attributes=invisible_edge_attributes)

    graph.subgraph(input_node_subgraph)
    graph.subgraph(hidden_node_subgraph)
    graph.subgraph(output_node_subgraph)

    graph.render(view=True, filename=filename)
