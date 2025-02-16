import yaml
from graphviz import Digraph
from hashlib import md5
from IPython.display import display
from PIL import Image

# Load the YAML file
with open("economic_hierarchy.yaml", "r") as file:
    data = yaml.safe_load(file)

# Create a Graphviz Digraph with a left-to-right layout (taller instead of wide)
dot = Digraph(format="png", engine="dot")
dot.attr(rankdir="LR", nodesep="0.3", ranksep="1.2", splines="ortho")  # Adjust layout to be taller

# Function to generate a unique ID for nodes to prevent duplicates
def unique_id(name, parent_label):
    return md5((parent_label + name).encode()).hexdigest()[:6]  # Short hash for uniqueness

# Function to recursively add nodes
def add_nodes(dot, parent_id, parent_label, data, depth=0):
    if isinstance(data, dict):
        for key, value in data.items():
            node_id = unique_id(key, parent_label)  # Generate a unique node ID
            dot.node(node_id, key, shape="box")  # Box shape for better readability
            dot.edge(parent_id, node_id)  # Connect with parent
            add_nodes(dot, node_id, key, value, depth + 1)  # Recursively process children
    elif isinstance(data, list):
        for item in data:
            node_id = unique_id(item, parent_label)  # Unique ID
            dot.node(node_id, item, shape="ellipse")  # Use different shapes for differentiation
            dot.edge(parent_id, node_id)

# Root node
root_id = unique_id("Economic Activity", "root")
dot.node(root_id, "Economic Activity", shape="doubleoctagon", style="filled", fillcolor="lightblue")

# Add children nodes
add_nodes(dot, root_id, "Economic Activity", data["Economic Activity"])

# Save and render the image
dot.render("economic_hierarchy", format="png")
print("Hierarchy image saved as 'economic_hierarchy.png'")

# Display the image
image = Image.open("Economic Hierarchy Visual.png")
display(image)
