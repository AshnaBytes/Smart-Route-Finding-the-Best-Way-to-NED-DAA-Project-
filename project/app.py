from flask import Flask, render_template, request, jsonify
import algorithms  # Import your algorithms from algorithm.py
import networkx as nx
import random
import webbrowser
from threading import Timer
import os

app = Flask(__name__, template_folder='templates')

# Store your algorithm functions in a dictionary
algo_functions = {
    'BFS': algorithms.bfs,
    'DFS': algorithms.dfs,
    'Dijkstra': algorithms.dijkstra,
    'A*': algorithms.a_star
}

# Route for daa.html
@app.route('/')
def daa():
    return render_template('daa.html')

# Route for about.html
@app.route('/about')
def about():
    return render_template('about.html')

# Route for project.html
@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/run_algorithm', methods=['POST'])
def run_algorithm():
    data = request.json
    start = data.get('start')
    goal = data.get('goal')
    multi_sources = data.get('multi_sources', [])

    if not start or not goal:
        return jsonify({'error': 'Invalid input, missing start or goal'}), 400

    # Ensure that graph and algorithm-related elements are properly initialized
    if not hasattr(algorithms, 'G'):
        return jsonify({'error': 'Graph not initialized. Please check the setup.'}), 500

    # Prepare the results for all algorithms
    results = []
    for algo_name, algo_function in algo_functions.items():
        # Run the algorithm to get the path and total time
        path, total_time = algo_function(start, goal)
        
        # Check for alternate paths and times if applicable
        alt_path, alt_time = algorithms.find_alternate_path_if_needed(path, algo_function, start, goal)
        
         # Visualize the path for this algorithm
        path_image_path = algorithms.visualize_path(path, algo_name, total_time, alt_path, alt_time)
         # Collect the result with the image path

        image_url = f"/static/algos/{os.path.basename(path_image_path)}"

        # Collecting the results for each algorithm
        results.append({
            'algorithm': algo_name,
            'graph': image_url,
            'path': path,
            'total_time': total_time,
            'alt_path': alt_path,
            'alt_time': alt_time,
            'path_image': path_image_path.split('/')[-1] 

        })

    # Optional multi-source visualization (if multi_sources are provided)
    multi_graph_path = None
    if multi_sources:
        multi_graph_path = algorithms.visualize_multi_source_graph(multi_sources, goal)

    # Return the results in JSON format with the multi-source graph if available
    return jsonify({
        'results': results,
        'multi_source_graph': f"/static/algos/{multi_graph_path.split('/')[-1]}" if multi_graph_path else None
    })

# Optional multi-source input for multi-source graph (if provided in the request)
@app.route('/multi_source_graph', methods=['POST'])
def multi_source_graph():
    data = request.json
    multi_sources = data.get('multi_sources')  # List of starting points from the frontend
    goal = data.get('goal')                    # Goal location

    if multi_sources and goal in algorithms.G.nodes:
        multi_graph_path = algorithms.visualize_multi_source_graph(multi_sources, goal)
        return jsonify({
            'message': 'Multi-source graph visualized successfully',
            'path': f"/static/algos/{multi_graph_path.split('/')[-1]}"
        })

    return jsonify({'error': 'Invalid sources or goal!'}), 400

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

if __name__ == '__main__':
    Timer(1, lambda: webbrowser.open('http://127.0.0.1:5001/')).start()
    app.run(debug=True, port=5001, use_reloader=False)
