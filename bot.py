import re
import discord
from discord.ext import commands
import json
import math

with open("database.json", "r", encoding="utf-8") as file:
    data = json.load(file)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True
)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    match = re.match(
        r"^!?loker\s*(\d+)?$",
        message.content.strip(),
        re.IGNORECASE
    )

    if match:
        halaman = int(match.group(1)) if match.group(1) else 1

        await loker.callback(ctx := await bot.get_context(message), halaman)
        return

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"✅ Login sebagai {bot.user}")

class ShowKarirView(discord.ui.View):
    def __init__(self, pesan_hasil):
        super().__init__(timeout=60)
        self.pesan_hasil = pesan_hasil

    @discord.ui.button(
        label="Show",
        style=discord.ButtonStyle.green,
        emoji="📌"
    )
    async def show(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            self.pesan_hasil,
            ephemeral=True
        )

import discord

import discord
from discord.ext import commands

@bot.command()
async def loker(ctx, halaman: int = 1):
    per_halaman = 10

    total_halaman = (len(data) + per_halaman - 1) // per_halaman

    if halaman < 1 or halaman > total_halaman:
        await ctx.send(
            f"❌ Halaman tidak ditemukan.\n"
            f"Gunakan angka dari 1 sampai {total_halaman}."
        )
        return

    awal = (halaman - 1) * per_halaman
    akhir = awal + per_halaman

    embed = discord.Embed(
        title="📋 Daftar Lowongan",
        description=f"Halaman {halaman}/{total_halaman}\n",
        color=discord.Color.blue()
    )

    for profesi in data[awal:akhir]:
        embed.add_field(
            name=f"🎯 {profesi['nama']}",
            value=(
                f"💰 **Gaji:** {profesi['gaji']}\n"
                f"📧 **Email:** {profesi['email']}\n"
                f"📝 **Deskripsi:** {profesi['deskripsi']}\n"
                f"\u200b"  # baris kosong
            ),
            inline=False
        )

    embed.set_footer(
        text=f"Lowongan {awal + 1}-{min(akhir, len(data))} dari {len(data)} | Gunakan !loker <halaman>"
    )

    await ctx.send(embed=embed)

@bot.command()
async def karir(ctx, *, minat_input):
    minat_user = [m.strip().lower() for m in minat_input.split(",")]

    hasil = []

    for profesi in data:
        minat_profesi = [m.lower() for m in profesi["minat"]]

        skor = sum(
            1 for minat in minat_user
            if minat in minat_profesi
        )

        if skor > 0:
            hasil.append((skor, profesi))

    hasil.sort(key=lambda x: x[0], reverse=True)

    if not hasil:
        await ctx.send("❌ Tidak ada profesi yang cocok.")
        return

    detail = "📌 **Rekomendasi Karir**\n\n"

    for skor, profesi in hasil[:10]:
        detail += (
            f"🎯 **{profesi['nama']}**\n"
            f"✅ {skor} minat cocok\n"
            f"📝 {profesi['deskripsi']}\n\n"
        )

    await ctx.send(
        f"🎮 Ditemukan **{len(hasil)}** karir yang cocok!",
        view=ShowKarirView(detail)
    )

bot.run("TOKEN")



