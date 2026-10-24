"""
database.py - SQLite Database Management for Smart Campus Lost & Found Matcher
------------------------------------------------------------------------------
Author: College Innovation Project
Purpose: Handles local database creation, schema management, report persistence,
         and sample data seeding using Python's built-in sqlite3 module.
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database file in the project folder
DB_PATH = os.path.join(os.path.dirname(__file__), "campus_lost_found.db")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")

# Ensure the uploads directory exists for user-uploaded images
os.makedirs(UPLOADS_DIR, exist_ok=True)


def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    row_factory = sqlite3.Row allows accessing columns by name like a dictionary.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the SQLite database tables.
    Runs CREATE TABLE IF NOT EXISTS so it is safe to call on every app startup.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Main reports table for both Lost and Found items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('LOST', 'FOUND')),
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            color TEXT NOT NULL,
            location TEXT NOT NULL,
            date_event TEXT NOT NULL,
            description TEXT NOT NULL,
            image_path TEXT DEFAULT '',
            contact_name TEXT DEFAULT 'Campus Member',
            contact_info TEXT DEFAULT '',
            status TEXT DEFAULT 'OPEN' CHECK(status IN ('OPEN', 'MATCH_PENDING', 'RESOLVED')),
            created_at TEXT NOT NULL
        )
    """)

    # Index for fast filtering by type and category
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_category ON reports(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)")

    conn.commit()
    conn.close()

    # Seed sample data only if the database is brand new and empty
    seed_sample_data_if_empty()


def mask_contact_info(contact: str) -> str:
    """
    Privacy Protection Helper:
    Masks student contact information (email or phone) to protect student privacy.
    Example: 'alex.smith@college.edu' -> 'al***@college.edu'
             '9876543210' -> '******3210'
    """
    if not contact:
        return "Not provided (Contact via Campus Lost & Found Desk)"

    contact = contact.strip()
    if "@" in contact:
        parts = contact.split("@")
        username = parts[0]
        domain = parts[1]
        if len(username) <= 2:
            masked_user = username[0] + "***"
        else:
            masked_user = username[:2] + "***" + username[-1]
        return f"{masked_user}@{domain}"
    elif len(contact) >= 7:
        # Assume phone number or student ID
        return "*" * (len(contact) - 4) + contact[-4:]
    else:
        return "***" + contact[-2:] if len(contact) >= 2 else "***"


def insert_report(report_type: str, title: str, category: str, color: str,
                  location: str, date_event: str, description: str,
                  image_path: str = "", contact_name: str = "",
                  contact_info: str = "") -> int:
    """
    Inserts a newly reported lost or found item into the database.
    Returns the auto-generated report ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contact_name = contact_name.strip() if contact_name else "Anonymous Student"

    cursor.execute("""
        INSERT INTO reports (
            type, title, category, color, location, date_event,
            description, image_path, contact_name, contact_info, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)
    """, (
        report_type.upper(),
        title.strip(),
        category.strip(),
        color.strip(),
        location.strip(),
        date_event.strip(),
        description.strip(),
        image_path.strip(),
        contact_name,
        contact_info.strip(),
        now_iso
    ))

    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id


def get_all_reports(report_type=None, category=None, location=None,
                    color=None, status=None, search_query=None):
    """
    Fetches reports with optional filters and keyword search.
    Returns a list of dictionary-like rows.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM reports WHERE 1=1"
    params = []

    if report_type and report_type != "All":
        query += " AND type = ?"
        params.append(report_type.upper())

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if location and location != "All":
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    if color and color != "All":
        query += " AND color LIKE ?"
        params.append(f"%{color}%")

    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    if search_query and search_query.strip():
        term = f"%{search_query.strip()}%"
        query += " AND (title LIKE ? OR description LIKE ? OR location LIKE ?)"
        params.extend([term, term, term])

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_report_by_id(report_id: int):
    """
    Retrieves a single report by its ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_report_status(report_id: int, new_status: str):
    """
    Updates the status of a report ('OPEN', 'MATCH_PENDING', 'RESOLVED').
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reports SET status = ? WHERE id = ?", (new_status, report_id))
    conn.commit()
    conn.close()


def get_stats():
    """
    Returns summary metrics for the dashboard:
    Total lost items, total found items, resolved items, and open reports.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM reports WHERE type = 'LOST'")
    total_lost = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE type = 'FOUND'")
    total_found = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE status = 'RESOLVED'")
    total_resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE status = 'OPEN'")
    total_open = cursor.fetchone()[0]

    conn.close()
    return {
        "total_lost": total_lost,
        "total_found": total_found,
        "total_resolved": total_resolved,
        "total_open": total_open
    }


def seed_sample_data_if_empty():
    """
    Seeds a small set of realistic, fictional sample reports ONLY if the
    reports table is empty. This guarantees that restarting the app will never
    duplicate sample records!
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM reports")
    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        return  # Data already exists; do not duplicate

    # Curated sample reports designed to showcase strong matches, partial matches, and distinct items
    sample_items = [
        # Match Pair 1: Hydro Flask (High Match)
        {
            "type": "LOST",
            "title": "Hydro Flask Insulated Water Bottle",
            "category": "Water Bottles & Tumblers",
            "color": "Matte Black",
            "location": "Central Library - 2nd Floor Study Area",
            "date_event": "2026-10-20",
            "description": "32oz wide mouth black water bottle. Has a scratch near the base and a small NASA sticker on one side.",
            "contact_name": "Rohan Patel (CS Dept)",
            "contact_info": "rohan.p@campus.edu",
            "status": "OPEN"
        },
        {
            "type": "FOUND",
            "title": "Black Metal Water Flask",
            "category": "Water Bottles & Tumblers",
            "color": "Black",
            "location": "Central Library - 2nd Floor Quiet Zone",
            "date_event": "2026-10-20",
            "description": "Black insulated flask left on study table 14. Has a space sticker and minor scratch on the bottom edge.",
            "contact_name": "Library Front Desk",
            "contact_info": "libdesk@campus.edu",
            "status": "OPEN"
        },

        # Match Pair 2: College ID Card Holder (High Match)
        {
            "type": "LOST",
            "title": "Navy Blue Lanyard with College ID",
            "category": "ID Cards & Wallets",
            "color": "Navy Blue",
            "location": "Student Cafeteria - Food Court",
            "date_event": "2026-10-21",
            "description": "Blue fabric neck strap with clear plastic badge holder. Contains student meal card and room key card.",
            "contact_name": "Ananya Sharma (1st Year)",
            "contact_info": "ananya.s@campus.edu",
            "status": "OPEN"
        },
        {
            "type": "FOUND",
            "title": "Blue Neck Lanyard with ID Badge",
            "category": "ID Cards & Wallets",
            "color": "Blue",
            "location": "Student Cafeteria - Near Coffee Counter",
            "date_event": "2026-10-21",
            "description": "Dark blue lanyard holding an ID card case with two cards inside. Handed over to cafeteria staff.",
            "contact_name": "Cafeteria Lost Desk",
            "contact_info": "dining@campus.edu",
            "status": "OPEN"
        },

        # Match Pair 3: Earphones (Moderate/Semantic Match)
        {
            "type": "LOST",
            "title": "Wireless Earbuds in White Case",
            "category": "Electronics & Chargers",
            "color": "White",
            "location": "Computer Science Lab 302",
            "date_event": "2026-10-22",
            "description": "Small white charging case with Bluetooth earphones. Has a tiny blue silicone lanyard attached.",
            "contact_name": "David Kim",
            "contact_info": "david.k@campus.edu",
            "status": "OPEN"
        },
        {
            "type": "FOUND",
            "title": "EarPods Charging Case",
            "category": "Electronics & Chargers",
            "color": "White",
            "location": "Computer Science Lab Hallway",
            "date_event": "2026-10-22",
            "description": "White wireless earphone case picked up from bench outside room 302. Has a short blue cord loop.",
            "contact_name": "Lab Assistant",
            "contact_info": "cslab@campus.edu",
            "status": "OPEN"
        },

        # Standalone Lost Item (No immediate match yet)
        {
            "type": "LOST",
            "title": "Engineering Mechanics Spiral Notebook",
            "category": "Notebooks & Stationery",
            "color": "Green",
            "location": "Lecture Hall B",
            "date_event": "2026-10-23",
            "description": "Green cover 5-subject spiral notebook with handwritten lecture notes on kinematics and dynamics.",
            "contact_name": "Marcus Lee",
            "contact_info": "marcus.l@campus.edu",
            "status": "OPEN"
        },

        # Standalone Found Item (No immediate match yet)
        {
            "type": "FOUND",
            "title": "Compact Folding Umbrella",
            "category": "Clothing & Umbrellas",
            "color": "Yellow",
            "location": "Campus Main Entrance Security Post",
            "date_event": "2026-10-23",
            "description": "Bright yellow mini umbrella with wooden handle. Kept in the main gate security booth.",
            "contact_name": "Main Gate Guard",
            "contact_info": "security@campus.edu",
            "status": "OPEN"
        }
    ]

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in sample_items:
        cursor.execute("""
            INSERT INTO reports (
                type, title, category, color, location, date_event,
                description, image_path, contact_name, contact_info, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, '', ?, ?, ?, ?)
        """, (
            item["type"],
            item["title"],
            item["category"],
            item["color"],
            item["location"],
            item["date_event"],
            item["description"],
            item["contact_name"],
            item["contact_info"],
            item["status"],
            now_iso
        ))

    conn.commit()
    conn.close()
