import re
import discord
from discord.ext import commands
import json
import math
import random
import os
import time

PLAYER_FILE = "player_data.json"

if not os.path.exists(PLAYER_FILE):
    with open(PLAYER_FILE, "w") as f:
        json.dump({}, f)

def load_players():
    with open(PLAYER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_players(players):
    with open(PLAYER_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=4)

players = load_players()
work_cooldown = {}

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
async def tertarik(ctx, *, nama_profesi):
    profesi_ditemukan = None

    for profesi in data:
        if profesi["nama"].lower() == nama_profesi.lower():
            profesi_ditemukan = profesi
            break

    if not profesi_ditemukan:
        await ctx.send("❌ Profesi tidak ditemukan.")
        return

    user_id = str(ctx.author.id)

    if user_id in players and players[user_id]["profesi"] is not None:
        await ctx.send(
            f"❌ Kamu masih bekerja sebagai **{players[user_id]['profesi']}**.\n"
            f"Gunakan `!resign` terlebih dahulu jika ingin berganti profesi."
        )
        return

    if user_id in players:
        players[user_id]["profesi"] = profesi_ditemukan["nama"]
    else:
        players[user_id] = {
            "nama": ctx.author.name,
            "profesi": profesi_ditemukan["nama"],
            "saldo": 0,
            "xp": 0,
            "level": 1
        }

    save_players(players)

    await ctx.send(
        f"🎉 Selamat! Kamu diterima sebagai **{profesi_ditemukan['nama']}**\n"
        f"🏢 Perusahaan: **{profesi_ditemukan['perusahaan']}**\n\n"
        f"Gunakan `!kerja` untuk mulai bekerja."
    )

@bot.command()
async def resign(ctx):
    user_id = str(ctx.author.id)

    if user_id not in players:
        await ctx.send("❌ Kamu belum memiliki profesi.")
        return

    profesi_lama = players[user_id]["profesi"]

    players[user_id]["profesi"] = None

    save_players(players)

    await ctx.send(
        f"📄 Kamu mengundurkan diri dari **{profesi_lama}**.\n"
        f"Gunakan `!tertarik <profesi>` untuk memilih profesi baru."
    )

@bot.command()
async def kerja(ctx):
    user_id = str(ctx.author.id)

    sekarang = time.time()

    if user_id in work_cooldown:
        sisa = 60 - (sekarang - work_cooldown[user_id])

        if sisa > 0:
            menit = int(sisa) // 60
            detik = int(sisa) % 60

            await ctx.send(
                f"⏳ Kamu masih lelah bekerja.\n"
                f"Tunggu **{menit}m {detik}s** lagi."
            )
            return

    if user_id not in players:
        await ctx.send(
            "❌ Kamu belum memiliki profesi.\n"
            "Gunakan `!tertarik <nama profesi>`."
        )
        return

    player = players[user_id]
    profesi = player["profesi"]

    berhasil = random.choice([True, False])

    if berhasil:
        uang = random.randint(3000000, 7000000)
        xp = random.randint(25, 50)

        pesan = (
            f"🏆 Sebagai **{profesi}**, kamu berhasil bekerja hari ini!\n"
            f"💰 +Rp{uang:,}\n"
            f"⭐ +{xp} XP"
        )
    else:
        uang = random.randint(500000, 2000000)
        xp = random.randint(5, 15)

        pesan = (
            f"😅 Hari ini kurang beruntung sebagai **{profesi}**.\n"
            f"💰 +Rp{uang:,}\n"
            f"⭐ +{xp} XP"
        )

    player["saldo"] += uang
    player["xp"] += xp

    kebutuhan_xp = player["level"] * 100

    if player["xp"] >= kebutuhan_xp:
        player["xp"] -= kebutuhan_xp
        player["level"] += 1
        pesan += f"\n\n🎉 LEVEL UP! Sekarang Level {player['level']}"

    work_cooldown[user_id] = sekarang

    save_players(players)

    await ctx.send(pesan)
    
@bot.command()
async def profile(ctx):
    user_id = str(ctx.author.id)

    if user_id not in players:
        await ctx.send("❌ Kamu belum memilih profesi.")
        return

    player = players[user_id]

    embed = discord.Embed(
        title=f"👤 Profil {ctx.author.name}",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="💼 Profesi",
        value=player["profesi"],
        inline=False
    )

    embed.add_field(
        name="⭐ Level",
        value=str(player["level"]),
        inline=True
    )

    embed.add_field(
        name="✨ XP",
        value=str(player["xp"]),
        inline=True
    )

    embed.add_field(
        name="💰 Saldo",
        value=f"Rp{player['saldo']:,}",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    if not players:
        await ctx.send("Belum ada data pemain.")
        return

    ranking = sorted(
        players.values(),
        key=lambda x: x["saldo"],
        reverse=True
    )

    embed = discord.Embed(
        title="🏆 Leaderboard Career Tycoon",
        color=discord.Color.green()
    )

    for i, player in enumerate(ranking[:10], start=1):
        embed.add_field(
            name=f"#{i} {player['nama']}",
            value=f"💰 Rp{player['saldo']:,}",
            inline=False
        )

    await ctx.send(embed=embed)

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
                f"🏢 **Perusahaan:** {profesi['perusahaan']}\n"
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
            title="📖 Cara Menggunakan Career Advisor Bot",
            description=(
                "Bot ini membantu menemukan profesi yang cocok berdasarkan minatmu "
                "serta menyediakan mini game Career Tycoon untuk mencoba simulasi karier."
            ),
            color=discord.Color.green()
        )

        embed.add_field(
            name="🎯 Mencari Rekomendasi Karier",
            value=(
                "**Command:** `!karir <minat>`\n\n"
                "**Contoh:**\n"
                "`!karir coding, teknologi, game`\n\n"
                "**Output:**\n"
                "Bot akan menampilkan profesi yang cocok dengan minatmu beserta deskripsinya."
            ),
            inline=False
        )

        embed.add_field(
            name="📋 Melihat Lowongan Kerja",
            value=(
                "**Command:** `!loker`\n"
                "`!loker 2`\n\n"
                "**Output:**\n"
                "Bot akan menampilkan daftar lowongan kerja, perusahaan, gaji, dan kontak."
            ),
            inline=False
        )

        embed.add_field(
            name="💡 Contoh Penggunaan",
            value=(
                "1. Gunakan `!karir basket, olahraga`\n"
                "2. Lihat rekomendasi profesi yang muncul\n"
                "3. Pilih profesi yang menarik untukmu"
            ),
            inline=False
        )

        embed.add_field(
            name="🎮 Mini Game: Career Tycoon",
            value=(
                "Selain memberi rekomendasi karier, bot ini juga memiliki mode simulasi karier.\n\n"
                "`!tertarik <profesi>` → memilih profesi\n"
                "`!kerja` → bekerja dan mendapatkan uang\n"
                "`!profile` → melihat level dan saldo\n"
                "`!leaderboard` → melihat ranking pemain\n"
                "`!resign` → keluar dari profesi saat ini"
            ),
            inline=False
        )

        embed.add_field(
            name="🏆 Tujuan Mini Game",
            value=(
                "Kumpulkan uang, naik level, dan jadilah pemain terkaya di leaderboard."
            ),
            inline=False
        )

        embed.set_footer(
            text="Career Advisor Bot • Temukan profesi yang cocok untuk masa depanmu"
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



