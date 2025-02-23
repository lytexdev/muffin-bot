import discord
from discord.ext import commands
from discord import app_commands

class HelpCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="help", description="Shows a list of available commands with descriptions")
    async def help_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(title="Help Menu", description="A list of all available commands, categorized by functionality.", color=discord.Color.purple())
        embed.add_field(
            name="🌍 Security & Network Commands",
            value=(
                "**`/nmap <target> <scan_type>`** - Performs an Nmap port scan\n"
                "**`/websitescan <domain>`** - Scans for security risks (WAF, SSL, headers, etc.)\n"
                "**`/checkip <ip>`** - Shows IP reputation and details\n"
                "**`/dns <domain>`** - Retrieves DNS records (A, MX, TXT, NS, etc.)\n"
                "**`/reverseip <ip>`** - Finds domains hosted on a given IP\n"
                "**`/webarchitecture <domain>`** - Detects technologies used by a website\n"
            ),
            inline=False
        )
        embed.add_field(
            name="📈 SEO & Performance Commands",
            value=(
                "**`/seocheck <domain>`** - Performs a full SEO audit including performance analysis\n"
                "**`/archive <domain>`** - Retrieves past versions of a website from Archive.org\n"
            ),
            inline=False
        )
        embed.set_footer(text="Use /help to see this menu again. Stay ethical & legal! 🛡️")

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(HelpCommand(client))
