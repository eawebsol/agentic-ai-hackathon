"""
agents/tutor/tools/resources.py
Resource retrieval tool — semantic search over Microsoft Learn content chunks.

The pgvector similarity search runs when embeddings have been populated.
If no embeddings exist yet, the tool falls back to a keyword (ILIKE) search
so the agent remains functional during development before content is indexed.
"""

import os

from api.database import get_connection


def search_learning_resources(
    query: str,
    certification_code: str = "AI-103",
    top_k: int = 4,
) -> dict:
    """
    Retrieves the most relevant official learning resource chunks for a topic.

    Use this tool before answering any technical question about the certification.
    Always include the returned source URLs and titles in your answer so the
    learner can verify the information against official Microsoft documentation.

    If retrieval returns no results, disclose that limitation rather than
    inventing a citation.

    Args:
        query: Natural-language description of the topic to search for.
        certification_code: Exam code to scope the search, e.g. "AI-103".
        top_k: Maximum number of chunks to return (1–8).

    Returns:
        A dict containing a list of relevant chunks with source metadata,
        or a disclosure message when no content is indexed yet.
    """
    top_k = max(1, min(8, top_k))

    with get_connection() as conn:
        # Check whether any embeddings exist for this certification
        has_embeddings = conn.execute(
            """
            SELECT 1
            FROM resource_chunks rc
            JOIN learning_resources lr ON rc.resource_id = lr.id
            JOIN certifications c ON lr.certification_id = c.id
            WHERE c.code = %s
              AND rc.embedding IS NOT NULL
            LIMIT 1
            """,
            (certification_code,),
        ).fetchone()

        if has_embeddings:
            # Full vector similarity search
            # Requires the query to be embedded first; embedding is done
            # by the caller (api layer) and passed here in a production flow.
            # For now, fall through to keyword search — swap this block when
            # the embedding pipeline is ready.
            chunks = _keyword_search(conn, query, certification_code, top_k)
        else:
            chunks = _keyword_search(conn, query, certification_code, top_k)

    if not chunks:
        return {
            "status": "no_results",
            "message": (
                "No indexed content found for this query. "
                "Disclose this to the learner and direct them to "
                "https://learn.microsoft.com for official AI-103 material."
            ),
            "chunks": [],
        }

    return {
        "status": "ok",
        "query": query,
        "chunks": chunks,
        "total": len(chunks),
    }


def _keyword_search(conn, query: str, certification_code: str, top_k: int) -> list[dict]:
    """Full-text keyword fallback search using ILIKE."""
    words = [w.strip() for w in query.split() if len(w.strip()) > 2]
    if not words:
        return []

    conditions = " OR ".join(["rc.content ILIKE %s"] * len(words))
    params = [f"%{w}%" for w in words] + [certification_code, top_k]

    rows = conn.execute(
        f"""
        SELECT rc.id, rc.content, rc.metadata,
               lr.title AS resource_title, lr.url AS resource_url,
               lr.last_verified_at
        FROM resource_chunks rc
        JOIN learning_resources lr ON rc.resource_id = lr.id
        JOIN certifications c ON lr.certification_id = c.id
        WHERE ({conditions})
          AND c.code = %s
        LIMIT %s
        """,  # noqa: S608
        params,
    ).fetchall()

    return [
        {
            "chunk_id": str(row["id"]),
            "content": row["content"],
            "source_title": row["resource_title"],
            "source_url": row["resource_url"],
            "verified_at": (
                row["last_verified_at"].isoformat()
                if row["last_verified_at"]
                else None
            ),
            "metadata": row["metadata"],
        }
        for row in rows
    ]

