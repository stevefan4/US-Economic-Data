import yaml
from graphviz import Digraph
from hashlib import md5
from IPython.display import display
from PIL import Image

# Load the YAML file
with open("economic_hierarchy.yaml", "r") as file:
    data = yaml.safe_load(file)

# Create a Graphviz Digraph with a top-down layout
dot = Digraph(format="png", engine="dot")
dot.attr(rankdir="TB", nodesep="0.5", ranksep="0.75")  # Top to bottom layout with better spacing

# Function to generate a unique ID for nodes to prevent duplicates
def unique_id(name):
    return md5(name.encode()).hexdigest()[:6]  # Short hash for uniqueness

# Function to recursively add nodes
def add_nodes(dot, parent_id, parent_label, data):
    if isinstance(data, dict):
        for key, value in data.items():
            node_id = unique_id(parent_label + key)  # Create a unique ID
            dot.node(node_id, key)  # Add node
            dot.edge(parent_id, node_id)  # Connect with parent
            add_nodes(dot, node_id, key, value)  # Recursively process children
    elif isinstance(data, list):
        for item in data:
            node_id = unique_id(parent_label + item)  # Unique ID
            dot.node(node_id, item)
            dot.edge(parent_id, node_id)

# Root node
root_id = unique_id("Economic Activity")
dot.node(root_id, "Economic Activity")

# Add children nodes
add_nodes(dot, root_id, "Economic Activity", data["Economic Activity"])

# Save and render the image
dot.render("economic_hierarchy", format="png")
print("Hierarchy image saved as 'economic_hierarchy.png'")

# Display the image
image = Image.open("economic_hierarchy.png")
display(image)
