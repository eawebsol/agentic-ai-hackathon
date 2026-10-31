"""
api/seed_demo_data.py
---------------------
Seeds initial demo data for Educentriks Cognify:
1. Microsoft AI-103 certification entry
2. Core AI-103 exam objectives
3. Concepts with prerequisite relationships (PS02 Concept Graph)
4. Objective-to-concept mappings
5. Official learning resources (Microsoft Learn)
6. Two demo learners (Beginner Career-Switcher vs. Experienced Cloud Dev)
"""

import json
from uuid import uuid4
from datetime import datetime, timezone
from api.database import get_connection

def seed():
    now = datetime.now(timezone.utc)
    with get_connection() as conn:
        print("Seeding demo data for Educentriks Cognify...")

        # 1. Certification: AI-103
        cert_id = str(uuid4())
        cert_row = conn.execute(
            """
            INSERT INTO certifications (id, provider, code, title, status, version, source_url, verified_at)
            VALUES (%s::uuid, 'Microsoft', 'AI-103', 'Azure AI Apps and Agents Developer Associate',
                    'active', '2025.1',
                    'https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-apps-and-agents-developer-associate/',
                    %s)
            ON CONFLICT (code) DO UPDATE SET title = EXCLUDED.title
            RETURNING id
            """,
            (cert_id, now)
        ).fetchone()
        cert_id = str(cert_row["id"])
        print(f"✓ Certification AI-103 ready (id: {cert_id})")

        # 2. Key AI-103 Exam Objectives
        objectives = [
            ("1.1", "Design and configure multi-turn agent conversations and state handling", "Design and implement AI agents", 20.0),
            ("1.2", "Integrate tool calling, custom functions, and external APIs in agents", "Design and implement AI agents", 25.0),
            ("2.1", "Implement Retrieval-Augmented Generation (RAG) with vector search", "Knowledge retrieval and grounding", 25.0),
            ("2.2", "Chunking strategies and vector indexing configuration", "Knowledge retrieval and grounding", 15.0),
            ("3.1", "Implement agent evaluation, guardrails, and responsible AI practices", "Evaluation and security", 15.0),
        ]

        obj_ids = {}
        for code, desc, domain, weight in objectives:
            row = conn.execute(
                """
                INSERT INTO exam_objectives (certification_id, objective_id, description, domain, weighting_pct, source_url, verified_at)
                VALUES (%s::uuid, %s, %s, %s, %s,
                        'https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-apps-and-agents-developer-associate/',
                        %s)
                ON CONFLICT (certification_id, objective_id) DO UPDATE SET description = EXCLUDED.description
                RETURNING id
                """,
                (cert_id, code, desc, domain, weight, now)
            ).fetchone()
            obj_ids[code] = str(row["id"])
        print(f"✓ Seeded {len(obj_ids)} exam objectives")

        # 3. PS02 Concept Graph (Nodes + Prerequisites)
        concepts_data = [
            # slug, name, description, domain, difficulty, [prereq_slugs]
            ("llm-foundations", "LLM Fundamentals & Prompt Engineering",
             "Understanding temperature, tokenization, context windows, and system prompting.",
             "Core AI", "beginner", []),
            ("vector-embeddings", "Vector Embeddings & Semantic Search",
             "High-dimensional representations, cosine similarity, distance metrics.",
             "Knowledge retrieval and grounding", "beginner", ["llm-foundations"]),
            ("chunking-strategies", "Document Chunking & Preprocessing",
             "Recursive character splitting, semantic chunking, and metadata tagging.",
             "Knowledge retrieval and grounding", "intermediate", ["vector-embeddings"]),
            ("rag-retrieval", "Retrieval-Augmented Generation (RAG) Pipelines",
             "Top-k semantic retrieval, hybrid search, grounding prompt construction.",
             "Knowledge retrieval and grounding", "intermediate", ["chunking-strategies"]),
            ("agent-tool-calling", "Agent Tool Calling & Function Execution",
             "Defining schemas, parsing tool calls, executing external APIs deterministically.",
             "Design and implement AI agents", "intermediate", ["llm-foundations"]),
            ("agent-state-memory", "Agent State Management & Multi-turn Memory",
             "Session state, conversation history, checkpointing, and scratchpad management.",
             "Design and implement AI agents", "advanced", ["agent-tool-calling"]),
            ("agent-guardrails", "Agent Evaluation, Guardrails & Responsible AI",
             "Evaluating faithfulness, hallucination mitigation, jailbreak prevention, content safety.",
             "Evaluation and security", "intermediate", ["agent-tool-calling", "rag-retrieval"]),
        ]

        concept_id_map = {}
        for slug, name, desc, domain, diff, _ in concepts_data:
            row = conn.execute(
                """
                INSERT INTO concepts (slug, name, description, certification, domain, difficulty, learning_objectives)
                VALUES (%s, %s, %s, 'AI-103', %s, %s, %s::jsonb)
                ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description
                RETURNING id
                """,
                (slug, name, desc, domain, diff, json.dumps([]))
            ).fetchone()
            concept_id_map[slug] = str(row["id"])

        # Insert Concept Prerequisites (Edges)
        prereq_count = 0
        for slug, _, _, _, _, prereqs in concepts_data:
            c_id = concept_id_map[slug]
            for p_slug in prereqs:
                p_id = concept_id_map[p_slug]
                conn.execute(
                    """
                    INSERT INTO concept_prerequisites (concept_id, prerequisite_id)
                    VALUES (%s::uuid, %s::uuid)
                    ON CONFLICT DO NOTHING
                    """,
                    (c_id, p_id)
                )
                prereq_count += 1
        print(f"✓ Seeded {len(concept_id_map)} concepts with {prereq_count} prerequisite relationships (Concept Graph)")

        # Map Objectives to Concepts
        obj_concept_pairs = [
            ("1.1", "agent-state-memory"),
            ("1.2", "agent-tool-calling"),
            ("2.1", "rag-retrieval"),
            ("2.2", "chunking-strategies"),
            ("3.1", "agent-guardrails"),
        ]
        for obj_code, concept_slug in obj_concept_pairs:
            conn.execute(
                """
                INSERT INTO objective_concepts (objective_id, concept_id)
                VALUES (%s::uuid, %s::uuid)
                ON CONFLICT DO NOTHING
                """,
                (obj_ids[obj_code], concept_id_map[concept_slug])
            )

        # 4. Learning Resources (Microsoft Learn links & content chunks)
        res_row = conn.execute(
            """
            INSERT INTO learning_resources (certification_id, title, url, resource_type, metadata, last_verified_at)
            VALUES (%s::uuid,
                    'Develop AI agents on Azure with Semantic Kernel and AutoGen',
                    'https://learn.microsoft.com/en-us/azure/ai-services/agents/overview',
                    'guide',
                    %s::jsonb,
                    %s)
            RETURNING id
            """,
            (cert_id, json.dumps({"topic": "agents", "provider": "Microsoft"}), now)
        ).fetchone()
        res_id = str(res_row["id"])

        conn.execute(
            """
            INSERT INTO resource_chunks (resource_id, chunk_index, content, metadata)
            VALUES (%s::uuid, 0,
                    'Azure AI Agents allow developers to build autonomous and semi-autonomous systems that reason, plan, and execute tool calls. Agents maintain session state and connect to enterprise vector stores for grounded RAG.',
                    %s::jsonb)
            ON CONFLICT (resource_id, chunk_index) DO UPDATE SET content = EXCLUDED.content
            """,
            (res_id, json.dumps({"source": "Microsoft Learn", "concept": "agent-state-memory"}))
        )
        print("✓ Seeded official learning resources and knowledge chunks")

        # 5. Two Diverse Demo Learners (for Hackathon Demo Acceptance)
        # Learner 1: Career switcher (Beginner)
        l1_id = "00000000-0000-0000-0000-000000000001"
        conn.execute(
            """
            INSERT INTO learners (id, name, "current_role", experience_level, target_certification,
                                  learning_preferences, available_study_hours, created_at)
            VALUES (%s::uuid, 'Alex Rivera', 'Frontend Web Developer', 'beginner', 'AI-103',
                    %s::jsonb, 8, %s)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            """,
            (l1_id, json.dumps(["voice-first", "practical-exercises", "visual-diagrams"]), now)
        )

        # Learner 2: Experienced Cloud Engineer
        l2_id = "00000000-0000-0000-0000-000000000002"
        conn.execute(
            """
            INSERT INTO learners (id, name, "current_role", experience_level, target_certification,
                                  learning_preferences, available_study_hours, created_at)
            VALUES (%s::uuid, 'Sarah Chen', 'Senior Cloud Solutions Architect', 'intermediate', 'AI-103',
                    %s::jsonb, 5, %s)
            ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            """,
            (l2_id, json.dumps(["scenario-questions", "architecture-reviews", "deep-dive"]), now)
        )
        print("✓ Seeded 2 demo learners (Alex: Beginner switcher, Sarah: Experienced Architect)")

        conn.commit()
        print("\nAll demo data seeded successfully!")

if __name__ == "__main__":
    seed()

