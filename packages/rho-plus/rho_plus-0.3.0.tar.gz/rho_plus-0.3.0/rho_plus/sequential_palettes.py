#!/usr/bin/env python3
"""Reads a core set of sequential color scales."""

from importlib.resources import open_text
import json
from matplotlib.colors import LinearSegmentedColormap

SEQUENTIAL = json.load(open_text("rho_plus.data", "sequential_palettes.json"))

for name, colors in SEQUENTIAL.items():
    globals()[name] = colors
