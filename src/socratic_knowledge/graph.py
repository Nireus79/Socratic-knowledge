"""Knowledge graph integration for semantic relationships and traversal."""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class RelationshipType(str, Enum):
    """Types of relationships between knowledge items."""

    REFERENCES = "references"  # Item A mentions/references item B
    DEPENDS_ON = "depends_on"  # Item A requires understanding of item B
    RELATED_TO = "related_to"  # Items are conceptually related
    PREREQUISITE = "prerequisite"  # Item B must be learned before item A
    EXTENDS = "extends"  # Item A extends/builds on item B
    CONTRADICTS = "contradicts"  # Items present conflicting information
    SIMILAR_TO = "similar_to"  # Items cover similar topics


@dataclass
class KnowledgeEdge:
    """Edge connecting two knowledge items in the graph."""

    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float = 1.0  # Strength of relationship (0-1)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "weight": self.weight,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class GraphPath:
    """Path through the knowledge graph."""

    node_ids: List[str]
    edges: List[KnowledgeEdge]
    total_weight: float = 0.0

    def __len__(self) -> int:
        """Get path length in edges."""
        return len(self.edges)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_ids": self.node_ids,
            "edges": [e.to_dict() for e in self.edges],
            "total_weight": self.total_weight,
            "length": len(self),
        }


class KnowledgeGraph:
    """Graph-based representation of knowledge item relationships."""

    def __init__(self):
        """Initialize knowledge graph."""
        self.edges: List[KnowledgeEdge] = []
        self.node_index: Dict[str, List[KnowledgeEdge]] = {}
        self.reverse_index: Dict[str, List[KnowledgeEdge]] = {}
        self.logger = logging.getLogger(__name__)

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: str = "",
    ) -> KnowledgeEdge:
        """
        Add an edge between two knowledge items.

        Args:
            source_id: ID of source item
            target_id: ID of target item
            relationship_type: Type of relationship
            weight: Relationship strength (0-1)
            metadata: Optional metadata
            created_at: Creation timestamp

        Returns:
            The created edge
        """
        if not 0 <= weight <= 1:
            raise ValueError("Weight must be between 0 and 1")

        edge = KnowledgeEdge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            weight=weight,
            metadata=metadata or {},
            created_at=created_at,
        )

        self.edges.append(edge)

        # Update forward index
        if source_id not in self.node_index:
            self.node_index[source_id] = []
        self.node_index[source_id].append(edge)

        # Update reverse index
        if target_id not in self.reverse_index:
            self.reverse_index[target_id] = []
        self.reverse_index[target_id].append(edge)

        self.logger.debug(
            f"Added edge: {source_id} -[{relationship_type.value}]-> {target_id}"
        )

        return edge

    def remove_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: Optional[RelationshipType] = None,
    ) -> int:
        """
        Remove edges between two nodes.

        Args:
            source_id: ID of source item
            target_id: ID of target item
            relationship_type: Optional type filter

        Returns:
            Number of edges removed
        """
        removed = 0

        self.edges = [
            e
            for e in self.edges
            if not (
                e.source_id == source_id
                and e.target_id == target_id
                and (relationship_type is None or e.relationship_type == relationship_type)
            )
        ]
        removed = len(self.edges)

        # Rebuild indices
        self._rebuild_indices()
        return removed

    def get_outgoing_edges(self, node_id: str) -> List[KnowledgeEdge]:
        """Get all edges going out from a node."""
        return self.node_index.get(node_id, [])

    def get_incoming_edges(self, node_id: str) -> List[KnowledgeEdge]:
        """Get all edges coming into a node."""
        return self.reverse_index.get(node_id, [])

    def get_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[RelationshipType] = None,
        direction: str = "both",
    ) -> List[str]:
        """
        Get neighboring nodes.

        Args:
            node_id: Node to get neighbors for
            relationship_type: Optional filter by relationship type
            direction: 'out', 'in', or 'both'

        Returns:
            List of neighboring node IDs
        """
        neighbors: Set[str] = set()

        if direction in ("out", "both"):
            for edge in self.get_outgoing_edges(node_id):
                if relationship_type is None or edge.relationship_type == relationship_type:
                    neighbors.add(edge.target_id)

        if direction in ("in", "both"):
            for edge in self.get_incoming_edges(node_id):
                if relationship_type is None or edge.relationship_type == relationship_type:
                    neighbors.add(edge.source_id)

        return list(neighbors)

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
        relationship_types: Optional[List[RelationshipType]] = None,
    ) -> Optional[GraphPath]:
        """
        Find shortest path between two nodes using BFS.

        Args:
            source_id: Starting node
            target_id: Destination node
            max_depth: Maximum path depth
            relationship_types: Optional filter by relationship types

        Returns:
            GraphPath if found, None otherwise
        """
        if source_id == target_id:
            return GraphPath(node_ids=[source_id], edges=[])

        # BFS
        queue = [(source_id, [], [])]  # (current_node, path_nodes, path_edges)
        visited = {source_id}
        depth = 0

        while queue and depth < max_depth:
            current_node, path_nodes, path_edges = queue.pop(0)

            for edge in self.get_outgoing_edges(current_node):
                if relationship_types and edge.relationship_type not in relationship_types:
                    continue

                next_node = edge.target_id

                if next_node == target_id:
                    # Found path
                    final_nodes = path_nodes + [current_node, target_id]
                    final_edges = path_edges + [edge]
                    total_weight = sum(e.weight for e in final_edges)
                    return GraphPath(
                        node_ids=final_nodes,
                        edges=final_edges,
                        total_weight=total_weight,
                    )

                if next_node not in visited:
                    visited.add(next_node)
                    queue.append(
                        (
                            next_node,
                            path_nodes + [current_node],
                            path_edges + [edge],
                        )
                    )

            depth += 1

        return None

    def find_related_items(
        self,
        node_id: str,
        depth: int = 2,
        relationship_types: Optional[List[RelationshipType]] = None,
    ) -> Dict[str, float]:
        """
        Find related items within specified depth.

        Args:
            node_id: Starting node
            depth: Maximum traversal depth
            relationship_types: Optional filter by relationship types

        Returns:
            Dictionary mapping node IDs to relevance scores
        """
        related: Dict[str, float] = {}
        visited = {node_id}
        current_level = {node_id: 1.0}

        for level in range(depth):
            next_level: Dict[str, float] = {}

            for current_node, current_score in current_level.items():
                # Get neighbors
                neighbors = self.get_neighbors(
                    current_node,
                    relationship_type=relationship_types[0] if relationship_types else None,
                )

                for neighbor in neighbors:
                    if neighbor not in visited:
                        # Calculate relevance score (decreases with distance)
                        relevance = current_score * (1.0 / (level + 2))
                        next_level[neighbor] = max(
                            next_level.get(neighbor, 0), relevance
                        )
                        visited.add(neighbor)
                        related[neighbor] = relevance

            current_level = next_level

        # Sort by relevance
        return dict(sorted(related.items(), key=lambda x: x[1], reverse=True))

    def get_all_nodes(self) -> Set[str]:
        """Get all unique node IDs in the graph."""
        nodes: Set[str] = set()

        for edge in self.edges:
            nodes.add(edge.source_id)
            nodes.add(edge.target_id)

        return nodes

    def get_node_degree(self, node_id: str) -> Tuple[int, int, int]:
        """
        Get degree information for a node.

        Returns:
            Tuple of (in_degree, out_degree, total_degree)
        """
        in_degree = len(self.get_incoming_edges(node_id))
        out_degree = len(self.get_outgoing_edges(node_id))
        return (in_degree, out_degree, in_degree + out_degree)

    def get_hub_nodes(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most connected nodes (hubs).

        Args:
            top_n: Number of nodes to return

        Returns:
            List of (node_id, degree) tuples
        """
        node_degrees = []

        for node_id in self.get_all_nodes():
            _, _, total_degree = self.get_node_degree(node_id)
            node_degrees.append((node_id, total_degree))

        return sorted(node_degrees, key=lambda x: x[1], reverse=True)[:top_n]

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            "nodes": list(self.get_all_nodes()),
            "edges": [e.to_dict() for e in self.edges],
            "node_count": len(self.get_all_nodes()),
            "edge_count": len(self.edges),
        }

    def export_as_cypher(self) -> str:
        """
        Export graph as Neo4j Cypher queries.

        Returns:
            String of Cypher CREATE statements
        """
        lines = []

        # Create unique nodes
        nodes = self.get_all_nodes()
        for node_id in nodes:
            lines.append(f'CREATE (n_{node_id} {{id: "{node_id}"}})')

        # Create relationships
        for edge in self.edges:
            lines.append(
                f'CREATE (n_{edge.source_id})-'
                f'[:{edge.relationship_type.value.upper()} {{weight: {edge.weight}}}]->'
                f'(n_{edge.target_id})'
            )

        return ";\n".join(lines) + ";"

    def _rebuild_indices(self) -> None:
        """Rebuild node indices after modification."""
        self.node_index = {}
        self.reverse_index = {}

        for edge in self.edges:
            if edge.source_id not in self.node_index:
                self.node_index[edge.source_id] = []
            self.node_index[edge.source_id].append(edge)

            if edge.target_id not in self.reverse_index:
                self.reverse_index[edge.target_id] = []
            self.reverse_index[edge.target_id].append(edge)
