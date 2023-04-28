import discord
from discord.ext import commands
from discord import Webhook, app_commands
from sdk import Client, Message
import asyncio
import json
import re
import aiohttp


bot = commands.Bot(intents=discord.Intents.all())


sdk = Client("token here")


@bot.tree.command(description="Pong")
async def ping(interaction):
    await interaction.response.send_message("{}ms".format(round(sdk.latency * 1000)))


invite_pattern = re.compile("(https?://)?((ptb|canary)\.)?(discord\.(gg|io)|discord(app)?.com/invite)/[0-9a-zA-Z]+", re.IGNORECASE)
token_pattern = re.compile("[A-Za-z0-9\-_]{23,30}\.[A-Za-z0-9\-_]{6,7}\.[A-Za-z0-9\-_]{27,40}", re.IGNORECASE)


async def message_check(message) -> bool:
    dis_tok = token_pattern.search(message.content)
    invite_link = invite_pattern.search(message.content)
    if dis_tok:
        embed = discord.Embed(description = "Discord認証トークンをグローバルチャットに送信することはできません。", colour = discord.Colour.red())

        await message.channel.send(embed=embed, reference=message)
        await message.add_reaction('❌')
        return True

    elif invite_link:
        embed = discord.Embed(description = "Discordの招待リンクをグローバルチャットに送信することはできません。", colour = discord.Colour.red())

        await message.channel.send(embed = embed, reference=message)
        await message.add_reaction('❌')
        return True

    else:
        return False


def json_load(path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            load = json.load(f)
            return load


@bot.tree.command(name="global",
                        description="グローバルチャットを作成します。すでに作成されている場合はできません。")
@app_commands.checks.has_permissions(manage_channels=True)
async def gc_join(ctx):
    load = json_load("./data/json/global.json")

    try:
        load[str(ctx.guild.id)]
        del load[str(ctx.guild.id)]

        with open("./data/json/global.json", "w") as f1:
            json.dump(load, f1, ensure_ascii=False, indent=4)

        embed = discord.Embed(title="登録を解除しました。",
                                description="Webhookは手動で削除してください。",
                                colour=discord.Colour.red())
        await ctx.respond(embed=embed)

    except KeyError:
        webhook_url = await ctx.channel.create_webhook(name="Global")

        load[str(ctx.guild.id)] = {"url": webhook_url.url, "channel": ctx.channel.id}

        with open("./data/json/global.json", "w", encoding="utf-8") as f1:
            json.dump(load, f1, ensure_ascii=False, indent=4)

        embed = discord.Embed(title="グローバルチャットに接続しました。",
                                colour=discord.Colour.green())
        await ctx.respond(embed=embed)

        await asyncio.sleep(5)

        for v in load.values():
            async with aiohttp.botSession() as session:
                webhook : Webhook = Webhook.from_url(url = v["url"], session = session)

                await webhook.send(content = f"新しいサーバーが参加しました！\nサーバー名: {ctx.guild.name}",
                                    avatar_url= "https://cdn.discordapp.com/embed/avatars/0.png",
                                    username= "[SYSTEM]")

@commands.Cog.listener(name="on_ready")
async def ugc_connect():
    await bot.tree.sync()
    print("UGCへの接続を開始します...")
    await sdk.connect()

@sdk.on("ready")
async def ready():
    print("Ready for ugc")

@sdk.on("message")
async def message(message : Message):
    if message.source == str(message.author.id):
        return

    if message.author.bot:
        return

    load = json_load("data/json/global.json")

    embeds = []
    if message.attachments != []:
        if message.attachments[0].width is not None:
            embed = discord.Embed(title = "添付ファイル")
            embed.set_image(url = message.attachments[0].url)

            embeds.append(embed)

    for k, v in load.items():
        async with aiohttp.botSession() as session:
            try:
                webhook : Webhook = Webhook.from_url(url = v["url"], session = session)

            except ValueError:
                ch = bot.get_channel(v["channel"])

                webhook = await ch.create_webhook(name="Global")
                load[str(message.guild.id)] = {"url": webhook.url, "channel": message.channel.id}

                with open("./data/json/global.json", "w", encoding="utf-8") as f1:
                    json.dump(load, f1, ensure_ascii=False, indent=4)

            await webhook.send(message.content,
                                username= message.author.name,
                                avatar_url= message.author.avatar_url,
                                embeds = embeds)


@commands.Cog.listener(name="on_message")
async def gc_msg(message : discord.Message):
    if message.author.bot:  #BOTの場合は何もせず終了
        return

    if message.guild is None:
        return

    load : dict = json_load("data/json/global.json")
    guild_data = load.get(str(message.guild.id))

    if guild_data is not None:
        if message.channel.id == guild_data["channel"]:
            if await message_check(message):
                return

            await message.add_reaction("🔄")
            urls = []

            for key, value in load.items():
                if key != str(message.guild.id):
                    urls.append(value['url'])

            embeds = []
            if message.attachments != []:
                if message.attachments[0].width is not None:
                    embed = discord.Embed(title = "添付ファイル")
                    embed.set_image(url = message.attachments[0].url)

                    embeds.append(embed)

            await sdk.send_message(message)

            for url in urls:
                async with aiohttp.botSession() as session:
                    try:
                        webhook : Webhook = Webhook.from_url(url = url, session = session)

                    except ValueError:
                        webhook = await message.channel.create_webhook(name="Global")
                        load[str(message.guild.id)] = {"url": webhook.url, "channel": message.channel.id}

                        with open("./data/json/global.json", "w", encoding="utf-8") as f1:
                            json.dump(load, f1, ensure_ascii=False, indent=4)

                    await webhook.send(message.content,
                                        username= message.author.name,
                                        avatar_url= message.author.display_avatar.url,
                                        embeds = embeds)

            await message.add_reaction("✅")

bot.run(bot.config["token"])
