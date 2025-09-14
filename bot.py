import discord
from discord.ext import commands
from flask import Flask
import threading
import os

# ----- AYARLAR -----
WELCOME_ROLE_ID = 1416554944915439677  # Yeni Üye rolünün ID'si
APPLY_ROLE_ID = 1416758210936705164    # Başvuru Adayı rolünün ID'si
AD_ROLE_ID = 1416758403769827368       # Reklamcı rolünün ID'si
WELCOME_CHANNEL_ID = 1416554612290490418 # Karşılama kanalının ID'si
BANNER_PATH = "banner.png"  # Hoş geldin banner görseli
TOKEN = "BURAYA_TOKENIN"  # <-- Token burada
# -------------------

# --- FLASK SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Aktif"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Flask serveri ayrı thread'de başlat
threading.Thread(target=run_flask).start()

# --- DISCORD BOT ---
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Butonların olduğu view ---
class PurposeView(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member

    @discord.ui.button(label="Ekibe Başvuru Yapmak", style=discord.ButtonStyle.green)
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.member:
            await interaction.response.send_message("Bu buton sana ait değil.", ephemeral=True)
            return

        guild = interaction.guild
        role_apply = guild.get_role(APPLY_ROLE_ID)
        role_welcome = guild.get_role(WELCOME_ROLE_ID)
        await self.member.remove_roles(role_welcome)
        await self.member.add_roles(role_apply)
        await interaction.response.send_message("✅ Başvuru Adayı rolü verildi!", ephemeral=True)

    @discord.ui.button(label="Sunucu Reklamı Yapmak", style=discord.ButtonStyle.blurple)
    async def ad_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.member:
            await interaction.response.send_message("Bu buton sana ait değil.", ephemeral=True)
            return

        guild = interaction.guild
        role_ad = guild.get_role(AD_ROLE_ID)
        role_welcome = guild.get_role(WELCOME_ROLE_ID)
        await self.member.remove_roles(role_welcome)
        await self.member.add_roles(role_ad)
        await interaction.response.send_message("📢 Reklamcı rolü verildi!", ephemeral=True)

# --- Sunucuya yeni üye girdiğinde ---
@bot.event
async def on_member_join(member):
    guild = member.guild
    welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
    welcome_role = guild.get_role(WELCOME_ROLE_ID)

    # Yeni üye rolü ver
    await member.add_roles(welcome_role)

    # Hoş geldin mesajı + banner
    file = discord.File(BANNER_PATH, filename="banner.png")
    await welcome_channel.send(
        content=f"Hoş geldin {member.mention} 🎉",
        file=file
    )

    # Altına butonlar
    await welcome_channel.send(
        content="Sunucumuza ne amaç ile katıldınız?",
        view=PurposeView(member)
    )

# --- BOTU ÇALIŞTIR ---
bot.run(TOKEN)

