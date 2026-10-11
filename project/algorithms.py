import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for headless environments (e.g., Flask, Django)
import matplotlib.pyplot as plt
import heapq
import random
import os
import re

# ----------------- GRAPH SETUP -----------------
graph = {
    'North Karachi': {'North Nazimabad': (7, 0.2), 'Water Pump': (5, 0.5), 'Gulshan': (9, 0.3),
                      'NED Main Gate': (12, 0.4), 'NED Maskan Gate': (12, 0.4),
                      'NED Staff Gate': (12, 0.4), 'NED Visitors Gate': (12, 0.4)},
    'North Nazimabad': {'Water Pump': (3, 0.3), 'Gulshan': (6, 0.6),
                        'NED Main Gate': (10, 0.4), 'NED Maskan Gate': (10, 0.4),
                        'NED Staff Gate': (10, 0.4), 'NED Visitors Gate': (10, 0.4)},
    'Water Pump': {'Gulshan': (4, 0.4), 'NED Main Gate': (6, 0.5),
                   'NED Maskan Gate': (6, 0.5), 'NED Staff Gate': (6, 0.5),
                   'NED Visitors Gate': (6, 0.5)},
    'Gulshan': {'NED Main Gate': (3, 0.3), 'NED Maskan Gate': (2, 0.3),
                'NED Staff Gate': (2, 0.3), 'NED Visitors Gate': (2, 0.3)},
}

# ----------------- CONGESTION & TIME -----------------
def simulate_live_congestion():
    for source in graph:
        for dest in graph[source]:
            distance = graph[source][dest][0]
            graph[source][dest] = (distance, round(random.uniform(0.1, 0.8), 2))

# Function to update travel time considering congestion
def update_travel_time(distance, congestion):
    return round((distance / 30) * 60 * (1 + congestion), 2)

# Build the graph
G = nx.Graph()
for source, destinations in graph.items():
    for dest, (distance, congestion) in destinations.items():
        time = update_travel_time(distance, congestion)
        G.add_edge(source, dest, weight=time)

# Algorithms
def bfs(start, goal):
    queue = [(start, [start], 0)]
    visited = set()
    while queue:
        vertex, path, cost = queue.pop(0)
        if vertex == goal:
            return path, cost
        visited.add(vertex)
        for neighbor in graph.get(vertex, {}):
            if neighbor not in visited:
                distance, congestion = graph[vertex][neighbor]
                travel_time = update_travel_time(distance, congestion)
                queue.append((neighbor, path + [neighbor], cost + travel_time))
    return None, float('inf')

def dfs(start, goal):
    stack = [(start, [start], 0)]
    visited = set()
    while stack:
        vertex, path, cost = stack.pop()
        if vertex == goal:
            return path, cost
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in graph.get(vertex, {}):
                if neighbor not in visited:
                    distance, congestion = graph[vertex][neighbor]
                    travel_time = update_travel_time(distance, congestion)
                    stack.append((neighbor, path + [neighbor], cost + travel_time))
    return None, float('inf')

def dijkstra(start, goal):
    queue = [(0, start, [start])]
    visited = set()
    while queue:
        cost, vertex, path = heapq.heappop(queue)
        if vertex == goal:
            return path, cost
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in graph.get(vertex, {}):
                if neighbor not in visited:
                    distance, congestion = graph[vertex][neighbor]
                    travel_time = update_travel_time(distance, congestion)
                    heapq.heappush(queue, (cost + travel_time, neighbor, path + [neighbor]))
    return None, float('inf')

def heuristic(node, goal):
    return 0

def a_star(start, goal):
    queue = [(0 + heuristic(start, goal), 0, start, [start])]
    visited = set()
    while queue:
        est_total, cost, vertex, path = heapq.heappop(queue)
        if vertex == goal:
            return path, cost
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in graph.get(vertex, {}):
                if neighbor not in visited:
                    distance, congestion = graph[vertex][neighbor]
                    travel_time = update_travel_time(distance, congestion)
                    est = cost + travel_time + heuristic(neighbor, goal)
                    heapq.heappush(queue, (est, cost + travel_time, neighbor, path + [neighbor]))
    return None, float('inf')

# Visualizations
def visualize_graph():
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.1f}" for k, v in labels.items()})
    plt.title("Graph Visualization")

    # Save graph as PNG in static folder
    os.makedirs("static/algos", exist_ok=True)
    file_path = "static/algos/graph_visualization.png"
    plt.savefig(file_path)
    plt.close()
    return file_path

def visualize_path(path, algo_name, total_time, alt_path=None, alt_time=None):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2500, font_size=12)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.1f}" for k, v in labels.items()})
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='orange', node_size=3000)

    if alt_path:
        nx.draw_networkx_nodes(G, pos, nodelist=alt_path, node_color='red', node_size=2000, alpha=0.6)
        edges_in_alt = list(zip(alt_path, alt_path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges_in_alt, width=2, edge_color='red', style='dashed')

    plt.title(f"{algo_name} Path: {path} | Time: {total_time} min"
              + (f"\nAlternate Path: {alt_path} | Time: {alt_time} min" if alt_path else ""))
    
       
    safe_algo_name = re.sub(r'[^a-zA-Z0-9_-]', '_', algo_name)  # replaces anything not a-z, A-Z, 0-9, _ or -
    filename = f"{safe_algo_name}.png"

    # Save path visualization as PNG in static folder
    os.makedirs("static/algos", exist_ok=True)
    file_path = f"static/algos/{safe_algo_name}.png"
    plt.savefig(file_path)
    plt.close()
    return file_path

# Function to find an alternate path if congestion is high
def find_alternate_path_if_needed(path, algo_func, start, goal):
    congested = False
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        congestion = graph[u][v][1]
        if congestion > 0.4:
            congested = True
            break
    if congested:
        print("⚠️ High congestion detected! Searching for alternate path...")
        new_graph = {
            u: {v: (d, c) for v, (d, c) in dest.items() if c <= 0.4}
            for u, dest in graph.items()
        }
        path_alt, time_alt = dijkstra_custom(new_graph, start, goal)
        return path_alt, time_alt
    return None, None

# Dijkstra for custom graph considering congestion
def dijkstra_custom(custom_graph, start, goal):
    queue = [(0, start, [start])]
    visited = set()
    while queue:
        cost, vertex, path = heapq.heappop(queue)
        if vertex == goal:
            return path, cost
        if vertex not in visited:
            visited.add(vertex)
            for neighbor in custom_graph.get(vertex, {}):
                if neighbor not in visited:
                    distance, congestion = custom_graph[vertex][neighbor]
                    travel_time = update_travel_time(distance, congestion)
                    heapq.heappush(queue, (cost + travel_time, neighbor, path + [neighbor]))
    return None, float('inf')

def visualize_multi_source_graph(sources, destination):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    node_colors = []
    for node in G.nodes:
        if node in sources:
            node_colors.append('lightgreen')
        elif node == destination:
            node_colors.append('red')
        else:
            node_colors.append('skyblue')

    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2500, font_size=11)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={k: f"{v:.1f}" for k, v in labels.items()})
    plt.title(f"Multi-Source Visualization\nSources: {', '.join(sources)} | Destination: {destination}")

    os.makedirs("static/algos", exist_ok=True)
    file_path = "static/algos/multi_source_graph.png"
    plt.savefig(file_path)
    plt.close()
    return file_path

# Flask-friendly function to process start, goal, and sources for multi-source
def process_paths(start, goal, sources_input=None):
    if start not in G.nodes or goal not in G.nodes:
        return "Invalid input! Please check the location names."
    
    results = []
    for algo_name, algo_func in [('BFS', bfs), ('DFS', dfs), ('Dijkstra', dijkstra), ('A*', a_star)]:
        path, total_time = algo_func(start, goal)
        alt_path, alt_time = find_alternate_path_if_needed(path, algo_func, start, goal)
        path_file = visualize_path(path, algo_name, total_time, alt_path, alt_time)
        results.append({
            'algorithm': algo_name,
            'path': path,
            'total_time': total_time,
            'alt_path': alt_path,
            'alt_time': alt_time,
            'path_image': path_file  # Include path image URL
        })
    
    if sources_input:
        multi_sources = [s.strip() for s in sources_input.split(',') if s.strip() in G.nodes]
        if start not in multi_sources:
            multi_sources.insert(0, start)
        if multi_sources:
            multi_source_file = visualize_multi_source_graph(multi_sources, goal)
            results.append({'multi_source_graph': multi_source_file})  # Include multi-source graph URL
    
    return results
