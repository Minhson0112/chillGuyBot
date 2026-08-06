import urllib.request
import json
import re
import random
from sqlalchemy import text
from bot.config.database import getDbSession

def create_table_if_not_exists():
    sql_drop = "DROP TABLE IF EXISTS quiz_questions;"
    sql_create = """
    CREATE TABLE quiz_questions (
        id VARCHAR(100) PRIMARY KEY,
        question TEXT NOT NULL,
        type VARCHAR(50) NOT NULL,
        difficulty VARCHAR(50) NOT NULL,
        options TEXT NULL,
        correct_answer TEXT NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    with getDbSession() as session:
        session.execute(text(sql_drop))
        session.execute(text(sql_create))
        session.commit()
    print("✅ Cleared and created clean quiz_questions table.")

def parse_question_text(q_text):
    parts = re.split(r'\s+[A-D]\.\s+|\n[A-D]\.\s+|^[A-D]\.\s+', q_text)
    if len(parts) >= 5:
        question_body = parts[0].strip()
        question_body = re.sub(r'^Câu\s+\d+[:\.]\s*', '', question_body)
        options = [p.strip() for p in parts[1:5]]
        return question_body, options
    return None, None

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def main():
    create_table_if_not_exists()

    tree_url = "https://api.github.com/repos/Xdao85/VNHSGE/git/trees/main?recursive=1"
    print("Fetching repository tree...")
    tree_data = fetch_json(tree_url)
    
    json_paths = []
    for item in tree_data.get('tree', []):
        path = item['path']
        if path.startswith("Dataset/VNHSGE-V/JSON format/") and path.endswith(".json"):
            # Only import History, Geography, and Civic Education (trivia-based, no LaTeX formulas)
            if any(subject in path for subject in ["History", "Geography", "CivicEducation"]):
                json_paths.append(path)

    print(f"Found {len(json_paths)} JSON files to import.")

    imported_count = 0
    skipped_count = 0
    existing_ids = set()

    chunk = []
    for idx, path in enumerate(json_paths):
        # Escape path for URL
        escaped_path = path.replace(" ", "%20")
        raw_url = f"https://raw.githubusercontent.com/Xdao85/VNHSGE/main/{escaped_path}"
        
        print(f"[{idx+1}/{len(json_paths)}] Downloading {path}...")
        try:
            questions_data = fetch_json(raw_url)
            for q in questions_data:
                q_id = q.get("ID")
                if not q_id or q_id in existing_ids:
                    continue

                # Skip if it is an image question
                if q.get("Image_Question") or q.get("Image_Answer"):
                    skipped_count += 1
                    continue

                question_raw = q.get("Question", "")
                choice_char = q.get("Choice", "").strip().upper()

                if not question_raw or choice_char not in ["A", "B", "C", "D"]:
                    skipped_count += 1
                    continue

                question_body, options = parse_question_text(question_raw)
                if not question_body or not options:
                    skipped_count += 1
                    continue

                choice_idx = ord(choice_char) - ord('A')
                if choice_idx >= len(options):
                    skipped_count += 1
                    continue

                correct_answer_text = options[choice_idx]

                # Map difficulty randomly
                difficulty = random.choice(["easy", "medium", "hard"])

                # Determine type
                # 80% multiple_choice, 20% fill_in (True/False boolean doesn't fit standard A/B/C/D text easily, but we have multiple_choice and fill_in)
                # Let's do 70% multiple_choice, 30% fill_in
                q_type = random.choice(["multiple_choice", "multiple_choice", "multiple_choice", "fill_in"])

                chunk.append({
                    "id": q_id,
                    "question": question_body,
                    "type": q_type,
                    "difficulty": difficulty,
                    "options": json.dumps(options, ensure_ascii=False),
                    "correct_answer": correct_answer_text
                })

                if len(chunk) >= 500:
                    insert_chunk(chunk)
                    imported_count += len(chunk)
                    chunk = []

        except Exception as e:
            print(f"Error processing {path}: {e}")

    if chunk:
        insert_chunk(chunk)
        imported_count += len(chunk)

    print(f"\nImport Completed!")
    print(f"Successfully imported: {imported_count} questions")
    print(f"Skipped (image-based or bad format): {skipped_count} questions")

def insert_chunk(chunk):
    sql = """
    INSERT INTO quiz_questions (id, question, type, difficulty, options, correct_answer)
    VALUES (:id, :question, :type, :difficulty, :options, :correct_answer)
    """
    with getDbSession() as session:
        for item in chunk:
            session.execute(text(sql), item)
        session.commit()
    print(f"Inserted chunk of {len(chunk)} questions...")

if __name__ == "__main__":
    main()
