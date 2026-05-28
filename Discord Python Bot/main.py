import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

import os
import gspread

from datetime import datetime

from google.oauth2.service_account import Credentials

load_dotenv()

TOKEN = os.getenv("TOKEN")

# =========================
# IDs
# =========================

REVIEW_ROLE_ID = 1507023384804986971

REVIEW_CHANNEL_ID = 1507019280565141544

ACCOUNT_CHANNEL_ID = 1509365219015528528

# =========================
# Google Sheets
# =========================

SCOPES = [

    "https://www.googleapis.com/auth/spreadsheets",

    "https://www.googleapis.com/auth/drive"

]

import json

creds_dict = json.loads(
    os.getenv("GOOGLE_CREDS")
)

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

gc = gspread.authorize(creds)

sheet = gc.open(

    "工作室記錄"

).sheet1

# =========================
# Bot Setup
# =========================

intents = discord.Intents.default()

intents.message_content = True

intents.members = True

bot = commands.Bot(

    command_prefix=".",

    intents=intents

)

# =========================
# Ready
# =========================

# =========================
# Ready
# =========================

@bot.event
async def on_ready():

    try:

        bot.tree.clear_commands(guild=None)

        synced = await bot.tree.sync()

        print(f"同步 {len(synced)} 個指令")

    except Exception as e:

        print(e)

    print(f"{bot.user} 已上線")

# =========================
# .r
# =========================

@bot.command()

async def r(

    ctx,

    amount:int

):

    rm = amount * 0.02

    twd = amount * 0.17

    embed = discord.Embed(

        title="💰 Robux 計算",

        color=0x00b0f4

    )

    embed.description=(

        f"**{amount} Robux In Game Gift**\n\n"

        f"🇲🇾 馬幣：RM{rm:.2f}\n"

        f"🇹🇼 台幣：{twd:.2f}台"

    )

    await ctx.reply(

        embed=embed

    )

# =========================
# /math
# =========================

@bot.tree.command(

    name="math",

    description="基本計算"

)

async def math(

    interaction:discord.Interaction,

    equation:str

):

    try:

        result=eval(equation)

        await interaction.response.send_message(

            f"🧮 結果：{result}",

            ephemeral=True

        )

    except:

        await interaction.response.send_message(

            "❌ 算式錯誤",

            ephemeral=True

        )

# =========================
# 評價 Modal
# =========================

class ReviewModal(

    discord.ui.Modal,

    title="填寫評價"

):

    stars=discord.ui.TextInput(

        label="星數(1-5)"

    )

    review=discord.ui.TextInput(

        label="評價內容",

        style=discord.TextStyle.paragraph

    )

    def __init__(

        self,

        image=None

    ):

        super().__init__()

        self.image=image

    async def on_submit(

        self,

        interaction:discord.Interaction

    ):

        try:

            star=int(

                self.stars.value

            )

            if star<1 or star>5:

                raise Exception()

        except:

            return await interaction.response.send_message(

                "❌ 星數只能1-5",

                ephemeral=True

            )

        channel=bot.get_channel(

            REVIEW_CHANNEL_ID

        )

        embed=discord.Embed(

            title="🌟 新客戶評價",

            color=0xFFD700

        )

        embed.add_field(

            name="客戶",

            value=interaction.user.mention,

            inline=True

        )

        embed.add_field(

            name="星數",

            value="⭐"*star,

            inline=True

        )

        embed.add_field(

            name="評價內容",

            value=self.review.value,

            inline=False

        )

        embed.set_thumbnail(

            url=interaction.user.display_avatar.url

        )

        if self.image:

            embed.set_image(

                url=self.image

            )

        await channel.send(

            embed=embed

        )

        await interaction.response.send_message(

            "✅ 感謝你的評價",

            ephemeral=True

        )

class ReviewView(

    discord.ui.View

):

    def __init__(

        self,

        image=None

    ):

        super().__init__(

            timeout=None

        )

        self.image=image

    @discord.ui.button(

        label="填寫評價",

        style=discord.ButtonStyle.primary

    )

    async def button(

        self,

        interaction,

        button

    ):

        await interaction.response.send_modal(

            ReviewModal(

                self.image

            )

        )

# =========================
# /評價
# =========================

@bot.tree.command(

    name="評價",

    description="發送評價"

)

async def review(

    interaction:discord.Interaction,

    圖片:discord.Attachment=None

):

    role=interaction.guild.get_role(

        REVIEW_ROLE_ID

    )

    if role not in interaction.user.roles:

        return await interaction.response.send_message(

            "❌ 沒有權限",

            ephemeral=True

        )

    embed=discord.Embed(

        title="🌟 客戶評價",

        description="請點按鈕填寫",

        color=0xFFD700

    )

    image=None

    if 圖片:

        image=圖片.url

        embed.set_image(

            url=image

        )

    await interaction.response.send_message(

        embed=embed,

        view=ReviewView(

            image

        )

    )

# =========================
# /記帳
# =========================

@app_commands.command(

    name="記帳",

    description="新增記帳"

)

@app_commands.choices(

    貨幣=[

        app_commands.Choice(

            name="MYR",

            value="MYR"

        ),

        app_commands.Choice(

            name="TWD",

            value="TWD"

        )

    ]

)

async def 記帳(

    interaction:discord.Interaction,

    用戶:discord.Member,

    商品:str,

    金額:float,

    貨幣:app_commands.Choice[str]

):

    currency=貨幣.value

    channel=bot.get_channel(

        ACCOUNT_CHANNEL_ID

    )

    embed=discord.Embed(

        title="🧾 新記帳",

        color=0x2ECC71

    )

    embed.add_field(

        name="購買用戶",

        value=f"{用戶.mention}\nID:`{用戶.id}`",

        inline=False

    )

    embed.add_field(

        name="商品",

        value=商品,

        inline=False

    )

    embed.add_field(

        name="金額",

        value=f"{currency} {金額}",

        inline=False

    )

    embed.add_field(

        name="記錄人",

        value=interaction.user.mention,

        inline=False

    )

    await channel.send(

        embed=embed

    )

    sheet.append_row([

        datetime.now().strftime(

            "%Y-%m-%d %H:%M"

        ),

        str(用戶),

        str(用戶.id),

        商品,

        currency,

        金額,

        str(interaction.user)

    ])

    await interaction.response.send_message(

        "✅ 已成功記帳",

        ephemeral=True

    )

bot.tree.add_command(

    記帳

)

bot.run(

    TOKEN

)
