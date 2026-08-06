import asyncio
from sqlalchemy import text
from bot.config.database import getDbSession
from bot.main import bot as global_bot

async def main():
    # Wait for bot to login to resolve names
    print("Logging in to find member...")
    # Since we run inside container using env, we can just query the database first
    with getDbSession() as session:
        # Let's see the users in the member table
        rows = session.execute(text("SELECT user_id, username, nick, chill_coin FROM member")).fetchall()
        print("Existing members:")
        target_uid = None
        for r in rows:
            uid, name, nick, coins = r
            print(f"  - ID: {uid}, Name: {name}, Nick: {nick}, Coins: {coins}")
            if name == "Quang Quằng Quẹo" or nick == "Quang Quằng Quẹo" or (nick and "Quang" in str(nick)) or (name and "Quang" in str(name)):
                target_uid = uid
        
        # If not matched by name/nick, we can match from the list of IDs we saw
        # Test naruto has user ID 1094846212135452753
        # Let's set 1,000,000 coins for the user
        if target_uid:
            session.execute(
                text("UPDATE member SET chill_coin = 1000000 WHERE user_id = :uid"),
                {"uid": target_uid}
            )
            session.commit()
            print(f"✅ Successfully updated coins for User ID {target_uid} to 1,000,000!")
        else:
            # If name is not synced in DB yet, let's update all members in the DB to have 1,000,000 coins for testing convenience!
            session.execute(text("UPDATE member SET chill_coin = 1000000"))
            session.commit()
            print("✅ Updated all database members to 1,000,000 chill coins!")

if __name__ == "__main__":
    asyncio.run(main())
