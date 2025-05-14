import csv
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base # Import your SQLAlchemy setup
from app.models import University                     # Import your University model
from app.utils import parse_db_range_string           # Import your parsing utility
from app.core.config import DATABASE_URL              # To verify DB URL is loaded

# --- Configuration ---
CSV_FILE_PATH = 'Find MyUni 3.0 (Responses) - University Data.csv' # Adjust if needed

def load_data_from_csv(db: Session, csv_filepath: str):
    """
    Reads data from the CSV file, parses it, and loads it into the database.
    """
    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file not found at {csv_filepath}")
        return

    existing_uni_names = {uni.name for uni in db.query(University.name).all()}
    new_universities = []
    skipped_count = 0

    with open(csv_filepath, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        print(f"Reading data from {csv_filepath}...")
        for i, row in enumerate(reader):
            try:
                uni_name = row.get('university_name', '').strip()
                if not uni_name:
                    print(f"Skipping row {i+2} due to missing university name.")
                    skipped_count += 1
                    continue

                if uni_name in existing_uni_names:
                    # print(f"Skipping already existing university: {uni_name}")
                    skipped_count += 1
                    continue

                # Parse tuition and cost of living ranges
                tuition_min, tuition_max = parse_db_range_string(row.get('tuition_fees_category'))
                cost_min, cost_max = parse_db_range_string(row.get('cost_of_living_category'))

                # Helper to convert to int or None
                def to_int_or_none(value_str):
                    if value_str and value_str.strip():
                        try:
                            return int(value_str)
                        except ValueError:
                            print(f"Warning: Could not convert '{value_str}' to int for uni '{uni_name}'. Using None.")
                            return None
                    return None

                uni_data = University(
                    name=uni_name,
                    geopolitical_region=row.get('geopolitical_region', '').strip(),
                    state=row.get('state', '').strip(),
                    specialty=row.get('specialty', '').strip(),
                    ownership=row.get('ownership', '').strip(),
                    type=row.get('type', '').strip(),
                    academic_rigor=to_int_or_none(row.get('academic_rigor')),
                    sports_facilities=to_int_or_none(row.get('sports_facilities')),
                    hostel_quality=to_int_or_none(row.get('hostel_quality')),
                    social_life=to_int_or_none(row.get('Social Life')), # Note space in CSV header
                    tuition_min=tuition_min,
                    tuition_max=tuition_max,
                    cost_of_living_min=cost_min,
                    cost_of_living_max=cost_max,
                    tuition_category_str=row.get('tuition_fees_category', '').strip(),
                    cost_category_str=row.get('cost_of_living_category', '').strip(),
                    source_url_1=row.get('source_urls__001', '').strip(),
                    source_url_2=row.get('source_urls__002', '').strip()
                )
                new_universities.append(uni_data)
                existing_uni_names.add(uni_name) # Add to set to avoid duplicate additions within the same run

            except Exception as e:
                print(f"Error processing row {i+2} for university '{uni_name}': {e}")
                skipped_count += 1
                continue

    if new_universities:
        try:
            db.add_all(new_universities)
            db.commit()
            print(f"Successfully added {len(new_universities)} new universities to the database.")
        except Exception as e:
            db.rollback()
            print(f"Error during database commit: {e}")
            print("Rolling back changes for this batch.")
    else:
        print("No new universities to add.")

    if skipped_count > 0:
        print(f"Skipped {skipped_count} rows (either due to errors, missing names, or already existing).")


if __name__ == "__main__":
    print("Starting data loading process...")

    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable is not set.")
        print("Please ensure your .env file is configured correctly.")
        exit(1)
    else:
        print(f"Connecting to database: {DATABASE_URL.split('@')[-1]}") # Obfuscate user/pass

    # Create tables if they don't exist (useful for initial setup)
    # In a production system with Alembic, you'd run migrations first.
    # For this script, it's okay to ensure tables exist.
    print("Ensuring database tables are created (if they don't exist)...")
    Base.metadata.create_all(bind=engine)
    print("Tables checked/created.")

    db_session = SessionLocal()
    try:
        load_data_from_csv(db_session, CSV_FILE_PATH)
    finally:
        db_session.close()
        print("Database session closed.")
    print("Data loading process finished.")