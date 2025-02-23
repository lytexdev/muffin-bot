import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, client):
        self.client = client
    @app_commands.command(name="ping", description="Ping of the bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        embed=discord.Embed(title="🏓 Pong!", color=discord.Color.purple())
        embed.add_field(name="📡 Latency", value=f"{round(self.client.latency * 1000)}ms", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(Ping(client))
