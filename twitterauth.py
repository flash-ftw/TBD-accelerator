import os
from cryptography.fernet import Fernet
import discord, requests, re, time, json, random
from discord import app_commands
from discord.ext import commands, tasks
from io import BytesIO
from datetime import datetime
from typing import Optional
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import cellFormat, textFormat, format_cell_range, Color
import logging

# -------------------------------
# Logging Setup (optional but recommended)
# -------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------------------
# Google Sheets Credentials
# -------------------------------
GOOGLE_CREDENTIALS = {
  "type": "service_account",
  "project_id": "discordbotbackup",
  "private_key_id": "41c3215084fc2c60afbc007240733060744481f5",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC98mdvTqtflMSv\nC7vLFh0tD14lE4bA4fpgCXU8X9vaOgA9grlkdVJWjeIKiuaOsfGe6o4BUyL1BSkO\nSMcGqep8M0kmh00BWBOSTUOQqXKp0Ig4Sw91z9qQXM5yWZyynrJNZrr7EtK1I3hg\nsRpJrQIloJPHNWe1XRQqqKLojQH58qeiuObVTn5gSh7ub62UWakC0cIhBmLvRM/b\neqnEGyQ1wJyz5OHnE337JEvMK5xelQEsfoyoa/rJzWPmw4hYWEPz1q0JfltpK/gF\nL2N1iGh7/gYi0ROinPYye3oswmjMP1QK0acl34YLXd3v+fdEbJPsAqlenYptj/zj\n+QUL9xLvAgMBAAECggEAU7TMclfX2+JCnuVr176iEuZv1aT6QGwVm1bvrDCOQWhI\nDNNcAfJV28Dg+UZm/kFaum6hL+JESHgCtMHLu5sLs7oiJXGAtPPshA+6k7ioyD8W\nmMAzSvbTWcUcUXY+QNUAvG1mPxj3dE3yUaIadJdil9Rg62wUjO884OO6DwN8+Hl8\nPmig27pVqWqpN5M/oRngCL1TuI0IeRkon8Y3UMsNC2jZ7TLvMCCwJqjnDOE5wTJO\nrWtTzF/+ILsArZLNp83C4TF0M2FDGbMKiIE5BMLB6zXdjWU9e+ZGNHi8DvcOK1Py\n2fDScvDFeJtiVV1ZikgvzqbENSMDG/6pnW3kYR6uiQKBgQD4Tr0rgJPddpc6amx2\noO4SaN52Xrmztdcrym/fScSDlwvI0PxKNQG6XgSMv52KgviMyT5ornxyGn1KDz46\nqumHnlemiMTcc2uRrpaleEo2kfvfOrNlNxMghulI3fzvwZ0+DQz09lCwR9QDFxT2\nYosnB/MHrjm2CMnMrbGsmpktIwKBgQDD1NJ1dAakde7BE1Invv6NMPZip9oHaSMr\nGciPAm6vhmlCa2NfaK1J5lAwvXfgrUdYEdyUIDHCzuloijR61X50TAbKiiSTwVHq\n1PaiKBNZdN0+m0s5tQOP/izB89N+kbpKsoZsW4w+OyiuCIX909nxgYh3YdgvRpgr\njHwtJrI9xQKBgG+mF/Ejk1kVJdKiX7rHicTFWqIm3aEstl9+WucvqCjzFd1p+sbz\nJp/B/pG65v+M/G1xX5p6OoKj3ooaaITArNjKHedHwBzP2SJcOmiUuennojUxk9CC\n/xq1Dtgw2LaFfEqWW6kZyBY7dd0d19MhZChcrq5ZbKGpOfPKdgWCTjW5AoGBAIdO\nq0PgMR69JYReNyujOfqQVA0CcREhwdzr6bl2MsgwlNYBoR2xE9q1ub6TixrAX0Uo\nwkHOpNM3Z+qFY5FjpgXw6dhT7sXwkwswrmCIVCZBKwUxA58RxS5ersosEHupcRBf\nnaWM86+j7I2i8gHZuQK3P3VNM7QmkMm2Pa5syEcJAoGBAKIGXoUBwAoIckpmXa9W\nKO+xooeg2kKKcqfgVFCal/TZBfqltD3Q3pcEhHRq27OsLWHDst4B+mqWdLd4BU0y\n5Ezga5/8x8tALaZ/1UfUlK0RX4BgZb5OUc5ArylucTaO/MyHULxaUaElVTPeLwqU\nAv0GeNmeBhdmpHY/kKPpQJ3h\n-----END PRIVATE KEY-----\n",
  "client_email": "gspread-backup@discordbotbackup.iam.gserviceaccount.com",
  "client_id": "106263493107571013960",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gspread-backup%40discordbotbackup.iam.gserviceaccount.com",
}

# -------------------------------
# Decryption Setup (Fill in the values obtained from encrypt_token.py)
# -------------------------------
ENCRYPTION_KEY = "Zm9V7FnI_KuP6-vR2JJ0s2fFuTThTrvQpqqVC9OIfbM="
ENCRYPTED_TOKEN = b"gAAAAABnwNB3y5u9FgjYcrdNT1iIombJi7h1TzSsMy9KPELJya_156AhjN46iQlcO45Ujm7YowJ7Dhf8SnUaNVVaFj4twJp6T8Dwn5ed9Pzxrp9DsLvSOO3hX9z6IMXz2U5h5mf4M2nDBPaGQCRnuXSNQOw6xbgGg_RwxP451IX7OTzW3BZqeJM="
cipher = Fernet(ENCRYPTION_KEY.encode())
TOKEN = cipher.decrypt(ENCRYPTED_TOKEN).decode()

# -------------------------------
# Persistence
# -------------------------------
DATA_FILE = 'bot_data.json'
def load_data():
    if os.path.exists(DATA_FILE):
        return json.load(open(DATA_FILE, 'r'))
    return {
        "user_credits": {},
        "user_wallets": {},
        "last_daily_claim": {},
        "last_transaction_index": {},
        "user_orders": {},
        "scheduled_orders": [],
        "admin_roles": {}
    }
def save_data(data):
    json.dump(data, open(DATA_FILE, 'w'))
data = load_data()
user_credits = data.get("user_credits", {})
user_wallets = data.get("user_wallets", {})
last_daily_claim = data.get("last_daily_claim", {})
last_transaction_index = data.get("last_transaction_index", {})
user_orders = data.get("user_orders", {})
scheduled_orders = data.get("scheduled_orders", [])
admin_roles = data.get("admin_roles", {})

def update_persistence():
    data_to_save = {
        "user_credits": user_credits,
        "user_wallets": user_wallets,
        "last_daily_claim": last_daily_claim,
        "last_transaction_index": last_transaction_index,
        "user_orders": user_orders,
        "scheduled_orders": scheduled_orders,
        "admin_roles": admin_roles
    }
    save_data(data_to_save)
    backup_data_to_sheet(data_to_save)

# -------------------------------
# Google Sheets Backup Functions
# -------------------------------
def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDENTIALS, scope)
    return gspread.authorize(creds)

def prepare_user_overview_data(guild):
    headers = ["User ID", "Username", "Credits", "Last Daily Reward", "Orders Count"]
    rows = [headers]
    for member in guild.members:
        uid = str(member.id)
        credits = user_credits.get(uid, DEFAULT_CREDITS)
        last_reward = last_daily_claim.get(uid, "N/A")
        if isinstance(last_reward, float):
            last_reward = format_ts(last_reward)
        orders_count = len(user_orders.get(uid, []))
        rows.append([uid, member.name, str(credits), last_reward, str(orders_count)])
    return rows

def prepare_order_details_data(guild):
    headers = ["Order ID", "Username", "User ID", "Service", "Quantity", "Cost", "Status", "Timestamp"]
    rows = [headers]
    for member in guild.members:
        uid = str(member.id)
        for order in user_orders.get(uid, []):
            timestamp = format_ts(order["timestamp"])
            rows.append([str(order["id"]), member.name, uid, order["service"].replace("_", " "), 
                         str(order["quantity"]), str(order["cost"]), order["status"], timestamp])
    return rows

def backup_data_to_sheet(data):
    try:
        client = get_gsheet_client()
        spreadsheet = client.open("BotBackup")
        for guild in bot.guilds:
            overview_title = f"{guild.name} Overview ({guild.id})"
            orders_title = f"{guild.name} Orders ({guild.id})"
            try:
                overview_sheet = spreadsheet.worksheet(overview_title)
            except Exception:
                overview_sheet = spreadsheet.add_worksheet(title=overview_title, rows="200", cols="10")
            try:
                orders_sheet = spreadsheet.worksheet(orders_title)
            except Exception:
                orders_sheet = spreadsheet.add_worksheet(title=orders_title, rows="200", cols="10")
            overview_data = prepare_user_overview_data(guild)
            orders_data = prepare_order_details_data(guild)
            overview_sheet.clear()
            overview_sheet.update(range_name="A1", values=overview_data)
            orders_sheet.clear()
            orders_sheet.update(range_name="A1", values=orders_data)
            header_format = cellFormat(
                backgroundColor=Color(0.2, 0.6, 0.86),
                textFormat=textFormat(bold=True, foregroundColor=Color(1, 1, 1))
            )
            format_cell_range(overview_sheet, "A1:E1", header_format)
            format_cell_range(orders_sheet, "A1:G1", header_format)
            logging.info(f"Updated backup for guild: {guild.name} ({guild.id})")
        logging.info("Backup successful!")
    except Exception as e:
        logging.error("Error during backup: %s", e)

# -------------------------------
# Bot Setup
# -------------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
guild_id = 995147630009139252
ADMIN_ROLE = "Gourmet Chef"

# Global start time for uptime calculation
start_time = time.time()

# -------------------------------
# API and Bot Settings
# -------------------------------
API_KEY = 'f0bc77275a0f45352a6fa2861ebc57be'
COINGECKO_API = 'https://api.coingecko.com/api/v3/simple/price?ids=solana,ethereum&vs_currencies=usd'
ETHERSCAN_API_KEY = '23ABXHGFQ1Z7URG7MRXKCC8PXPEHED1NPW'
SOLANA_RPC_URL = 'https://api.mainnet-beta.solana.com'
SMMA_API_URL = 'https://smmapro.com/api/v2'
DEFAULT_CREDITS, CREDITS_PER_USD = 10, 10
DAILY_REWARD_AMOUNT, DAILY_REWARD_INTERVAL = 10, 86400

# Updated service info with the new services
BOOST_PRICING = {
    "Twitter_Likes": 5,
    "Twitter_Views": 2,   # Updated from 3 to 2 credits per unit
    "Twitter_Followers": 40,
    "Twitter_Retweets": 7
}

SMMA_SERVICE_IDS = {
    "Twitter_Likes": 8133,
    "Twitter_Views": 7998,
    "Twitter_Followers": 7062,
    "Twitter_Retweets": 7058
}

MIN_QUANTITY = {
    "Twitter_Likes": 10,
    "Twitter_Views": 100,
    "Twitter_Followers": 50,
    "Twitter_Retweets": 20
}

# -------------------------------
# Helper Functions
# -------------------------------
def is_valid_solana_address(a):
    return len(a) == 44 and re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', a)
def is_valid_ethereum_address(a):
    return re.match(r'^0x[a-fA-F0-9]{40}$', a)

# For user commands, we leave them open to everyone.
def is_admin(user: discord.Member):
    return any(role.name == ADMIN_ROLE for role in user.roles) or (user == user.guild.owner)

# -------------------------------
# Restricted Role Check
# -------------------------------
# Use the provided admin role ID.
RESTRICTED_FUNCTION_ROLE_ID = 995344859319775292

def has_restricted_role(user: discord.Member):
    return any(role.id == RESTRICTED_FUNCTION_ROLE_ID for role in user.roles)

def format_ts(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

# -------------------------------
# USER COMMANDS
# -------------------------------

@bot.tree.command(name='balance', description='💰 Check your current credit balance')
async def balance(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    await interaction.followup.send(
        f'💎 **Balance:** {interaction.user.mention}, you have **{user_credits.get(uid, DEFAULT_CREDITS)}** credits.',
        ephemeral=True
    )

@bot.tree.command(name='dailyreward', description='🎁 Claim your daily free credits')
async def daily_reward(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    now = time.time()
    last = last_daily_claim.get(uid, 0)
    if now - last < DAILY_REWARD_INTERVAL:
        r = int(DAILY_REWARD_INTERVAL - (now - last))
        await interaction.followup.send(
            f'⏳ **Hold on!** Next daily reward in **{r // 3600}h {r % 3600 // 60}m**.',
            ephemeral=True
        )
        return
    last_daily_claim[uid] = now
    user_credits[uid] = user_credits.get(uid, DEFAULT_CREDITS) + DAILY_REWARD_AMOUNT
    update_persistence()
    await interaction.followup.send(
        f'🎉 {interaction.user.mention}, you received **{DAILY_REWARD_AMOUNT}** free credits!',
        ephemeral=True
    )

@bot.tree.command(name='pricelist', description='📜 View boost service pricing')
async def pricelist(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    e = discord.Embed(title="✨ Boost Service Pricing", color=0x1ABC9C)
    for s, c in BOOST_PRICING.items():
        m = MIN_QUANTITY.get(s, 1)
        emoji = "❤️" if s == "Twitter_Likes" else "👀" if s == "Twitter_Views" else "👥" if s == "Twitter_Followers" else "🔄"
        e.add_field(
            name=f"{emoji} {s.replace('_', ' ')}",
            value=f"**Cost:** `{c}` credits/unit\n**Min Qty:** `{m}`",
            inline=False
        )
    e.set_footer(text="Use /buyboost to purchase services.")
    await interaction.followup.send(embed=e, ephemeral=True)

@bot.tree.command(name='setwallet', description='🔐 Set your wallet address with network selection')
@app_commands.describe(network='Select your network', wallet='Enter your wallet address')
@app_commands.choices(network=[
    app_commands.Choice(name="Solana", value="solana"),
    app_commands.Choice(name="Ethereum", value="ethereum")
])
async def set_wallet(interaction: discord.Interaction, network: app_commands.Choice[str], wallet: str):
    await interaction.response.defer(ephemeral=True)
    if network.value == "solana" and not is_valid_solana_address(wallet):
        await interaction.followup.send('❌ **Error:** Not a valid Solana address.', ephemeral=True)
        return
    if network.value == "ethereum" and not is_valid_ethereum_address(wallet):
        await interaction.followup.send('❌ **Error:** Not a valid Ethereum address.', ephemeral=True)
        return
    user_wallets[str(interaction.user.id)] = {"network": network.value, "address": wallet}
    update_persistence()
    await interaction.followup.send(
        f'✅ {interaction.user.mention}, your **{network.name}** wallet is set!',
        ephemeral=True
    )

@bot.tree.command(name='faq', description='❓ Frequently Asked Questions')
async def faq(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="❓ FAQ", color=0x00BFFF)
    embed.add_field(name="What is this bot?", value="It's an NFT/crypto-powered engagement bot that offers boost services and more.", inline=False)
    embed.add_field(name="How do I earn credits?", value="You can claim daily rewards and even gamble credits for a chance to win extra.", inline=False)
    embed.add_field(name="Is my data secure?", value="Yes, all data is securely backed up to our secured database.", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name='notifications', description='🔔 Manage your notification settings')
async def notifications(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="🔔 Notifications", color=0xFFD700)
    embed.add_field(name="Settings", value="This feature is under development. Stay tuned for updates!", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name='gamble', description='🎲 Gamble some credits for a chance to win more')
@app_commands.describe(bet='Amount of credits to gamble')
async def gamble(interaction: discord.Interaction, bet: int):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    current = user_credits.get(uid, DEFAULT_CREDITS)
    if bet > current:
        await interaction.followup.send("❌ You cannot bet more credits than you have.", ephemeral=True)
        return
    outcome = random.choice(["win", "lose"])
    if outcome == "win":
        winnings = bet  # doubling your bet as gain
        user_credits[uid] = current + winnings
        result_text = f"🎉 You won! You gained {winnings} credits."
    else:
        user_credits[uid] = current - bet
        result_text = f"😢 You lost {bet} credits."
    update_persistence()
    await interaction.followup.send(result_text, ephemeral=True)

@bot.tree.command(name='uptime', description='⏱️ Show the bot uptime')
async def uptime(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    now = time.time()
    uptime_seconds = int(now - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    embed = discord.Embed(title="⏱️ Bot Uptime", color=0xFFA500)
    embed.add_field(name="Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name='buyboost', description='🚀 Purchase boost services with your credits')
@app_commands.describe(service='Select a service', link='Provide the tweet URL', quantity='Enter number of units')
@app_commands.choices(service=[
    app_commands.Choice(name="Twitter Likes", value="Twitter_Likes"),
    app_commands.Choice(name="Twitter Views", value="Twitter_Views"),
    app_commands.Choice(name="Twitter Followers", value="Twitter_Followers"),
    app_commands.Choice(name="Twitter Retweets", value="Twitter_Retweets")
])
async def buy_boost(interaction: discord.Interaction, service: app_commands.Choice[str], link: str, quantity: int):
    await interaction.response.defer(ephemeral=True)
    print(f"buyboost command invoked by {interaction.user} with service {service.value}")
    uid = str(interaction.user.id)
    s = service.value
    link = link.strip().rstrip(";")
    if not (link.startswith("https://twitter.com/") or link.startswith("https://x.com/")):
        await interaction.followup.send(
            '❌ **Invalid Tweet URL:** Provide a valid tweet URL (e.g. `https://twitter.com/username/status/1234567890`).',
            ephemeral=True
        )
        return
    if quantity < MIN_QUANTITY.get(s, 1):
        await interaction.followup.send(
            f'❌ **Minimum Quantity:** For **{service.name}**, min is `{MIN_QUANTITY.get(s)}`.',
            ephemeral=True
        )
        return
    cost = BOOST_PRICING[s] * quantity
    balance_now = user_credits.get(uid, DEFAULT_CREDITS)
    if balance_now < cost:
        await interaction.followup.send(
            '❌ **Insufficient Credits:** You need more credits for this order.',
            ephemeral=True
        )
        return
    payload = {'key': API_KEY, 'action': 'add', 'service': SMMA_SERVICE_IDS[s], 'link': link, 'quantity': quantity}
    try:
        r = requests.get(SMMA_API_URL, params=payload)
        if r.status_code == 200:
            user_credits[uid] = balance_now - cost
            order = {
                "id": int(time.time()),
                "service": s,
                "link": link,
                "quantity": quantity,
                "cost": cost,
                "timestamp": time.time(),
                "status": "Pending"
            }
            user_orders.setdefault(uid, []).append(order)
            update_persistence()
            await interaction.followup.send(
                f'✅ **Order Placed!** Your order for **{quantity} {service.name}** boost(s) has been processed and **{cost}** credits deducted.',
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                '❌ **Error:** Problem processing your order. Try later.',
                ephemeral=True
            )
    except Exception as e:
        await interaction.followup.send(f'❌ **Exception:** {e}', ephemeral=True)

@bot.tree.command(name='dashboard', description='📊 View your personal account dashboard')
async def dashboard(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    b = user_credits.get(uid, DEFAULT_CREDITS)
    orders = user_orders.get(uid, [])
    total_orders = len(orders)
    total_spent = sum(o["cost"] for o in orders)
    avg_cost = total_spent / total_orders if total_orders else 0
    e = discord.Embed(title=f"{interaction.user.name}'s Dashboard", color=0x3498DB)
    e.add_field(name="💰 Balance", value=f"**{b}** credits", inline=True)
    w = user_wallets.get(uid)
    if w:
        net = w.get("network") if isinstance(w, dict) else ("Ethereum" if w.startswith("0x") else "Solana")
        addr = w.get("address") if isinstance(w, dict) else w
        e.add_field(name="🔐 Wallet", value=f"**{net.capitalize()}**\n`{addr}`", inline=True)
    else:
        e.add_field(name="🔐 Wallet", value="*Not set*", inline=True)
    e.add_field(name="⏰ Last Daily Reward", value=format_ts(last_daily_claim.get(uid)) if last_daily_claim.get(uid) else "Never claimed", inline=True)
    e.add_field(name="🛒 Total Orders", value=f"`{total_orders}`", inline=True)
    e.add_field(name="💸 Total Spent", value=f"`{total_spent}` credits", inline=True)
    e.add_field(name="📊 Avg Order Cost", value=f"`{avg_cost:.2f}` credits", inline=True)
    if orders:
        lines = "".join([
            f'`#{o["id"]}` **{o["service"].replace("_", " ")}** - Qty: `{o["quantity"]}` - Cost: **{o["cost"]}**\n_{format_ts(o["timestamp"])}_\n'
            for o in orders[-5:]
        ])
        e.add_field(name="🛒 Recent Orders", value=lines, inline=False)
    else:
        e.add_field(name="🛒 Orders", value="No orders placed yet.", inline=False)
    e.set_footer(text="Keep boosting and earning!")
    await interaction.followup.send(embed=e, ephemeral=True)

@bot.tree.command(name='orderstatus', description='📦 Check status of your active orders')
async def order_status(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    orders = user_orders.get(uid, [])
    if not orders:
        await interaction.followup.send("ℹ️ You have no orders.", ephemeral=True)
        return
    e = discord.Embed(title="📦 Order Status", color=0x00FF00)
    for o in orders:
        status = o.get("status", "Unknown")
        e.add_field(
            name=f'Order `#{o["id"]}`',
            value=f'**Service:** {o["service"].replace("_", " ")}\n'
                  f'**Qty:** {o["quantity"]}\n'
                  f'**Cost:** {o["cost"]} credits\n'
                  f'**Status:** **{status}**\n'
                  f'**Time:** {format_ts(o["timestamp"])}',
            inline=False
        )
    await interaction.followup.send(embed=e, ephemeral=True)

@bot.tree.command(name='analytics', description='📊 View interactive analytics of your orders')
async def analytics(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    orders = user_orders.get(uid, [])
    if not orders:
        await interaction.followup.send("ℹ️ No order data available for analytics.", ephemeral=True)
        return
    orders_sorted = sorted(orders, key=lambda o: o["timestamp"])
    times = [datetime.fromtimestamp(o["timestamp"]) for o in orders_sorted]
    costs = [o["cost"] for o in orders_sorted]
    plt.figure(figsize=(6, 4))
    plt.plot(times, costs, marker='o')
    plt.title('Order Cost Over Time')
    plt.xlabel('Time')
    plt.ylabel('Cost (credits)')
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await interaction.followup.send("📈 Here are your analytics:", file=discord.File(buf, 'analytics.png'), ephemeral=True)
    plt.close()

@bot.tree.command(name='orderhistory', description='📜 View your order history with filters')
@app_commands.describe(service='Filter by service (optional)', start_date='Start date YYYY-MM-DD (optional)', end_date='End date YYYY-MM-DD (optional)')
@app_commands.choices(service=[
    app_commands.Choice(name="Twitter Likes", value="Twitter_Likes"),
    app_commands.Choice(name="Twitter Views", value="Twitter_Views")
])
async def orderhistory(interaction: discord.Interaction, service: Optional[app_commands.Choice[str]] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    orders = user_orders.get(uid, [])
    filtered = orders
    if service:
        filtered = [o for o in filtered if o["service"] == service.value]
    if start_date:
        try:
            start_ts = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
            filtered = [o for o in filtered if o["timestamp"] >= start_ts]
        except Exception:
            await interaction.followup.send("❌ **Invalid start date.** Use YYYY-MM-DD.", ephemeral=True)
            return
    if end_date:
        try:
            end_ts = datetime.strptime(end_date, "%Y-%m-%d").timestamp()
            filtered = [o for o in filtered if o["timestamp"] <= end_ts]
        except Exception:
            await interaction.followup.send("❌ **Invalid end date.** Use YYYY-MM-DD.", ephemeral=True)
            return
    if not filtered:
        await interaction.followup.send("ℹ️ No orders found with given filters.", ephemeral=True)
        return
    e = discord.Embed(title="📜 Order History", color=0xFFA500)
    for o in filtered[-10:]:
        status = o.get("status", "Unknown")
        e.add_field(
            name=f'Order `#{o["id"]}`',
            value=f'**Service:** {o["service"].replace("_", " ")}\n'
                  f'**Qty:** {o["quantity"]}\n'
                  f'**Cost:** {o["cost"]}\n'
                  f'**Status:** {status}\n'
                  f'**Time:** {format_ts(o["timestamp"])}',
            inline=False
        )
    await interaction.followup.send(embed=e, ephemeral=True)

@bot.tree.command(name='scheduleorder', description='⏰ Schedule a boost order for later')
@app_commands.describe(service='Select a service', link='Tweet URL', quantity='Units', delay='Delay in minutes')
@app_commands.choices(service=[
    app_commands.Choice(name="Twitter Likes", value="Twitter_Likes"),
    app_commands.Choice(name="Twitter Views", value="Twitter_Views")
])
async def scheduleorder(interaction: discord.Interaction, service: app_commands.Choice[str], link: str, quantity: int, delay: int):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    if not (link.startswith("https://twitter.com/") or link.startswith("https://x.com/")):
        await interaction.followup.send('❌ **Invalid Tweet URL.**', ephemeral=True)
        return
    if quantity < MIN_QUANTITY.get(service.value, 1):
        await interaction.followup.send(
            f'❌ **Minimum Quantity:** For **{service.name}**, min is `{MIN_QUANTITY.get(service.value)}`.',
            ephemeral=True
        )
        return
    cost = BOOST_PRICING[service.value] * quantity
    balance_now = user_credits.get(uid, DEFAULT_CREDITS)
    if balance_now < cost:
        await interaction.followup.send('❌ **Insufficient Credits.**', ephemeral=True)
        return
    user_credits[uid] = balance_now - cost
    update_persistence()
    order = {
        "id": int(time.time()),
        "service": service.value,
        "link": link,
        "quantity": quantity,
        "cost": cost,
        "timestamp": time.time(),
        "status": "Scheduled"
    }
    exec_at = time.time() + delay * 60
    scheduled_orders.append({"user_id": uid, "order": order, "execute_at": exec_at})
    update_persistence()
    await interaction.followup.send(
        f'✅ **Order Scheduled!** Your order for **{quantity} {service.name}** will execute in **{delay}** minute(s) and **{cost}** credits deducted.',
        ephemeral=True
    )

@bot.tree.command(name='livefeed', description='📡 View a live feed of recent orders')
async def livefeed(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    all_orders = []
    for uid, orders in user_orders.items():
        for o in orders:
            all_orders.append((uid, o))
    if not all_orders:
        await interaction.followup.send("ℹ️ No orders have been placed yet.", ephemeral=True)
        return
    all_orders.sort(key=lambda x: x[1]["timestamp"], reverse=True)
    e = discord.Embed(title="📡 Live Order Feed", color=0x00BFFF)
    for uid, o in all_orders[:10]:
        user_obj = bot.get_user(int(uid))
        username = user_obj.name if user_obj else uid
        status = o.get("status", "Unknown")
        e.add_field(
            name=f'Order `#{o["id"]}` by **{username}**',
            value=f'**Service:** {o["service"].replace("_", " ")}\n'
                  f'**Qty:** {o["quantity"]}\n'
                  f'**Cost:** {o["cost"]}\n'
                  f'**Status:** {status}\n'
                  f'**Time:** {format_ts(o["timestamp"])}',
            inline=False
        )
    await interaction.followup.send(embed=e, ephemeral=True)

@bot.tree.command(name='roimetrics', description='📈 View your ROI & performance metrics')
async def roimetrics(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    uid = str(interaction.user.id)
    orders = user_orders.get(uid, [])
    if not orders:
        await interaction.followup.send("ℹ️ No order data available.", ephemeral=True)
        return
    tot = len(orders)
    spent = sum(o["cost"] for o in orders)
    avg = spent / tot if tot else 0
    e = discord.Embed(title="📈 ROI & Performance Metrics", color=0x8E44AD)
    e.add_field(name="Total Orders", value=f"`{tot}`", inline=True)
    e.add_field(name="Total Spent", value=f"`{spent}` credits", inline=True)
    e.add_field(name="Average Order Cost", value=f"`{avg:.2f}` credits", inline=True)
    roi = (tot * 10) / spent if spent > 0 else 0
    e.add_field(name="Simulated ROI", value=f"`{roi:.2f}`", inline=True)
    await interaction.followup.send(embed=e, ephemeral=True)

# -------------------------------
# ADMIN COMMANDS (Restricted to the specified role)
# -------------------------------

@bot.tree.command(name='setadminrole', description='⚙️ Set the admin role for this server (One-time setup)')
async def set_admin_role(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    if not has_restricted_role(interaction.user):
        await interaction.followup.send("❌ You do not have permission to set the admin role.", ephemeral=True)
        return
    if str(interaction.guild.id) in admin_roles:
        await interaction.followup.send("❌ Admin role is already set and cannot be changed.", ephemeral=True)
        return
    admin_roles[str(interaction.guild.id)] = str(role.id)
    update_persistence()
    await interaction.followup.send(f"✅ Admin role set to **{role.name}** for this server.", ephemeral=True)

@bot.tree.command(name='adminlog', description='📜 Admin: View last 10 transactions')
async def admin_log(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not has_restricted_role(interaction.user):
        await interaction.followup.send("❌ You do not have permission to view the admin log.", ephemeral=True)
        return
    log = "\n".join([f'User `{uid}`: **{c}** credits' for uid, c in list(user_credits.items())[-10:]])
    await interaction.followup.send(f'📜 **Last 10 Transactions:**\n{log}', ephemeral=True)

@bot.tree.command(name='checktransactions', description='🔄 Admin: Force check for new transactions')
async def check_transactions_now(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not has_restricted_role(interaction.user):
        await interaction.followup.send("❌ You do not have permission to force check transactions.", ephemeral=True)
        return
    await monitor_transactions()
    await interaction.followup.send('🔄 Checked transactions.', ephemeral=True)

@bot.tree.command(name='addcredits', description='➕ Admin: Add credits to a user')
@app_commands.describe(user='Select a user', amount='Amount to add')
async def add_credits(interaction: discord.Interaction, user: discord.Member, amount: int):
    await interaction.response.defer(ephemeral=True)
    if not has_restricted_role(interaction.user):
        await interaction.followup.send("❌ You do not have permission to add credits.", ephemeral=True)
        return
    uid = str(user.id)
    user_credits[uid] = user_credits.get(uid, DEFAULT_CREDITS) + amount
    update_persistence()
    await interaction.followup.send(f'✅ Added **{amount}** credits to {user.mention}.', ephemeral=True)

@bot.tree.command(name='removekredits', description='➖ Admin: Remove credits from a user')
@app_commands.describe(user='Select a user', amount='Amount to remove')
async def remove_credits(interaction: discord.Interaction, user: discord.Member, amount: int):
    await interaction.response.defer(ephemeral=True)
    if not has_restricted_role(interaction.user):
        await interaction.followup.send("❌ You do not have permission to remove credits.", ephemeral=True)
        return
    uid = str(user.id)
    user_credits[uid] = max(0, user_credits.get(uid, DEFAULT_CREDITS) - amount)
    update_persistence()
    await interaction.followup.send(f'✅ Removed **{amount}** credits from {user.mention}.', ephemeral=True)

@bot.tree.command(name='totalcredits', description='💰 Admin: View total credits of a user')
@app_commands.describe(user='Select a user')
async def total_credits(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral=True)
    if not has_restricted_role(interaction.user):
        await interaction.followup.send("❌ You do not have permission to view total credits.", ephemeral=True)
        return
    await interaction.followup.send(f'💰 {user.mention} has **{user_credits.get(str(user.id), DEFAULT_CREDITS)}** credits.', ephemeral=True)

@bot.command()
async def sync(ctx):
    if not has_restricted_role(ctx.author):
        await ctx.send("❌ You do not have permission to sync commands.")
        return
    try:
        await bot.tree.sync(guild=discord.Object(id=guild_id))
        await ctx.send("✅ Slash commands synced!")
    except Exception as e:
        await ctx.send(f"❌ Sync error: {e}")

# -------------------------------
# BACKGROUND TASKS
# -------------------------------
async def monitor_transactions():
    for uid, w_obj in user_wallets.items():
        if isinstance(w_obj, dict):
            wallet, network = w_obj.get("address"), w_obj.get("network")
        else:
            wallet, network = w_obj, "ethereum" if w_obj.startswith("0x") else "solana"
        if network == "ethereum":
            url = f'https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&startblock=0&endblock=99999999&sort=asc&apikey={ETHERSCAN_API_KEY}'
            try:
                r = requests.get(url)
                if r.status_code == 200 and r.json().get("status") == "1":
                    txs = r.json().get("result", [])
                    last = last_transaction_index.get(wallet, 0)
                    for tx in txs[last:]:
                        v = int(tx.get("value", 0)) / 1e18
                        eth_price = requests.get(COINGECKO_API).json().get("ethereum", {}).get("usd", 0)
                        credits = int(v * eth_price * CREDITS_PER_USD)
                        if credits > 0:
                            user_credits[uid] = user_credits.get(uid, DEFAULT_CREDITS) + credits
                    last_transaction_index[wallet] = len(txs)
                    update_persistence()
            except Exception as e:
                print(f"ETH error for {wallet}: {e}")
        elif network == "solana":
            try:
                r = requests.post(
                    SOLANA_RPC_URL,
                    json={"jsonrpc": "2.0", "id": 1, "method": "getSignaturesForAddress", "params": [wallet, {"limit": 10}]},
                    headers={'Content-Type': 'application/json'}
                )
                if r.status_code == 200:
                    txs = r.json().get("result", [])
                    last = last_transaction_index.get(wallet, 0)
                    for tx in txs[last:]:
                        user_credits[uid] = user_credits.get(uid, DEFAULT_CREDITS) + int(1 * CREDITS_PER_USD)
                    last_transaction_index[wallet] = len(txs)
                    update_persistence()
            except Exception as e:
                print(f"Solana error for {wallet}: {e}")

@tasks.loop(seconds=30)
async def order_status_updater():
    now = time.time()
    changed = False
    for uid, orders in user_orders.items():
        for order in orders:
            if order.get("status") == "Pending" and now - order["timestamp"] >= 120:
                order["status"] = "Completed"
                changed = True
                user_obj = bot.get_user(int(uid))
                if user_obj:
                    try:
                        await user_obj.send(f'✅ Your order `#{order["id"]}` for **{order["service"].replace("_", " ")}** boost is now **Completed**!')
                    except Exception as e:
                        print(f"DM error for {uid}: {e}")
    if changed:
        update_persistence()

@tasks.loop(seconds=60)
async def scheduled_order_executor():
    now = time.time()
    to_exec = [s for s in scheduled_orders if s["execute_at"] <= now]
    if to_exec:
        for s in to_exec:
            uid = s["user_id"]
            order = s["order"]
            order["status"] = "Pending"
            user_orders.setdefault(uid, []).append(order)
            scheduled_orders.remove(s)
            user_obj = bot.get_user(int(uid))
            if user_obj:
                try:
                    await user_obj.send(f'🚀 Your scheduled order `#{order["id"]}` for **{order["service"].replace("_", " ")}** is now processing!')
                except Exception as e:
                    print(f"Scheduled order DM error for {uid}: {e}")
        update_persistence()

@tasks.loop(seconds=60)
async def transaction_monitor_loop():
    await monitor_transactions()

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Sync error: {e}")
    activity = discord.Activity(type=discord.ActivityType.watching, name="TBD HATERS BURN")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    transaction_monitor_loop.start()
    order_status_updater.start()
    scheduled_order_executor.start()
    print("🤖 Bot ready & monitoring transactions...")

print("Decrypted token:", TOKEN)
bot.run(TOKEN)
