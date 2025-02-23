import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import socket
import ssl
from datetime import datetime

class WebsiteScan(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_security_headers(self, domain):
        url = f"https://{domain}"
        headers_to_check = [
            "Strict-Transport-Security", "Content-Security-Policy",
            "X-Frame-Options", "X-Content-Type-Options",
            "Referrer-Policy", "Permissions-Policy", "Access-Control-Allow-Origin"
        ]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    security_headers = {header: response.headers.get(header, "❌ Missing") for header in headers_to_check}
                    return security_headers, response
        except Exception:
            return None, None

    async def check_http_vs_https(self, domain):
        url = f"http://{domain}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, allow_redirects=False, timeout=5) as response:
                    if response.status in [301, 302]:
                        return f"✅ Redirects to HTTPS ({response.headers.get('Location', 'Unknown')})"
                    return "❌ No HTTPS redirection detected"
        except Exception:
            return "⚠️ Could not check HTTPS redirection"

    def check_ssl_certificate(self, domain):
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as sslsock:
                    cert = sslsock.getpeercert()
                    tls_version = sslsock.version()

            issuer = dict(x[0] for x in cert["issuer"])["organizationName"]
            expiration_date = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y GMT")

            return {
                "issuer": issuer,
                "expires": expiration_date.strftime("%Y-%m-%d"),
                "valid": expiration_date > datetime.utcnow(),
                "tls_version": tls_version
            }
        except Exception:
            return None

    async def detect_waf(self, domain):
        url = f"https://{domain}"
        waf_headers = {
            "server": ["cloudflare", "akamai", "incapsula", "sucuri"],
            "x-powered-by": ["mod_security", "sucuri"],
            "x-cdn": ["cloudflare", "imperva", "fastly"]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    headers = {key.lower(): value.lower() for key, value in response.headers.items()}

                    for header, waf_list in waf_headers.items():
                        if header in headers:
                            for waf in waf_list:
                                if waf in headers[header]:
                                    return f"🛡 Detected: {waf.capitalize()} WAF"

                async with session.get(f"{url}/?id=' OR 1=1 --", timeout=5) as response:
                    if response.status in [403, 406]:
                        return "🚫 WAF Detected (Blocked SQL Injection)"

        except Exception:
            return "⚠️ Could not test for WAF"

        return "✅ No WAF Detected"

    async def check_cdn_provider(self, domain):
        url = f"https://{domain}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    cdn_headers = ["server", "via", "x-cache", "cf-ray"]
                    detected_cdn = [f"{header}: {response.headers.get(header)}" for header in cdn_headers if header in response.headers]
                    return detected_cdn if detected_cdn else ["❌ No CDN detected"]
        except Exception:
            return ["⚠️ Could not check CDN"]

    async def check_performance(self, domain):
        url = f"https://{domain}"
        try:
            async with aiohttp.ClientSession() as session:
                start_time = datetime.utcnow()
                async with session.get(url, timeout=5) as response:
                    elapsed_time = (datetime.utcnow() - start_time).total_seconds()
                    return f"⏳ Response Time: {elapsed_time:.2f} seconds"
        except Exception:
            return "⚠️ Could not measure response time"

    @app_commands.command(name="websitescan", description="Scan a website for security headers, SSL, WAF, and performance")
    async def website_scan(self, interaction: discord.Interaction, domain: str):
        await interaction.response.defer(thinking=True, ephemeral=True)

        security_headers, response = await self.check_security_headers(domain)
        ssl_info = self.check_ssl_certificate(domain)
        https_check = await self.check_http_vs_https(domain)
        waf_check = await self.detect_waf(domain)
        cdn_info = await self.check_cdn_provider(domain)
        performance_info = await self.check_performance(domain)

        embed = discord.Embed(title=f"🔍 Security Scan for {domain}", color=discord.Color.red())

        if security_headers:
            missing_headers = [key for key, value in security_headers.items() if value == "❌ Missing"]
            security_summary = "✅ Good Security" if not missing_headers else f"⚠️ Missing: {', '.join(missing_headers)}"
            embed.add_field(name="🛑 Security Headers", value=security_summary, inline=False)

        embed.add_field(name="🔐 HTTPS Redirection", value=https_check, inline=False)

        if ssl_info:
            ssl_status = "✅ Valid" if ssl_info["valid"] else "❌ Expired"
            embed.add_field(name="🔒 SSL Status", value=ssl_status, inline=False)
            embed.add_field(name="🏢 Issuer", value=ssl_info["issuer"], inline=False)
            embed.add_field(name="📅 Expires", value=ssl_info["expires"], inline=False)
            embed.add_field(name="🔐 TLS Version", value=ssl_info["tls_version"], inline=False)

        embed.add_field(name="🛡 WAF Detection", value=waf_check, inline=False)
        embed.add_field(name="📡 CDN Provider", value="\n".join(cdn_info), inline=False)
        embed.add_field(name="⚡ Performance", value=performance_info, inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(client):
    await client.add_cog(WebsiteScan(client))
