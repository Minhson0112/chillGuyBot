# Test Plan: Quiz Feature Redevelopment

## Manual Testing
1.  **Quiz Start (`cg quiz`)**: Verify that the command sends a Vietnamese question with the correct difficulty and layout.
2.  **Answering Multiple Choice / True/False**: Click buttons to answer and verify correct/incorrect response, `chill_coin` balance update, and database record creation.
3.  **Answering Fill-in-the-blank**: Send text answers in the channel to verify matching.
4.  **Leaderboard (`cg topq`)**: Run the command and verify it outputs correct rankings.
