import sqlite3
import os
from logger import get_logger

log = get_logger(__name__)
DB_NAME = "leads.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    log.info("Initialising database at '%s'", DB_NAME)
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if table exists and has the old schema (containing my_skills column)
    cursor.execute("PRAGMA table_info(leads)")
    columns = [row[1] for row in cursor.fetchall()]
    if columns and "my_skills" in columns:
        log.info("Old schema detected in 'leads' table. Dropping table for recreation.")
        cursor.execute("DROP TABLE leads")
        conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            email TEXT NOT NULL,
            company_focus TEXT,
            our_value_proposition TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    log.debug("Database initialised successfully")

def save_lead(company_name, email, company_focus, our_value_proposition):
    """Saves a single lead to the database."""
    log.info("Saving single lead | company='%s' email='%s'",
             company_name, email)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads (company_name, email, company_focus, our_value_proposition)
        VALUES (?, ?, ?, ?)
    """, (
        str(company_name).strip(),
        str(email).strip(),
        str(company_focus).strip() if company_focus else "",
        str(our_value_proposition).strip() if our_value_proposition else ""
    ))
    conn.commit()
    conn.close()
    log.debug("Lead saved successfully | company='%s'", company_name)

def save_leads_batch(leads_list):
    """Saves a batch of leads to the database.
    Each item in leads_list should be a dictionary with keys matching the schema fields.
    """
    log.info("Saving batch of %d leads to database", len(leads_list))
    conn = get_connection()
    cursor = conn.cursor()

    parsed_leads = []
    for lead in leads_list:
        parsed_leads.append((
            str(lead.get('company_name', '')).strip(),
            str(lead.get('email', '')).strip(),
            str(lead.get('company_focus', '')).strip(),
            str(lead.get('our_value_proposition', '')).strip()
        ))

    cursor.executemany("""
        INSERT INTO leads (company_name, email, company_focus, our_value_proposition)
        VALUES (?, ?, ?, ?)
    """, parsed_leads)

    conn.commit()
    conn.close()
    log.info("Batch save complete — %d leads persisted", len(parsed_leads))

def get_all_leads():
    """Retrieves all leads from the database sorted by insertion order (newest first)."""
    log.debug("Fetching all leads from database")
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    log.info("Fetched %d lead(s) from database", len(rows))
    return [dict(row) for row in rows]

def delete_leads(lead_ids):
    """Deletes leads matching the provided list of IDs."""
    if not lead_ids:
        log.warning("delete_leads called with empty ID list — nothing to do")
        return
    log.info("Deleting %d lead(s) with IDs: %s", len(lead_ids), lead_ids)
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in lead_ids)
    cursor.execute(f"DELETE FROM leads WHERE id IN ({placeholders})", tuple(lead_ids))
    conn.commit()
    conn.close()
    log.info("Delete complete")

if __name__ == "__main__":
    init_db()
    print("Database and 'leads' table initialized successfully.")
