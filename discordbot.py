from discord.ext import commands
import os
import traceback

bot = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']


#@bot.event
#async def on_command_error(ctx, error):
#    orig_error = getattr(error, "original", error)
#    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
#    await ctx.send(error_msg)


#@bot.command()
#async def ping(ctx):
#    await ctx.send('pong')

#@bot.command()
#async def ping2(ctx):
#    await ctx.send('pong2')

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # お遊び処理
    if message.content.split(",")[0] == '/test':
        xxx  = message.content
        channel = client.get_channel(CHANNEL_ID)
        await channel.send(message.content.split(",")[1])
        return

bot.run(token)
