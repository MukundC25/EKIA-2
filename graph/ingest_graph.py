"""
Graph Layer — Neo4j Graph Ingestion Script
Seeds Neo4j with the entire error knowledge base as a knowledge graph.
Run with: python -m graph.ingest_graph
"""
import json
import os
import sys
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
KNOWLEDGE_BASE_PATH = "data/error_knowledge_base/errors.json"


def load_errors() -> list[dict]:
    path = Path(KNOWLEDGE_BASE_PATH)
    if not path.exists():
        print(f"[ERROR] Knowledge base not found at {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)


def create_constraints(session):
    constraints = [
        "CREATE CONSTRAINT error_name IF NOT EXISTS FOR (e:Error) REQUIRE e.name IS UNIQUE",
        "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
        "CREATE CONSTRAINT fix_id IF NOT EXISTS FOR (f:Fix) REQUIRE f.id IS UNIQUE",
        "CREATE CONSTRAINT problem_name IF NOT EXISTS FOR (p:Problem) REQUIRE p.name IS UNIQUE",
        "CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE",
    ]
    for stmt in constraints:
        try:
            session.run(stmt)
        except Exception as e:
            print(f"[WARN] Constraint creation: {e}")
    print("[Graph] Constraints created.")


def ingest_error(session, error: dict):
    error_name = error["error_type"]
    language = error["language"]
    concept = error["concept"]
    fix_id = error["id"].replace("err_", "fix_")

    # Upsert Language node
    session.run(
        "MERGE (l:Language {name: $language})",
        language=language
    )

    # Upsert Error node
    session.run(
        """
        MERGE (e:Error {name: $name})
        SET e.language = $language,
            e.description = $description,
            e.tags = $tags
        """,
        name=error_name,
        language=language,
        description=error.get("description", ""),
        tags=",".join(error.get("tags", [])),
    )

    # Upsert Concept node
    session.run(
        "MERGE (c:Concept {name: $concept})",
        concept=concept
    )

    # Upsert Fix node
    session.run(
        """
        MERGE (f:Fix {id: $fix_id})
        SET f.description = $fix,
            f.code_tip = $code_tip
        """,
        fix_id=fix_id,
        fix=error.get("fix", ""),
        code_tip=error.get("fix_code", ""),
    )

    # Upsert Problem nodes
    for problem_name in error.get("practice_problems", []):
        session.run(
            "MERGE (p:Problem {name: $name})",
            name=problem_name
        )

    # Create relationships
    session.run(
        "MATCH (e:Error {name: $e}), (c:Concept {name: $c}) MERGE (e)-[:CAUSED_BY]->(c)",
        e=error_name, c=concept
    )
    session.run(
        "MATCH (e:Error {name: $e}), (f:Fix {id: $f}) MERGE (e)-[:FIXED_BY]->(f)",
        e=error_name, f=fix_id
    )
    session.run(
        "MATCH (e:Error {name: $e}), (l:Language {name: $l}) MERGE (e)-[:IN_LANGUAGE]->(l)",
        e=error_name, l=language
    )

    for concept_name in error.get("related_concepts", []):
        session.run("MERGE (c:Concept {name: $c})", c=concept_name)
        session.run(
            "MATCH (e:Error {name: $e}), (c:Concept {name: $c}) MERGE (e)-[:RELATED_TO]->(c)",
            e=error_name, c=concept_name
        )

    for problem_name in error.get("practice_problems", []):
        session.run(
            "MATCH (c:Concept {name: $c}), (p:Problem {name: $p}) MERGE (c)-[:PRACTICED_BY]->(p)",
            c=concept, p=problem_name
        )


def main():
    print(f"[Graph] Connecting to Neo4j at {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            driver.verify_connectivity()
            print("[Graph] Connected to Neo4j.")

            create_constraints(session)

            errors = load_errors()
            print(f"[Graph] Ingesting {len(errors)} errors into knowledge graph...")

            for i, error in enumerate(errors, 1):
                try:
                    ingest_error(session, error)
                    print(f"  [{i:02d}/{len(errors)}] ✓ {error['error_type']} ({error['language']})")
                except Exception as e:
                    print(f"  [{i:02d}/{len(errors)}] ✗ Failed {error['error_type']}: {e}")

            print("\n[Graph] ✅ Ingestion complete!")
            print(f"[Graph] Nodes: run `MATCH (n) RETURN count(n)` in Neo4j Browser to verify")

    except Exception as e:
        print(f"[Graph] ❌ Connection failed: {e}")
        print("[Graph] Make sure Neo4j Desktop is running and credentials are correct in .env")
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
