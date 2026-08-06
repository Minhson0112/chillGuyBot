# Specification: Redeveloped Quiz Feature

## Overview
Redevelop the bot's quiz game to use a curated Vietnamese question bank instead of the unreliable and English-only Open Trivia Database (OpenTDB) API.

## Requirements

### 1. Question Bank Source
*   Use the VNHSGE (Vietnamese High School Graduation Examination) dataset from `https://github.com/Xdao85/VNHSGE`.
*   Completely eliminate English questions.
*   Store or read the questions locally or via a loaded database/JSON file to avoid slow API translations.

### 2. Difficulty and Formats
*   **Difficulty levels**: Easy (Dễ) and medium( trung bình)  Hard (Khó).
*   **Question types**:
    *   Multiple Choice (Trắc nghiệm 4 lựa chọn)
    *   True/False (Đúng / Sai)
    *   Fill-in-the-blank (Điền vào chỗ trống)

### 3. Leaderboard Command (`cg topq`)
*   Display top players who have answered the most questions correctly.
*   Format output in a clean Discord embed.
