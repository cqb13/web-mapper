import networkx as nx
import json
import webview
import os

def generate_d3_graph(data):
    graph = nx.DiGraph()
    add_nodes_edges(graph, data)

    nodes = [{"id": node} for node in graph.nodes]
    links = [{"source": source, "target": target} for source, target in graph.edges]

    d3_code = """
    <script src="https://d3js.org/d3.v5.min.js"></script>
    <div>
        <label for="search">Search:</label>
        <input type="text" id="search" oninput="filterNodes()" placeholder="Enter node name">
    </div>
    <svg id="graph-svg"></svg>
    <script>
        var allNodes = %s;
        var links = %s;

        var width = window.innerWidth;
        var height = window.innerHeight;

        var svg = d3.select('#graph-svg')
            .attr('width', width)
            .attr('height', height);

        var zoom = d3.zoom()
            .scaleExtent([0.1, 1])
            .on('zoom', function() {
                svg.attr('transform', d3.event.transform);
            });

        svg.call(zoom);

        var simulation = d3.forceSimulation(allNodes)
            .force('link', d3.forceLink(links).id(function(d) { return d.id; }).distance(150).strength(0.2))
            .force('charge', d3.forceManyBody().strength(-300))  // Adjust the strength here
            .force('center', d3.forceCenter(width / 2, height / 2));

        var link = svg.selectAll('line')
            .data(links)
            .enter().append('line')
            .style('stroke', '#aaa')  // Adjust line color
            .style('stroke-width', 1);  // Adjust line width

        var node = svg.selectAll('g')
            .data(allNodes)
            .enter().append('g')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));

        // Append circles for nodes
        node.append('circle')
            .attr('r', 8)  // Adjust node radius
            .style('fill', '#69b3a2');  // Adjust node color

        // Append text labels for nodes
        node.append('text')
            .attr('dx', 12)
            .attr('dy', '.35em')
            .text(function(d) { return d.id; });

        simulation.on('tick', function() {
            link
                .attr('x1', function(d) { return d.source.x; })
                .attr('y1', function(d) { return d.source.y; })
                .attr('x2', function(d) { return d.target.x; })
                .attr('y2', function(d) { return d.target.y; });

            // Update the positions of circles and text labels
            node
                .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; });
        });

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
function filterNodes() {
    var searchTerm = document.getElementById('search').value.toLowerCase();
    var filteredNodes = allNodes.filter(function(node) {
        return node.id.toLowerCase().includes(searchTerm);
    });

    node = svg.selectAll('g')
        .data(filteredNodes, function(d) { return d.id; });

    node.exit().remove();
    node = node.enter().append('g')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .merge(node);

    // Update or append circles for nodes
    node.selectAll('circle')
        .attr('r', 8)
        .style('fill', '#69b3a2');

    // Update or append text labels for nodes
    var text = node.selectAll('text')
        .data(function(d) { return [d]; });  // Use an array to bind data to a single element

    text.exit().remove();
    text = text.enter().append('text')
        .attr('dx', 12)
        .attr('dy', '.35em')
        .merge(text)
        .text(function(d) { return d.id; })
        .style('display', function(d) {
            return d.id.toLowerCase().includes(searchTerm) ? 'block' : 'none';
        });

    simulation.nodes(filteredNodes);
    simulation.alpha(1).restart();
}


    </script>
    """ % (json.dumps(nodes), json.dumps(links))

    with open("dist/graph.html", "w") as f:
        f.write(d3_code)
        
def add_nodes_edges(graph, data, parent=None):
    url = data["url"]
    graph.add_node(url)

    if parent is not None:
        graph.add_edge(parent, url)

    if "children" in data:
        for child in data["children"]:
            add_nodes_edges(graph, child, url)

def view():
    with open("dist/map.json", "r") as f:
        json_data = json.load(f)
        json_data = json_data[0]

    generate_d3_graph(json_data)

    html_file_path = os.path.abspath("dist/graph.html")

    webview.create_window(
        "Graph Viewer", url=f"file:///{html_file_path}", width=1800, height=1200
    )
    webview.start()
