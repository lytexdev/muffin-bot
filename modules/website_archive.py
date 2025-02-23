import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

class WebsiteArchiveLookup(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def fetch_archive_snapshots(self, domain):
        url = f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&fl=timestamp,original&filter=statuscode:200&limit=5"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        snapshots = await response.json()
                        return snapshots[1:] if len(snapshots) > 1 else None
        except Exception:
            return None

    @app_commands.command(name="webarchive", description="Retrieve old versions of a website from Archive.org")
    async def archive_lookup(self, interaction: discord.Interaction, domain: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        snapshots = await self.fetch_archive_snapshots(domain)

        embed = discord.Embed(title=f"📜 Archive Lookup for {domain}", color=discord.Color.gold())

        if snapshots:
            archive_links = [f"[{snap[0]}](https://web.archive.org/web/{snap[0]}/{snap[1]})" for snap in snapshots]
            embed.description = "\n".join(archive_links)
        else:
            embed.description = "❌ No archived versions found."

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(WebsiteArchiveLookup(client))
