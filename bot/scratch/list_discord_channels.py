import os
import discord
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        for guild in self.guilds:
            print(f"\nGuild: {guild.name} ({guild.id})")
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    print(f"  - #{channel.name} ({channel.id})")
        await self.close()

client = Client(intents=discord.Intents.default())
client.run(token)
