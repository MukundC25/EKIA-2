"""Graph Service — Neo4j driver and query interface for GraphRAG."""
import os
from typing import Optional
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

load_dotenv()


class GraphService:
    """Service layer for all Neo4j graph operations."""

    def __init__(self):
        self._driver: Optional[Driver] = None

    def connect(self):
        """Initialize Neo4j driver connection."""
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        try:
            self._driver = GraphDatabase.driver(uri, auth=(username, password))
            self._driver.verify_connectivity()
            print(f"[GraphService] Connected to Neo4j at {uri}")
        except Exception as e:
            print(f"[GraphService] ⚠ Could not connect to Neo4j: {e}")
            print("[GraphService] Graph features will be unavailable. Start Neo4j Desktop to enable.")
            self._driver = None

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    @property
    def is_connected(self) -> bool:
        return self._driver is not None

    def search_errors(self, error_name: str, depth: int = 2) -> list[dict]:
        """GraphRAG traversal: find errors, causes, fixes, and related problems."""
        if not self._driver:
            return []

        query = """
        MATCH (e:Error)
        WHERE toLower(e.name) CONTAINS toLower($error_name)
           OR toLower(e.language) CONTAINS toLower($error_name)
        OPTIONAL MATCH (e)-[:CAUSED_BY]->(c:Concept)
        OPTIONAL MATCH (e)-[:FIXED_BY]->(f:Fix)
        OPTIONAL MATCH (c)-[:PRACTICED_BY]->(p:Problem)
        OPTIONAL MATCH (e)-[:RELATED_TO]->(rc:Concept)
        RETURN e, c, f, collect(distinct p.name) AS problems, collect(distinct rc.name) AS related_concepts
        LIMIT 5
        """

        try:
            database = os.getenv("NEO4J_DATABASE", "neo4j")
            with self._driver.session(database=database) as session:
                result = session.run(query, error_name=error_name)
                records = []
                for record in result:
                    entry = {}
                    if record["e"]:
                        entry["error"] = dict(record["e"])
                    if record["c"]:
                        entry["concept"] = dict(record["c"])
                    if record["f"]:
                        entry["fix"] = dict(record["f"])
                    entry["practice_problems"] = record["problems"]
                    entry["related_concepts"] = record["related_concepts"]
                    records.append(entry)
                return records
        except Exception as e:
            print(f"[GraphService] Query error: {e}")
            return []

    def get_full_graph(self, limit: int = 100) -> dict:
        """Retrieve nodes and edges for graph visualization."""
        if not self._driver:
            return {"nodes": [], "edges": []}

        query = """
        MATCH (n)-[r]->(m)
        RETURN n, type(r) AS rel_type, m
        LIMIT $limit
        """

        try:
            database = os.getenv("NEO4J_DATABASE", "neo4j")
            with self._driver.session(database=database) as session:
                result = session.run(query, limit=limit)
                nodes_map = {}
                edges = []

                for record in result:
                    n = record["n"]
                    n_id = str(n.element_id)
                    if n_id not in nodes_map:
                        labels = list(n.labels)
                        nodes_map[n_id] = {
                            "id": n_id,
                            "label": n.get("name") or n.get("id") or n.get("description", "")[:30],
                            "type": labels[0] if labels else "Unknown",
                            "properties": dict(n),
                        }

                    m = record["m"]
                    m_id = str(m.element_id)
                    if m_id not in nodes_map:
                        labels = list(m.labels)
                        nodes_map[m_id] = {
                            "id": m_id,
                            "label": m.get("name") or m.get("id") or m.get("description", "")[:30],
                            "type": labels[0] if labels else "Unknown",
                            "properties": dict(m),
                        }

                    edges.append({
                        "source": n_id,
                        "target": m_id,
                        "relationship": record["rel_type"],
                    })

                return {"nodes": list(nodes_map.values()), "edges": edges}
        except Exception as e:
            print(f"[GraphService] get_full_graph error: {e}")
            return {"nodes": [], "edges": []}

    def get_stats(self) -> dict:
        """Return node/relationship count stats."""
        if not self._driver:
            return {"connected": False}

        try:
            database = os.getenv("NEO4J_DATABASE", "neo4j")
            with self._driver.session(database=database) as session:
                counts = {}
                for label in ["Error", "Concept", "Fix", "Problem", "Language"]:
                    result = session.run(f"MATCH (n:{label}) RETURN count(n) AS cnt")
                    counts[label.lower() + "s"] = result.single()["cnt"]
                rel_result = session.run("MATCH ()-[r]->() RETURN count(r) AS cnt")
                counts["relationships"] = rel_result.single()["cnt"]
                return {"connected": True, **counts}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def ingest_debug_result(self, error_name: str, language: str, root_cause: str, fix: str, related_concepts: list[str]) -> bool:
        """Dynamically ingest an analyzed error into the Neo4j Knowledge Graph."""
        if not self._driver or not error_name:
            return False

        query = """
        MERGE (e:Error {name: $error_name})
        ON CREATE SET e.id = toLower($error_name), e.language = $language
        ON MATCH SET e.language = $language
        
        MERGE (f:Fix {description: $fix})
        ON CREATE SET f.id = toLower($error_name) + '_fix'
        
        MERGE (e)-[:FIXED_BY]->(f)
        
        WITH e
        UNWIND $related_concepts AS concept_name
        MERGE (c:Concept {name: concept_name})
        ON CREATE SET c.id = toLower(concept_name)
        MERGE (e)-[:RELATED_TO]->(c)
        """
        
        try:
            database = os.getenv("NEO4J_DATABASE", "neo4j")
            with self._driver.session(database=database) as session:
                session.run(query, 
                            error_name=error_name[:100], 
                            language=language or "unknown",
                            fix=fix[:500] if fix else "No fix provided.",
                            related_concepts=[c[:50] for c in related_concepts] if related_concepts else [])
                print(f"[GraphService] Successfully ingested '{error_name}' into graph.")
                return True
        except Exception as e:
            print(f"[GraphService] Failed to ingest debug result: {e}")
            return False


graph_service = GraphService()
