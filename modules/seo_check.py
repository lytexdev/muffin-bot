import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import re
from datetime import datetime

class SEOCheck(commands.Cog):
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

    async def check_robots_txt(self, domain):
        url = f"https://{domain}/robots.txt"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False

    async def check_sitemap_xml(self, domain):
        url = f"https://{domain}/sitemap.xml"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    return url if response.status == 200 else None
        except Exception:
            return None

    async def measure_performance(self, domain):
        url = f"https://{domain}"
        try:
            async with aiohttp.ClientSession() as session:
                start_time = datetime.utcnow()
                async with session.get(url, timeout=5) as response:
                    elapsed_time = (datetime.utcnow() - start_time).total_seconds()
                    return f"⏳ **Load Time:** {elapsed_time:.2f} seconds"
        except Exception:
            return "⚠️ Could not measure response time"

    async def analyze_seo(self, domain):
        html = await self.fetch_website_source(domain)
        headers = await self.fetch_website_headers(domain)
        robots_exists = await self.check_robots_txt(domain)
        sitemap_url = await self.check_sitemap_xml(domain)
        load_time = await self.measure_performance(domain)

        seo_results = [load_time]

        if headers:
            if "strict-transport-security" in headers:
                seo_results.append("🔒 **HTTPS Security:** Enabled ✅")
            else:
                seo_results.append("⚠️ **HTTPS Security:** No HSTS detected ❌")

        if html:
            title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
            title = title_match.group(1) if title_match else "❌ No Title Tag Found"
            seo_results.append(f"📌 **Title Tag:** {title}")

            # Meta Description
            desc_match = re.search(r'<meta name="description" content="(.*?)"', html, re.IGNORECASE)
            description = desc_match.group(1) if desc_match else "❌ No Meta Description Found"
            seo_results.append(f"📖 **Meta Description:** {description}")

            # Meta Keywords
            keywords_match = re.search(r'<meta name="keywords" content="(.*?)"', html, re.IGNORECASE)
            keywords = keywords_match.group(1) if keywords_match else "❌ No Meta Keywords Found"
            seo_results.append(f"🔑 **Meta Keywords:** {keywords}")

            # Open Graph Tags (Social Media SEO)
            og_title_match = re.search(r'<meta property="og:title" content="(.*?)"', html, re.IGNORECASE)
            og_title = og_title_match.group(1) if og_title_match else "❌ No Open Graph Title Found"
            seo_results.append(f"📲 **Open Graph Title:** {og_title}")

            canonical_match = re.search(r'<link rel="canonical" href="(.*?)"', html, re.IGNORECASE)
            canonical = canonical_match.group(1) if canonical_match else "❌ No Canonical URL Found"
            seo_results.append(f"🔗 **Canonical URL:** {canonical}")

        seo_results.append(f"🤖 **robots.txt:** {'✅ Found' if robots_exists else '❌ Not Found'}")
        seo_results.append(f"🗺 **Sitemap.xml:** {sitemap_url if sitemap_url else '❌ Not Found'}")

        return seo_results if seo_results else ["❌ No SEO Data Available"]

    @app_commands.command(name="seocheck", description="Performs a full SEO audit of a website")
    async def seo_check(self, interaction: discord.Interaction, domain: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        seo_results = await self.analyze_seo(domain)

        embed = discord.Embed(title=f"📊 SEO & Performance Analysis for {domain}", color=discord.Color.yellow())
        embed.description = "\n".join(seo_results)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(SEOCheck(client))
