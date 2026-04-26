"""Seed script for LiveNeed demo data.

Run: python seed.py
Populates the database with sample needs and volunteers for demo purposes.
"""

import sys
import os

# Ensure we can import from the backend directory
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, SessionLocal
from models import Need, User
from ai.nlp_processor import process_need_text
from ai.urgency_scorer import compute_urgency
from datetime import datetime, timedelta
import json
import random

SAMPLE_NEEDS = [
    {
        "raw_text": "Emergency! Family of 5 trapped after building collapse in downtown district. Need immediate medical rescue and ambulance.",
        "location_hint": "Downtown District, Block 4",
    },
    {
        "raw_text": "Critical: 200 displaced families in Riverside need emergency food supplies and clean drinking water urgently.",
        "location_hint": "Riverside Community Center",
    },
    {
        "raw_text": "Urgent medical supplies needed at St. Mary's clinic. Running out of antibiotics and bandages for flood victims.",
        "location_hint": "St. Mary's Clinic, East Side",
    },
    {
        "raw_text": "Three homeless families with children need temporary shelter before tonight's storm. Currently at the bus station.",
        "location_hint": "Central Bus Station",
    },
    {
        "raw_text": "School building roof damaged in earthquake. 150 students cannot attend class. Need construction volunteers.",
        "location_hint": "Greenfield Public School",
    },
    {
        "raw_text": "Community kitchen running low on supplies. Need volunteers to organize food distribution for 80 elderly residents.",
        "location_hint": "Oak Street Community Hall",
    },
    {
        "raw_text": "Violence reported in north sector. Several families feel unsafe and need relocation assistance immediately.",
        "location_hint": "North Sector, Area 7",
    },
    {
        "raw_text": "Children in rural area lack basic learning materials. Teacher requesting books, notebooks, and stationery for 45 students.",
        "location_hint": "Willowbrook Village School",
    },
    {
        "raw_text": "Fire at textile factory. Workers injured. Need medical help and temporary housing for displaced workers.",
        "location_hint": "Industrial Zone, Factory Row",
    },
    {
        "raw_text": "Clean water supply disrupted after pipe burst. 300 residents in Maple Heights affected. Need logistics support for water tankers.",
        "location_hint": "Maple Heights, Sector 12",
    },
]

SAMPLE_VOLUNTEERS = [
    {
        "name": "Dr. Sarah Chen",
        "email": "sarah.chen@example.com",
        "role": "volunteer",
        "skills": "medical, general",
        "latitude": 28.6139,
        "longitude": 77.2090,
    },
    {
        "name": "Raj Patel",
        "email": "raj.patel@example.com",
        "role": "volunteer",
        "skills": "logistics, construction",
        "latitude": 28.6200,
        "longitude": 77.2150,
    },
    {
        "name": "Maria Gonzalez",
        "email": "maria.g@example.com",
        "role": "volunteer",
        "skills": "education, general, logistics",
        "latitude": 28.6350,
        "longitude": 77.2250,
    },
    {
        "name": "Ahmed Hassan",
        "email": "ahmed.h@example.com",
        "role": "volunteer",
        "skills": "construction, general",
        "latitude": 28.6450,
        "longitude": 77.1950,
    },
    {
        "name": "Dr. Emily Park",
        "email": "emily.park@example.com",
        "role": "volunteer",
        "skills": "medical, education",
        "latitude": 28.6100,
        "longitude": 77.2300,
    },
    {
        "name": "James Okonkwo",
        "email": "james.o@example.com",
        "role": "coordinator",
        "skills": "logistics, general, construction",
        "latitude": 28.6250,
        "longitude": 77.2050,
    },
]


def seed():
    init_db()
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_needs = db.query(Need).count()
        existing_users = db.query(User).count()

        if existing_needs > 0 or existing_users > 0:
            print(f"Database already has {existing_needs} needs and {existing_users} users.")
            response = input("Clear and re-seed? (y/N): ").strip().lower()
            if response != "y":
                print("Aborted.")
                return
            # Clear existing data
            db.query(Need).delete()
            db.query(User).delete()
            db.commit()
            print("Cleared existing data.")

        # Seed volunteers
        print("\n--- Seeding Volunteers ---")
        for v in SAMPLE_VOLUNTEERS:
            user = User(
                name=v["name"],
                email=v["email"],
                role=v["role"],
                skills=v["skills"],
                latitude=v["latitude"],
                longitude=v["longitude"],
                is_active=True,
                created_at=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"  [OK] {user.name} (ID: {user.id}) - skills: {user.skills}")

        # Seed needs with staggered submission times
        print("\n--- Seeding Needs ---")
        for i, n in enumerate(SAMPLE_NEEDS):
            # Stagger submission times to test recency bonus
            submitted_at = datetime.utcnow() - timedelta(minutes=random.randint(0, 120))
            need = Need(
                raw_text=n["raw_text"],
                location_hint=n["location_hint"],
                status="pending",
                submitted_at=submitted_at,
                updated_at=submitted_at,
            )
            db.add(need)
            db.commit()
            db.refresh(need)

            # Run NLP analysis
            nlp_result = process_need_text(need.raw_text)
            score = compute_urgency(nlp_result, need.submitted_at)

            need.category = nlp_result.category
            need.urgency_score = score
            need.entities = json.dumps(nlp_result.entities)
            need.updated_at = datetime.utcnow()
            db.commit()

            print(
                f"  [OK] Need #{need.id}: [{need.category.upper():>9}] "
                f"urgency={need.urgency_score:5.1f} - {need.raw_text[:60]}..."
            )

        print(f"\n[DONE] Seeded {len(SAMPLE_VOLUNTEERS)} volunteers and {len(SAMPLE_NEEDS)} needs.")
        print("   Run the backend with: uvicorn main:app --reload")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
