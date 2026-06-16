import sqlite3
import os

DB_NAME = "leads.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            email TEXT NOT NULL,
            target_role TEXT NOT NULL,
            company_focus TEXT,
            my_skills TEXT,
            experience_years REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_lead(company_name, email, target_role, company_focus, my_skills, experience_years):
    """Saves a single lead to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure experience_years is a float or None
    try:
        exp = float(experience_years) if experience_years is not None and str(experience_years).strip() != "" else 0.0
    except ValueError:
        exp = 0.0

    cursor.execute("""
        INSERT INTO leads (company_name, email, target_role, company_focus, my_skills, experience_years)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(company_name).strip(),
        str(email).strip(),
        str(target_role).strip(),
        str(company_focus).strip() if company_focus else "",
        str(my_skills).strip() if my_skills else "",
        exp
    ))
    conn.commit()
    conn.close()

def save_leads_batch(leads_list):
    """Saves a batch of leads to the database.
    Each item in leads_list should be a dictionary with keys matching the schema fields.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    parsed_leads = []
    for lead in leads_list:
        try:
            exp_val = lead.get('experience_years', 0.0)
            exp = float(exp_val) if exp_val is not None and str(exp_val).strip() != "" else 0.0
        except ValueError:
            exp = 0.0
            
        parsed_leads.append((
            str(lead.get('company_name', '')).strip(),
            str(lead.get('email', '')).strip(),
            str(lead.get('target_role', '')).strip(),
            str(lead.get('company_focus', '')).strip(),
            str(lead.get('my_skills', '')).strip(),
            exp
        ))

    cursor.executemany("""
        INSERT INTO leads (company_name, email, target_role, company_focus, my_skills, experience_years)
        VALUES (?, ?, ?, ?, ?, ?)
    """, parsed_leads)
    
    conn.commit()
    conn.close()

def get_all_leads():
    """Retrieves all leads from the database sorted by insertion order (newest first)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_leads(lead_ids):
    """Deletes leads matching the provided list of IDs."""
    if not lead_ids:
        return
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in lead_ids)
    cursor.execute(f"DELETE FROM leads WHERE id IN ({placeholders})", tuple(lead_ids))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database and 'leads' table initialized successfully.")
