import yaml  # Import YAML module to read the economic hierarchy data
from graphviz import Digraph  # Import Graphviz to generate the hierarchy diagram
from hashlib import md5  # Import hashlib for generating unique IDs for nodes
from IPython.display import display  # Import display function to show the image in Jupyter/IPython environments
from PIL import Image  # Import PIL (Pillow) to open and display the image

# Load the economic hierarchy YAML file
with open("economic_hierarchy.yaml", "r") as file:
    data = yaml.safe_load(file)  # Parse the YAML file into a Python dictionary

# Create a Graphviz Digraph with a left-to-right layout (instead of top-down)
dot = Digraph(format="png", engine="dot")
dot.attr(rankdir="LR", nodesep="0.3", ranksep="1.2", splines="ortho")  
# rankdir="LR" → Ensures the hierarchy extends horizontally (Left to Right)
# nodesep="0.3" → Reduces horizontal spacing between nodes
# ranksep="1.2" → Increases vertical spacing between layers
# splines="ortho" → Uses orthogonal edges for better clarity

# Function to generate a unique internal ID for each node
def unique_id(name, parent_label, depth):
    """Generates a unique hash-based ID for each node to prevent merging issues."""
    return md5((parent_label + name + str(depth)).encode()).hexdigest()[:8]  # Short hash for uniqueness

# Function to recursively add nodes to the hierarchy
def add_nodes(dot, parent_id, parent_label, data, depth=0):
    """Recursively adds nodes to the Graphviz hierarchy."""
    if isinstance(data, dict):  # If the data is a dictionary (i.e., it has nested categories)
        for key, value in data.items():  # Loop through each key (category name)
            node_id = unique_id(key, parent_id, depth)  # Generate a unique internal ID for the node
            dot.node(node_id, key, shape="box")  # Create a node with a box shape
            dot.edge(parent_id, node_id)  # Connect the node to its parent
            add_nodes(dot, node_id, key, value, depth + 1)  # Recursively add child nodes

    elif isinstance(data, list):  # If the data is a list (i.e., it contains terminal values)
        for item in data:  # Loop through each item in the list
            node_id = unique_id(item, parent_id, depth)  # Generate a unique ID for each list item
            dot.node(node_id, item, shape="ellipse")  # Create a node with an ellipse shape for terminal values
            dot.edge(parent_id, node_id)  # Connect the terminal node to its parent

# Create the root node with a distinct shape and color
root_id = unique_id("Economic Activity", "root", 0)  # Generate a unique ID for the root node
dot.node(root_id, "Economic Activity", shape="doubleoctagon", style="filled", fillcolor="lightblue")  
# shape="doubleoctagon" → Makes the root node visually distinct
# style="filled", fillcolor="lightblue" → Colors the root node for emphasis

# Add children nodes recursively starting from the root node
add_nodes(dot, root_id, "Economic Activity", data["Economic Activity"])

# Save and render the hierarchy as a PNG image
dot.render("Economic_Hierarchy_Graphic", format="png")
print("Hierarchy image saved as 'Economic_Hierarchy_Graphic.png'")  # Print confirmation message

# Open and display the generated hierarchy image
image = Image.open("Economic_Hierarchy_Graphic.png")
display(image)  # Display the image in Jupyter/IPython notebooks
