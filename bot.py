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

class StartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(
        label="How To Use",
        style=discord.ButtonStyle.blurple,
        emoji="📖"
    )
    async def how_to_use(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="📖 Cara Menggunakan Bot",
            color=discord.Color.green()
        )

        embed.add_field(
            name="🎯 !karir",
            value=(
                "Mencari rekomendasi karir berdasarkan minat.\n"
                "**Contoh:**\n"
                "`!karir coding, teknologi, game`"
            ),
            inline=False
        )

        embed.add_field(
            name="📋 !loker",
            value=(
                "Menampilkan daftar lowongan kerja.\n"
                "**Contoh:**\n"
                "`!loker`\n"
                "`!loker 2` (halaman 2)"
            ),
            inline=False
        )

        embed.add_field(
            name="💡 Cara Kerja Bot",
            value=(
                "1. Masukkan minat kamu menggunakan `!karir`.\n"
                "2. Bot akan mencocokkan minat dengan database profesi.\n"
                "3. Klik tombol Show untuk melihat hasil lengkap.\n"
                "4. Gunakan `!loker` untuk melihat lowongan yang tersedia."
            ),
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


@bot.command()
async def start(ctx):
    embed = discord.Embed(
        title="🤖 Selamat Datang di Career Advisor Bot",
        description=(
            "Bot ini membantu kamu menemukan profesi yang cocok "
            "berdasarkan minat dan melihat lowongan kerja yang tersedia."
        ),
        color=discord.Color.gold()
    )

    embed.add_field(
        name="✨ Fitur Utama",
        value=(
            "🎯 Rekomendasi karir berdasarkan minat\n"
            "📋 Daftar lowongan kerja\n"
            "📌 Tampilan hasil yang mudah dibaca"
        ),
        inline=False
    )

    embed.set_footer(
        text="Klik tombol 'How To Use' untuk melihat panduan."
    )

    await ctx.send(
        embed=embed,
        view=StartView()
    )

bot.run("Token")



