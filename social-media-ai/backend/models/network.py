from typing import Dict, Any, List
import networkx as nx

class SocialGraphAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, posts: List[Dict[str, Any]], users: List[Dict[str, Any]] = None):
        """Constructs a directed NetworkX graph from posts and replies"""
        self.graph.clear()

        # Add user nodes
        if users:
            for u in users:
                self.graph.add_node(
                    u["id"],
                    label=u.get("username", u["id"]),
                    handle=u.get("handle", f"@{u['id']}"),
                    platform=u.get("platform", "twitter"),
                    followers=u.get("followers", 100),
                    node_type="user",
                    community=1
                )

        # Add post links and parent replies
        for p in posts:
            uid = p.get("user_id") or "usr_unknown"
            if not self.graph.has_node(uid):
                self.graph.add_node(
                    uid,
                    label=p.get("user_name", uid),
                    handle=p.get("handle", f"@{uid}"),
                    platform=p.get("platform", "twitter"),
                    followers=p.get("user_followers", 500),
                    node_type="user",
                    community=1
                )

            # Reply or Repost Edge
            parent_id = p.get("parent_post_id")
            if parent_id:
                # Find author of parent post
                parent_post = next((item for item in posts if item["id"] == parent_id), None)
                if parent_post:
                    parent_author = parent_post.get("user_id", "usr_unknown")
                    if not self.graph.has_node(parent_author):
                        self.graph.add_node(
                            parent_author,
                            label=parent_post.get("user_name", parent_author),
                            handle=parent_post.get("handle", f"@{parent_author}"),
                            platform=parent_post.get("platform", "twitter"),
                            followers=parent_post.get("user_followers", 1000),
                            node_type="user",
                            community=1
                        )
                    # Add directed edge from replier to original author
                    self.graph.add_edge(uid, parent_author, relation="reply", weight=1.8)

            # Mentions edges
            mentions = p.get("mentions", [])
            for m in mentions:
                target_node = f"usr_{m}"
                if not self.graph.has_node(target_node):
                    self.graph.add_node(
                        target_node,
                        label=f"@{m}",
                        handle=f"@{m}",
                        platform=p.get("platform", "twitter"),
                        followers=2000,
                        node_type="user",
                        community=2
                    )
                self.graph.add_edge(uid, target_node, relation="mention", weight=1.2)

        # Community clustering using Louvain or greedy modularity if undirected
        try:
            undirected = self.graph.to_undirected()
            communities = nx.community.greedy_modularity_communities(undirected)
            for comm_id, comm_nodes in enumerate(communities, start=1):
                for node in comm_nodes:
                    if self.graph.has_node(node):
                        self.graph.nodes[node]["community"] = comm_id
        except Exception:
            pass

    def compute_metrics(self) -> Dict[str, Any]:
        """Calculates PageRank, degree centrality, betweenness centrality"""
        if len(self.graph.nodes) == 0:
            return {"pagerank": {}, "betweenness": {}, "top_influencers": []}

        try:
            pagerank = nx.pagerank(self.graph, weight="weight")
        except Exception:
            pagerank = {n: 0.1 for n in self.graph.nodes}

        try:
            betweenness = nx.betweenness_centrality(self.graph)
        except Exception:
            betweenness = {n: 0.05 for n in self.graph.nodes}

        # Rank top influencers
        influencers = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:6]
        top_list = []
        for node_id, pr in influencers:
            ndata = self.graph.nodes.get(node_id, {})
            top_list.append({
                "id": node_id,
                "label": ndata.get("label", node_id),
                "handle": ndata.get("handle", f"@{node_id}"),
                "platform": ndata.get("platform", "twitter"),
                "pagerank": round(pr, 4),
                "betweenness": round(betweenness.get(node_id, 0.0), 4),
                "followers": ndata.get("followers", 0)
            })

        return {
            "pagerank": pagerank,
            "betweenness": betweenness,
            "top_influencers": top_list
        }

    def export_visualization_data(self) -> Dict[str, Any]:
        """Exports nodes and links in standard D3 / Vis.js / Canvas force-graph format"""
        metrics = self.compute_metrics()
        pagerank = metrics["pagerank"]
        betweenness = metrics["betweenness"]

        nodes = []
        for n in self.graph.nodes:
            data = self.graph.nodes[n]
            pr = pagerank.get(n, 0.05)
            nodes.append({
                "id": n,
                "label": data.get("label", n),
                "handle": data.get("handle", f"@{n}"),
                "platform": data.get("platform", "twitter"),
                "group": data.get("community", 1),
                "radius": max(8, min(28, int(pr * 180 + 10))),
                "pagerank": round(pr, 4),
                "betweenness": round(betweenness.get(n, 0.0), 4),
                "followers": data.get("followers", 0)
            })

        links = []
        for u, v, data in self.graph.edges(data=True):
            links.append({
                "source": u,
                "target": v,
                "relation": data.get("relation", "link"),
                "weight": data.get("weight", 1.0)
            })

        return {
            "nodes": nodes,
            "links": links,
            "total_nodes": len(nodes),
            "total_edges": len(links),
            "top_influencers": metrics["top_influencers"]
        }

network_model = SocialGraphAnalyzer()
