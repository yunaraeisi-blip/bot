import discord
from discord.ext import commands
import g4f
import sympy
import yt_dlp
import asyncio
#do not change anything at all the script will ask the token it self when it run
gf156 = input("token:")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
async def get_ai_response(prompt):
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "user", "content": f"reply casually like a discord user, short, lowercase only: {prompt}"}]
        )
        return response.lower()
    except Exception as e:
        print("ai error:", e)
        return "idk honestly"
async def fix_music_query(query):
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_35_turbo,
            messages=[{"role": "user", "content": f"""turn this typo music search into the most likely real song name.only reply with the corrected search.search:{query}"""}]
        )
        fixed = response.strip()
        print("fixed query:", fixed)
        return fixed
    except Exception as e:
        print("music fix error:", e)
        return query
ydl_opts = {"format": "bestaudio/best", "quiet": True, "default_search": "ytsearch1"}
@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
@bot.command()
async def ping(ctx):
    await ctx.send("pong")
@bot.command()
async def math(ctx, *, q):
    try:
        result = sympy.simplify(q)
        await ctx.send(f"it's {result}")
    except:
        await ctx.send("i'm not sure about that one")
@bot.command()
async def say(ctx, *, msg):
    try:
        await ctx.message.delete()
    except:
        pass
    await ctx.send(msg)
@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("join a voice channel first")
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    await ctx.send("joined")
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    await ctx.send("left vc")
@bot.command()
async def spam(ctx, amount: int, *, text):
    if amount < 51:
        for i in range(amount):
            await ctx.send(text)
            await asyncio.sleep(0.5)
    else:
        await ctx.send("Because Of Spamming Ban, The Max Spam Is 50")
@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    await ctx.send("stopped")
@bot.command()
async def play(ctx, *, query):
    print("play command used")
    if not ctx.author.voice:
        await ctx.send("join a voice channel first")
        return
    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    vc = ctx.voice_client

    async with ctx.typing():
        try:
            fixed_query = await fix_music_query(query)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"ytsearch5:{fixed_query} song",
                    download=False
                )

                if "entries" not in info or not info["entries"]:
                    await ctx.send("nothing found")
                    return

                selected = None
                banned_words = [
                    "tutorial",
                    "gameplay",
                    "reaction",
                    "podcast",
                    "interview",
                    "news",
                    "livestream",
                    "stream",
                    "movie",
                    "clip"
                ]

                for entry in info["entries"]:

                    if not entry:
                        continue

                    title = entry.get("title", "").lower()
                    duration = entry.get("duration", 0)
                    if duration and duration > 900:
                        continue

                    # skip bad matches
                    if any(word in title for word in banned_words):
                        continue
                    selected = entry
                    break
                if not selected:
                    await ctx.send("no music found")
                    return
                title = selected.get("title", "Unknown Title")
                url = selected["url"]
                print("found:", title)
            source = await discord.FFmpegOpusAudio.from_probe(
                url,
                method="fallback"
            )
            if vc.is_playing():
                vc.stop()
            vc.play(source)
            await ctx.send(f"Playing: {title}")
        except Exception as e:
            print("play error:", e)
            await ctx.send(f"error: {e}")
bot.run("gf156")
