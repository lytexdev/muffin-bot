import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import re

class WebArchitecture(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def fetch_website_headers(self, domain):
        url = f"https://{domain}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    return response.headers if response.status == 200 else None
        except Exception:
            return None

    async def fetch_website_source(self, domain):
        url = f"https://{domain}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    return await response.text() if response.status == 200 else None
        except Exception:
            return None

    async def detect_technologies(self, domain):
        headers = await self.fetch_website_headers(domain)
        html = await self.fetch_website_source(domain)

        tech_info = []

        if headers:
            # Server
            if "server" in headers:
                tech_info.append(f"🖥 **Server:** {headers['server']}")
            if "x-powered-by" in headers:
                tech_info.append(f"⚙️ **Powered by:** {headers['x-powered-by']}")
            if "x-generator" in headers:
                tech_info.append(f"📄 **CMS:** {headers['x-generator']}")

        if html:
            # CMS
            if re.search(r"wp-content", html, re.IGNORECASE):
                tech_info.append("📄 **CMS:** WordPress")
            if re.search(r"drupal.js", html, re.IGNORECASE):
                tech_info.append("📄 **CMS:** Drupal")
            if re.search(r"Joomla!", html, re.IGNORECASE):
                tech_info.append("📄 **CMS:** Joomla")

            # JavaScript-Frameworks
            if re.search(r"jquery", html, re.IGNORECASE):
                tech_info.append("🛠 **JS Library:** jQuery")
            if re.search(r"react", html, re.IGNORECASE):
                tech_info.append("⚛️ **Frontend:** React.js")
            if re.search(r"vue", html, re.IGNORECASE):
                tech_info.append("🟢 **Frontend:** Vue.js")
            if re.search(r"angular", html, re.IGNORECASE):
                tech_info.append("🟥 **Frontend:** Angular")

            # Frontend CSS Frameworks
            if re.search(r"bootstrap", html, re.IGNORECASE):
                tech_info.append("🟣 **CSS Framework:** Bootstrap")
            if re.search(r"tailwind", html, re.IGNORECASE):
                tech_info.append("💠 **CSS Framework:** Tailwind CSS")

            # Backend Frameworks
            if re.search(r"django", html, re.IGNORECASE):
                tech_info.append("🐍 **Backend:** Django")
            if re.search(r"flask", html, re.IGNORECASE):
                tech_info.append("🥃 **Backend:** Flask")
            if re.search(r"express", html, re.IGNORECASE):
                tech_info.append("🟡 **Backend:** Express.js")
            if re.search(r"laravel", html, re.IGNORECASE):
                tech_info.append("🟥 **Backend:** Laravel")
            if re.search(r"asp.net", html, re.IGNORECASE):
                tech_info.append("🔵 **Backend:** ASP.NET")

            # Databases
            if re.search(r"mysql", html, re.IGNORECASE):
                tech_info.append("💾 **Database:** MySQL")
            if re.search(r"postgresql", html, re.IGNORECASE):
                tech_info.append("🐘 **Database:** PostgreSQL")
            if re.search(r"mongodb", html, re.IGNORECASE):
                tech_info.append("🍃 **Database:** MongoDB")
            if re.search(r"firebase", html, re.IGNORECASE):
                tech_info.append("🔥 **Database:** Firebase")

        return tech_info if tech_info else ["❌ No detectable technologies"]

    @app_commands.command(name="webarchitecture", description="Detects technologies used by a website")
    async def web_architecture(self, interaction: discord.Interaction, domain: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        tech_info = await self.detect_technologies(domain)

        embed = discord.Embed(title=f"🕵️‍♂️ Web Architecture for {domain}", color=discord.Color.blue())
        embed.description = "\n".join(tech_info)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(WebArchitecture(client))
