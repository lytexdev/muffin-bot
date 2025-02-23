import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import nmap
import socket
import ipaddress

class NetworkScan(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.nm = nmap.PortScanner()

    def is_private_ip(self, ip):
        try:
            return ipaddress.ip_address(ip).is_private
        except ValueError:
            return False

    def resolve_domain(self, target):
        try:
            ip_address = socket.gethostbyname(target)
            if self.is_private_ip(ip_address):
                return None
            return ip_address
        except socket.gaierror:
            return None

    def run_nmap_scan(self, target, scan_type):
        resolved_ip = self.resolve_domain(target) or target

        if self.is_private_ip(resolved_ip) or resolved_ip in ["127.0.0.1", "::1", "localhost"]:
            return resolved_ip, "❌ Scanning local or private addresses is not allowed."

        scan_types = {
            "Quick Scan": "-F",
            "Full Scan": "-p-",
            "Service Detection": "-sV"
        }

        if scan_type not in scan_types:
            return resolved_ip, "❌ Invalid scan type."

        try:
            self.nm.scan(resolved_ip, arguments=scan_types[scan_type])
            scan_data = self.nm[resolved_ip]

            results = []
            for port in scan_data.get("tcp", {}):
                service = scan_data["tcp"][port].get("name", "Unknown")
                results.append(f"🟢 **Port {port}** - {service}")

            if scan_type == "OS Detection":
                os_guess = scan_data.get("osmatch", [])
                if os_guess:
                    results.append(f"🖥 **OS Detected:** {os_guess[0]['name']} ({os_guess[0]['accuracy']}% accuracy)")

            return resolved_ip, results if results else None
        except Exception as e:
            return resolved_ip, f"Error running Nmap: {str(e)}"

    @app_commands.command(name="nmap", description="Scan open ports on a target using Nmap")
    @app_commands.describe(
        target="The domain or IP to scan",
        scan_type="Select a scan type"
    )
    @app_commands.choices(scan_type=[
        app_commands.Choice(name="Quick Scan (Fast)", value="Quick Scan"),
        app_commands.Choice(name="Full Scan (All Ports)", value="Full Scan"),
        app_commands.Choice(name="Service Detection (Find Running Services)", value="Service Detection"),
    ])
    async def nmap_scan(self, interaction: discord.Interaction, target: str, scan_type: app_commands.Choice[str]):
        await interaction.response.defer(thinking=True, ephemeral=True)

        resolved_ip, scan_result = self.run_nmap_scan(target, scan_type.value)

        embed = discord.Embed(title=f"🔍 Nmap Scan Results for {target} ({resolved_ip})", color=discord.Color.blue())

        if isinstance(scan_result, str):
            embed.description = scan_result
        elif scan_result:
            embed.add_field(name="🛠 Scan Type", value=scan_type.name, inline=False)
            embed.add_field(name="📡 Scan Results", value="\n".join(scan_result), inline=False)
        else:
            embed.add_field(name="✅ No Open Ports Found", value="Target appears to be secure.", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(NetworkScan(client))
