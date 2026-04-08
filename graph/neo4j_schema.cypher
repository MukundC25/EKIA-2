// =============================================================================
// EKIA-2 Neo4j Schema — Cypher Queries
// Run these in Neo4j Browser or via ingest_graph.py
// =============================================================================

// --- Step 1: Create Constraints (ensure uniqueness) ---

CREATE CONSTRAINT error_name IF NOT EXISTS
FOR (e:Error) REQUIRE e.name IS UNIQUE;

CREATE CONSTRAINT concept_name IF NOT EXISTS
FOR (c:Concept) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT fix_id IF NOT EXISTS
FOR (f:Fix) REQUIRE f.id IS UNIQUE;

CREATE CONSTRAINT problem_name IF NOT EXISTS
FOR (p:Problem) REQUIRE p.name IS UNIQUE;

CREATE CONSTRAINT language_name IF NOT EXISTS
FOR (l:Language) REQUIRE l.name IS UNIQUE;

// --- Step 2: Create Indexes for fast lookups ---

CREATE INDEX error_language IF NOT EXISTS
FOR (e:Error) ON (e.language);

CREATE INDEX error_type IF NOT EXISTS
FOR (e:Error) ON (e.type);

// =============================================================================
// Sample Data Queries (also handled by ingest_graph.py)
// =============================================================================

// --- Language Nodes ---
MERGE (java:Language {name: "Java"})
MERGE (python:Language {name: "Python"})
MERGE (js:Language {name: "JavaScript"})
MERGE (cpp:Language {name: "C++"})
MERGE (sql:Language {name: "SQL"});

// --- Error Nodes ---
MERGE (e1:Error {name: "NullPointerException", language: "Java", type: "Runtime"})
MERGE (e2:Error {name: "KeyError", language: "Python", type: "Runtime"})
MERGE (e3:Error {name: "StackOverflowError", language: "Java", type: "Runtime"})
MERGE (e4:Error {name: "IndexError", language: "Python", type: "Runtime"})
MERGE (e5:Error {name: "TypeError", language: "JavaScript", type: "Runtime"})
MERGE (e6:Error {name: "Segmentation Fault", language: "C++", type: "Critical"})
MERGE (e7:Error {name: "Deadlock", language: "SQL", type: "Concurrency"})
MERGE (e8:Error {name: "RecursionError", language: "Python", type: "Runtime"})
MERGE (e9:Error {name: "OutOfMemoryError", language: "Java", type: "Runtime"})
MERGE (e10:Error {name: "CORS Error", language: "Web", type: "Network"});

// --- Concept Nodes ---
MERGE (c1:Concept {name: "Null Reference"})
MERGE (c2:Concept {name: "Recursion"})
MERGE (c3:Concept {name: "Array Bounds"})
MERGE (c4:Concept {name: "Memory Management"})
MERGE (c5:Concept {name: "Type Safety"})
MERGE (c6:Concept {name: "Concurrency"})
MERGE (c7:Concept {name: "Async Programming"})
MERGE (c8:Concept {name: "Dictionary Access"})
MERGE (c9:Concept {name: "Network Security"})
MERGE (c10:Concept {name: "Dynamic Programming"});

// --- Fix Nodes ---
MERGE (f1:Fix {id: "fix_001", description: "Use Optional<T> and null checks", code_tip: "Optional.ofNullable(obj).ifPresent(...)"})
MERGE (f2:Fix {id: "fix_002", description: "Add base case to recursive function", code_tip: "if (n <= 1) return n;"})
MERGE (f3:Fix {id: "fix_003", description: "Use dict.get() with default value", code_tip: "value = dict.get(key, default)"})
MERGE (f4:Fix {id: "fix_004", description: "Use @lru_cache for memoization", code_tip: "@functools.lru_cache"})
MERGE (f5:Fix {id: "fix_005", description: "Use smart pointers in C++", code_tip: "std::unique_ptr<T>"})
MERGE (f6:Fix {id: "fix_006", description: "Acquire locks in consistent order", code_tip: "Always lock A before B"})
MERGE (f7:Fix {id: "fix_007", description: "Configure CORSMiddleware in FastAPI", code_tip: "app.add_middleware(CORSMiddleware, ...)"})
MERGE (f8:Fix {id: "fix_008", description: "Increase JVM heap with -Xmx flag", code_tip: "java -Xmx4g -jar app.jar"});

// --- Problem Nodes ---
MERGE (p1:Problem {name: "LeetCode 206 - Reverse Linked List", platform: "LeetCode", difficulty: "Easy"})
MERGE (p2:Problem {name: "LeetCode 141 - Linked List Cycle", platform: "LeetCode", difficulty: "Easy"})
MERGE (p3:Problem {name: "LeetCode 509 - Fibonacci Number", platform: "LeetCode", difficulty: "Easy"})
MERGE (p4:Problem {name: "LeetCode 1 - Two Sum", platform: "LeetCode", difficulty: "Easy"})
MERGE (p5:Problem {name: "LeetCode 146 - LRU Cache", platform: "LeetCode", difficulty: "Medium"})
MERGE (p6:Problem {name: "LeetCode 70 - Climbing Stairs", platform: "LeetCode", difficulty: "Easy"})
MERGE (p7:Problem {name: "LeetCode 1114 - Print in Order", platform: "LeetCode", difficulty: "Easy"})
MERGE (p8:Problem {name: "LeetCode 322 - Coin Change", platform: "LeetCode", difficulty: "Medium"});

// =============================================================================
// Relationships
// =============================================================================

// Error --CAUSED_BY--> Concept
MATCH (e:Error {name: "NullPointerException"}), (c:Concept {name: "Null Reference"})
MERGE (e)-[:CAUSED_BY]->(c);

MATCH (e:Error {name: "StackOverflowError"}), (c:Concept {name: "Recursion"})
MERGE (e)-[:CAUSED_BY]->(c);

MATCH (e:Error {name: "RecursionError"}), (c:Concept {name: "Recursion"})
MERGE (e)-[:CAUSED_BY]->(c);

MATCH (e:Error {name: "KeyError"}), (c:Concept {name: "Dictionary Access"})
MERGE (e)-[:CAUSED_BY]->(c);

MATCH (e:Error {name: "Segmentation Fault"}), (c:Concept {name: "Memory Management"})
MERGE (e)-[:CAUSED_BY]->(c);

MATCH (e:Error {name: "OutOfMemoryError"}), (c:Concept {name: "Memory Management"})
MERGE (e)-[:CAUSED_BY]->(c);

MATCH (e:Error {name: "Deadlock"}), (c:Concept {name: "Concurrency"})
MERGE (e)-[:CAUSED_BY]->(c);

MATCH (e:Error {name: "TypeError"}), (c:Concept {name: "Type Safety"})
MERGE (e)-[:CAUSED_BY]->(c);

MATCH (e:Error {name: "CORS Error"}), (c:Concept {name: "Network Security"})
MERGE (e)-[:CAUSED_BY]->(c);

// Error --FIXED_BY--> Fix
MATCH (e:Error {name: "NullPointerException"}), (f:Fix {id: "fix_001"})
MERGE (e)-[:FIXED_BY]->(f);

MATCH (e:Error {name: "StackOverflowError"}), (f:Fix {id: "fix_002"})
MERGE (e)-[:FIXED_BY]->(f);

MATCH (e:Error {name: "RecursionError"}), (f:Fix {id: "fix_004"})
MERGE (e)-[:FIXED_BY]->(f);

MATCH (e:Error {name: "KeyError"}), (f:Fix {id: "fix_003"})
MERGE (e)-[:FIXED_BY]->(f);

MATCH (e:Error {name: "Segmentation Fault"}), (f:Fix {id: "fix_005"})
MERGE (e)-[:FIXED_BY]->(f);

MATCH (e:Error {name: "Deadlock"}), (f:Fix {id: "fix_006"})
MERGE (e)-[:FIXED_BY]->(f);

MATCH (e:Error {name: "CORS Error"}), (f:Fix {id: "fix_007"})
MERGE (e)-[:FIXED_BY]->(f);

MATCH (e:Error {name: "OutOfMemoryError"}), (f:Fix {id: "fix_008"})
MERGE (e)-[:FIXED_BY]->(f);

// Concept --PRACTICED_BY--> Problem
MATCH (c:Concept {name: "Null Reference"}), (p:Problem {name: "LeetCode 206 - Reverse Linked List"})
MERGE (c)-[:PRACTICED_BY]->(p);

MATCH (c:Concept {name: "Null Reference"}), (p:Problem {name: "LeetCode 141 - Linked List Cycle"})
MERGE (c)-[:PRACTICED_BY]->(p);

MATCH (c:Concept {name: "Recursion"}), (p:Problem {name: "LeetCode 509 - Fibonacci Number"})
MERGE (c)-[:PRACTICED_BY]->(p);

MATCH (c:Concept {name: "Recursion"}), (p:Problem {name: "LeetCode 70 - Climbing Stairs"})
MERGE (c)-[:PRACTICED_BY]->(p);

MATCH (c:Concept {name: "Dynamic Programming"}), (p:Problem {name: "LeetCode 322 - Coin Change"})
MERGE (c)-[:PRACTICED_BY]->(p);

MATCH (c:Concept {name: "Dictionary Access"}), (p:Problem {name: "LeetCode 1 - Two Sum"})
MERGE (c)-[:PRACTICED_BY]->(p);

MATCH (c:Concept {name: "Memory Management"}), (p:Problem {name: "LeetCode 146 - LRU Cache"})
MERGE (c)-[:PRACTICED_BY]->(p);

MATCH (c:Concept {name: "Concurrency"}), (p:Problem {name: "LeetCode 1114 - Print in Order"})
MERGE (c)-[:PRACTICED_BY]->(p);

// Error --IN_LANGUAGE--> Language
MATCH (e:Error {language: "Java"}), (l:Language {name: "Java"})
MERGE (e)-[:IN_LANGUAGE]->(l);

MATCH (e:Error {language: "Python"}), (l:Language {name: "Python"})
MERGE (e)-[:IN_LANGUAGE]->(l);

MATCH (e:Error {language: "JavaScript"}), (l:Language {name: "JavaScript"})
MERGE (e)-[:IN_LANGUAGE]->(l);

// =============================================================================
// Example GraphRAG Query
// =============================================================================

// Find errors, their causes, fixes, and practice problems:
// MATCH (e:Error {name: $error})-[:CAUSED_BY]->(c)-[:PRACTICED_BY]->(p)
// OPTIONAL MATCH (e)-[:FIXED_BY]->(f)
// RETURN e, c, p, f
