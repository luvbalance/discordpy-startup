from discord.ext import commands
import os
import traceback

token = os.environ['DISCORD_BOT_TOKEN']

#これはbot frameworkを使った書き方(discordpy-startupのサンプルコードのまま)
#bot = commands.Bot(command_prefix='/')
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

#bot.run(token)

# 接続に必要なオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('gogocats logged in')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # 受信メッセージの解析
    params = message.content.split(" ")
    if params[0] == '/test':
        await message.channel.send(params)
        return
    
bot.run(token)
