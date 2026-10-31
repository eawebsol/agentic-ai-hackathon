"""
agents/tutor/tools/curriculum.py
Curriculum tool — retrieve verified AI-103 exam objectives from the database.
"""

from api.database import get_connection


def get_exam_objectives(
    certification_code: str = "AI-103",
    domain: str | None = None,
) -> dict:
    """
    Returns the versioned exam objectives for the specified certification.

    Use this tool to ground explanations, diagnostics and learning plans
    in official exam content. Never invent objective IDs or weightings.
    Only trust data returned by this tool; do not rely on training knowledge
    for official exam structure.

    Args:
        certification_code: The Microsoft exam code, e.g. "AI-103".
        domain: Optional domain filter (e.g. "Design and implement agents").
                Pass None to return all domains.

    Returns:
        A dict containing certification metadata and a list of objectives,
        or {"error": "..."} if the certification is not found.
    """
    with get_connection() as conn:
        cert = conn.execute(
            """
            SELECT id, provider, code, title, status, version,
                   source_url, verified_at
            FROM certifications
            WHERE code = %s
            """,
            (certification_code,),
        ).fetchone()

        if cert is None:
            return {
                "error": (
                    f"Certification '{certification_code}' not found in the database. "
                    "Seed the certifications table before running the tutor agent."
                )
            }

        cert_id = cert["id"]

        query = """
            SELECT objective_id, description, domain, weighting_pct,
                   source_url, verified_at
            FROM exam_objectives
            WHERE certification_id = %s
        """
        params: list = [cert_id]

        if domain:
            query += " AND domain ILIKE %s"
            params.append(f"%{domain}%")

        query += " ORDER BY objective_id"
        objectives = conn.execute(query, params).fetchall()

    return {
        "certification": {
            "code": cert["code"],
            "title": cert["title"],
            "provider": cert["provider"],
            "status": cert["status"],
            "version": cert["version"],
            "source_url": cert["source_url"],
            "verified_at": cert["verified_at"].isoformat() if cert["verified_at"] else None,
        },
        "objectives": [
            {
                "objective_id": obj["objective_id"],
                "description": obj["description"],
                "domain": obj["domain"],
                "weighting_pct": float(obj["weighting_pct"]) if obj["weighting_pct"] else None,
                "source_url": obj["source_url"],
                "verified_at": obj["verified_at"].isoformat() if obj["verified_at"] else None,
            }
            for obj in objectives
        ],
        "total_objectives": len(objectives),
    }

