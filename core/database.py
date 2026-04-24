import sqlite3
import json
from datetime import datetime
from typing import List, Tuple
from .models import Node, Edge, NodeType, EdgeType

class GraphDB:
    def __init__(self, db_path: str = "vourdalak_v3.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(type, value)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    source_id TEXT,
                    target_id TEXT,
                    type TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    timestamp TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY(source_id) REFERENCES nodes(id),
                    FOREIGN KEY(target_id) REFERENCES nodes(id),
                    PRIMARY KEY(source_id, target_id, type)
                )
            """)
            conn.commit()

    def _get_node_id(self, node: Node) -> str:
        return f"{node.type.value}:{node.value}"

    def upsert_node(self, node: Node):
        node_id = self._get_node_id(node)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO nodes (id, type, value, metadata)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET metadata = excluded.metadata
            """, (node_id, node.type.value, node.value, json.dumps(node.metadata)))
            conn.commit()

    def upsert_edge(self, edge: Edge):
        source_id = self._get_node_id(edge.source)
        target_id = self._get_node_id(edge.target)
        self.upsert_node(edge.source)
        self.upsert_node(edge.target)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO edges (source_id, target_id, type, weight, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, target_id, type) DO UPDATE SET
                    weight = excluded.weight,
                    metadata = excluded.metadata
            """, (source_id, target_id, edge.type.value, edge.weight, 
                  edge.timestamp.isoformat(), json.dumps(edge.metadata)))
            conn.commit()
