# Technical Plan: Quiz Feature Redevelopment

## Proposed Technical Design

### 1. Data Storage
*   We will download a curated subset of the Vietnamese High School Graduation Exam (VNHSGE) dataset.
*   We will store the questions in a JSON file at `bot/assets/quiz/vnhsge_questions.json` or load them into a database table.
*   Questions will be structured as:
    ```json
    {
      "id": "uuid",
      "question": "Nội dung câu hỏi...",
      "type": "multiple_choice | boolean | fill_in",
      "difficulty": "easy |medium | hard",
      "options": ["A", "B", "C", "D"], // Only for multiple_choice
      "correct_answer": "Đáp án đúng"

    }
     {
      "id": "uuid",
      "question": "Nội dung câu hỏi...",
      "type": "multiple_choice | boolean | fill_in",
      "difficulty": "easy |medium| hard",
      "options": [ " đúng /sai"], // Only for multiple_choice
      "correct_answer": "Đáp án đúng" 
     }
    ```


### 2. Service Implementation
*   Modify `bot/services/quiz/quizQuestionService.py` to read from the local JSON questions file instead of fetching from OpenTDB.
*   Implement format-specific rendering:
    *   `multiple_choice`: Display buttons A, B, C, D.
    *   `boolean`: Display True/False (Đúng / Sai) buttons.
    *   `fill_in`: Listen to chat messages in the channel to match the correct answer.

### 3. Command Implementation
*   Update `bot/commands/quiz/quiz.py` to load new questions.
*   Create a new file `bot/commands/quiz/topq.py` (or add to `quiz.py`) implementing `cg topq` which queries `QuizAnswerHistory` grouped by `user_id` and sorted descending.
