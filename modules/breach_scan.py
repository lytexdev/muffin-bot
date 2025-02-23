import discord
from discord.ext import commands
from discord import app_commands
import aiohttp


class BreachScan(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_email(self, email):
        url = f"https://api.xposedornot.com/v1/check-email/{email}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def check_domain(self, domain):
        url = f"https://api.xposedornot.com/v1/breaches?domain={domain}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def get_breach_details(self, email):
        url = f"https://api.xposedornot.com/v1/breach-analytics?email={email}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None

    @app_commands.command(name="breachscan", description="Scan an email for data breaches")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def breach_scan(self, interaction: discord.Interaction, email: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        scan_message = await interaction.followup.send(f"🔍 Scanning `{email}` for data breaches... Please wait.", wait=True)
        check_result = await self.check_email(email)

        if not check_result or not check_result.get("breaches", []):
            embed = discord.Embed(
                title="✅ No Breaches Found!",
                description=f"**{email}** is not in any known data breaches.",
                color=discord.Color.green()
            )
            await scan_message.edit(content="", embed=embed)
            return

        breach_details = await self.get_breach_details(email)
        breaches = breach_details.get("DataClasses", [])

        embed = discord.Embed(title=f"⚠️ {email} was found in breaches!", color=discord.Color.red())
        embed.add_field(name="🔍 Total Breaches", value=f"**{check_result['breaches']}** breaches found.", inline=False)

        if breaches:
            breach_list = "\n".join([f"- {b}" for b in breaches[:10]])
            embed.add_field(name="📂 Breached Data Includes:", value=breach_list, inline=False)

        await scan_message.edit(content="", embed=embed)

    @app_commands.command(name="domainscan", description="Scan a domain for data breaches")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def domain_scan(self, interaction: discord.Interaction, domain: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        scan_message = await interaction.followup.send(f"🔍 Scanning `{domain}` for domain-wide data breaches... Please wait.", wait=True)

        results = await self.check_domain(domain)

        if not results or not results.get("Breaches"):
            embed = discord.Embed(
                title="✅ No Breaches Found!",
                description=f"**{domain}** has not been involved in any known data breaches.",
                color=discord.Color.green()
            )
            await scan_message.edit(content="", embed=embed)
            return

        embed = discord.Embed(title=f"⚠️ {domain} has been breached!", color=discord.Color.red())
        embed.add_field(name="🔍 Total Breaches", value=f"**{len(results['Breaches'])}** breaches found.", inline=False)

        breach_list = "\n".join([f"- {b}" for b in results['Breaches'][:10]])
        embed.add_field(name="📂 Breached Services", value=breach_list, inline=False)

        await scan_message.edit(content="", embed=embed)

async def setup(client):
    await client.add_cog(BreachScan(client))
