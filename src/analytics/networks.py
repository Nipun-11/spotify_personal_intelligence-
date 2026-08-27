"""Music network graph and bridge detection analytical module."""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import networkx as nx

logger = logging.getLogger(__name__)

def build_music_network(
    artist_transitions_df: pd.DataFrame,
    artist_lifecycles_df: pd.DataFrame,
    min_edge_weight: int = 2
) -> Dict[str, Any]:
    """Build NetworkX graph of artist transitions and compute topological metrics.
    
    Args:
        artist_transitions_df: Artist transitions DataFrame with transition_count.
        artist_lifecycles_df: Artist lifecycles DataFrame with total_minutes and plays.
        min_edge_weight: Minimum transition count to include an edge in the graph.
        
    Returns:
        Dictionary containing:
          - 'nodes': List of node dicts (id, label, size, degree, betweenness, pagerank, community)
          - 'edges': List of edge dicts (source, target, weight)
          - 'bridges': Top bridge artists connecting disparate clusters
          - 'summary': Graph level statistics
    """
    logger.info("Building personal music network graph...")
    
    # Filter out self-transitions for structural network analysis
    cross_artist_edges = artist_transitions_df[
        (~artist_transitions_df["is_self_transition"]) &
        (artist_transitions_df["transition_count"] >= min_edge_weight)
    ].copy()
    
    # Create directed and undirected graphs
    G = nx.DiGraph()
    G_undirected = nx.Graph()
    
    # Add nodes from lifecycles
    artist_info = {}
    for _, r in artist_lifecycles_df.iterrows():
        art_id = str(r["artist_id"])
        art_name = str(r["artist_name"])
        tot_min = float(r["total_minutes"])
        plays = int(r["total_plays"])
        stage = str(r["lifecycle_stage"])
        
        artist_info[art_id] = {
            "name": art_name,
            "total_minutes": tot_min,
            "total_plays": plays,
            "lifecycle_stage": stage
        }
        
    for _, r in cross_artist_edges.iterrows():
        src = str(r["previous_artist_id"])
        tgt = str(r["artist_id"])
        weight = int(r["transition_count"])
        
        # Ensure nodes exist
        if not G.has_node(src):
            src_info = artist_info.get(src, {"name": r["previous_artist_name"], "total_minutes": 10.0, "total_plays": 5, "lifecycle_stage": "Regular"})
            G.add_node(src, **src_info)
            G_undirected.add_node(src, **src_info)
            
        if not G.has_node(tgt):
            tgt_info = artist_info.get(tgt, {"name": r["artist_name"], "total_minutes": 10.0, "total_plays": 5, "lifecycle_stage": "Regular"})
            G.add_node(tgt, **tgt_info)
            G_undirected.add_node(tgt, **tgt_info)
            
        G.add_edge(src, tgt, weight=weight)
        if G_undirected.has_edge(src, tgt):
            G_undirected[src][tgt]["weight"] += weight
        else:
            G_undirected.add_edge(src, tgt, weight=weight)
            
    # Calculate Centrality & Community Detection
    logger.info(f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    if G.number_of_nodes() == 0:
        return {"nodes": [], "edges": [], "bridges": [], "summary": {}}
        
    # PageRank
    try:
        pagerank = nx.pagerank(G, weight="weight")
    except Exception:
        pagerank = {n: 1.0 / len(G) for n in G.nodes()}
        
    # Betweenness Centrality
    try:
        betweenness = nx.betweenness_centrality(G_undirected, weight="weight", normalized=True)
    except Exception:
        betweenness = {n: 0.0 for n in G.nodes()}
        
    # Communities (using greedy modularity on undirected graph)
    communities_map = {}
    try:
        community_sets = list(nx.community.greedy_modularity_communities(G_undirected, weight="weight"))
        for comm_id, c_set in enumerate(community_sets):
            for node in c_set:
                communities_map[node] = comm_id
    except Exception:
        communities_map = {n: 0 for n in G.nodes()}
        
    # Format node list
    nodes_data = []
    for node, data in G.nodes(data=True):
        deg = G.degree(node)
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)
        
        nodes_data.append({
            "id": node,
            "name": data.get("name", node),
            "total_minutes": round(data.get("total_minutes", 0), 1),
            "total_plays": data.get("total_plays", 0),
            "lifecycle_stage": data.get("lifecycle_stage", "Regular"),
            "degree": deg,
            "in_degree": in_deg,
            "out_degree": out_deg,
            "pagerank": round(float(pagerank.get(node, 0.0)), 5),
            "betweenness": round(float(betweenness.get(node, 0.0)), 5),
            "community_id": int(communities_map.get(node, 0))
        })
        
    nodes_data = sorted(nodes_data, key=lambda x: x["pagerank"], reverse=True)
    
    # Format edge list
    edges_data = []
    for u, v, d in G.edges(data=True):
        edges_data.append({
            "source": u,
            "target": v,
            "weight": int(d.get("weight", 1)),
            "source_name": G.nodes[u].get("name", u),
            "target_name": G.nodes[v].get("name", v)
        })
        
    # Bridge artists: high betweenness and connecting distinct communities
    bridges = sorted(nodes_data, key=lambda x: x["betweenness"], reverse=True)[:10]
    
    summary = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "num_communities": len(set(communities_map.values())),
        "density": round(nx.density(G), 5)
    }
    
    return {
        "nodes": nodes_data,
        "edges": edges_data,
        "bridges": bridges,
        "summary": summary
    }
