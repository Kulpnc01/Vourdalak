"""
EgoWeaver 2.0 Core Engine
Exposes the spatial, physiological, and psychological processing units.
"""

# Import from timeline.py
from .timeline import build_index, get_closest_coordinate, export_lean_records

# Import from health.py 
# We alias this so it doesn't collide with the timeline version
from .health import build_health_index, get_closest_health_metrics, export_health_records 

# Import from filter.py
from .filter import evaluate_psych_signal