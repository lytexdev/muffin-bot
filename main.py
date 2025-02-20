import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


class MuffinBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/",
            intents=discord.Intents.default(),
            activity=discord.Activity(type=discord.ActivityType.playing, name=os.getenv('STATUS', 'lytex.dev')),
            status=discord.Status.online,
            help_command=None,
        )

    async def on_ready(self):
        print(f'{self.user} is now running!')
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands globally.")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

client = MuffinBot()

async def load_extensions():
    for file in os.listdir("modules"):
        if file.endswith(".py"):
            try:
                await client.load_extension(f"modules.{file[:-3]}")
                print(f"Module loaded: {file}")
            except Exception as e:
                print(f"Error loading {file}: {e}")

async def main():
    async with client:
        await load_extensions()
        await client.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
