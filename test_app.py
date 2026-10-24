"""
test_app.py - Verification Script to Test Database and Matching Engine
"""

import os
import database as db
import matcher

def test_system():
    print("1. Testing Database Initialization...")
    db.init_db()
    stats = db.get_stats()
    print(f"   Database initialized successfully. Current Stats: {stats}")
    assert stats["total_lost"] >= 1, "Expected sample lost items to be seeded."
    assert stats["total_found"] >= 1, "Expected sample found items to be seeded."

    print("\n2. Testing Sample Deduplication on Re-init...")
    db.init_db()  # Run again
    stats2 = db.get_stats()
    assert stats["total_lost"] == stats2["total_lost"], "Duplicate seeding detected!"
    print(f"   Deduplication verified: {stats2['total_lost']} lost items still in database.")

    print("\n3. Testing Contact Masking...")
    masked_email = db.mask_contact_info("rohan.patel@college.edu")
    masked_phone = db.mask_contact_info("9876543210")
    print(f"   rohan.patel@college.edu -> {masked_email}")
    print(f"   9876543210 -> {masked_phone}")
    assert "rohan.patel@" not in masked_email
    assert "987654" not in masked_phone

    print("\n4. Testing Matcher Engine (Rule-Based & NLP)...")
    reports = db.get_all_reports()
    rule_matches = matcher.find_all_matches(reports, min_score=40, use_nlp=False)
    nlp_matches = matcher.find_all_matches(reports, min_score=40, use_nlp=True)

    print(f"   Rule-Based matches found: {len(rule_matches)}")
    print(f"   NLP-Assisted matches found: {len(nlp_matches)}")
    assert len(rule_matches) >= 2, "Expected at least 2 high-confidence sample matches."

    top_match = rule_matches[0]
    print(f"\n   Top Match: '{top_match['lost_item']['title']}' <---> '{top_match['found_item']['title']}'")
    print(f"   Score: {top_match['total_score']}/100 ({top_match['confidence']})")
    print("   Breakdown:")
    for b in top_match["breakdown"]:
        print(f"     * {b['factor']}: {b['score']}/{b['max']} ({b['detail']})")

    print("\n5. Testing Inserting New Report...")
    new_id = db.insert_report(
        report_type="LOST",
        title="Test Scientific Calculator Casio FX-991EX",
        category="Electronics & Chargers",
        color="Black",
        location="Computer Science Lab 301",
        date_event="2026-10-24",
        description="Black Casio scientific calculator with solar panel and student ID sticker on backside.",
        contact_name="Tester Student",
        contact_info="tester@campus.edu"
    )
    print(f"   Inserted test lost report with ID: {new_id}")
    retrieved = db.get_report_by_id(new_id)
    assert retrieved is not None
    assert retrieved["title"] == "Test Scientific Calculator Casio FX-991EX"
    print("   Retrieved report verified successfully.")

    # Clean up test report to keep sample clean
    conn = db.get_db_connection()
    conn.execute("DELETE FROM reports WHERE id = ?", (new_id,))
    conn.commit()
    conn.close()
    print("   Cleaned up test record.")

    print("\nALL VERIFICATION CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_system()
