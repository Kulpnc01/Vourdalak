from flask import Flask, request, jsonify
from core.database import GraphDB

app = Flask(__name__)
db = GraphDB()

@app.route('/api/v3/hunt', methods=['POST'])
def start_hunt():
    data = request.json
    # Launch async hunt task...
    return jsonify({"status": "initiated", "target": data.get("target")})

@app.route('/api/v3/graph/<node_id>', methods=['GET'])
def get_node(node_id):
    # Fetch from DB...
    return jsonify({"id": node_id, "data": {}})

if __name__ == "__main__":
    app.run(port=5000)
