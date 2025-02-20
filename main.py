import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import aiohttp

config = load_dotenv()

class MuffinBot(commands.Bot):
    async def on_ready(self):
        print(f'{self.user} is now running!')
        
intents = discord.Intents.default()
intents.message_content = True

client = MuffinBot(
    command_prefix="/",
    intents=intents,
    activity=discord.Activity(type=discord.ActivityType.listening, name=os.getenv('STATUS', 'lytex.dev')),
    status=discord.Status.online,
    sync_commands=True,
    delete_not_existing_commands=True
)

@client.tree.command(name="ping", description="Replies with pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

if __name__ == "__main__":
    try:
        for file in os.listdir('modules'):
            if file.endswith('.py'):
                client.load_extension(f'modules.{file[:-3]}')
        
        client.run(os.getenv('TOKEN'))
    except Exception as e:
        print(f"Error: {e}")