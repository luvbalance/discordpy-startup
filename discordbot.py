import discord
import datetime
import time
from discord.ext import tasks
from discord.ext import commands
import os
import traceback
import re   #正規表現

#ヘルプ
def helpstr():
    retstr = '**使い方**\n'
    retstr += '\t/gogohelp\tヘルプ表示\n'
    retstr += '\t/init\t待機状況初期化\n'
    retstr += '\t/stat\t待機状況表示\n'
    retstr += '\t/xyz (rw1) (rw2) (rw3)\t待機状況登録\n'
    retstr += '\t\tx...待機数(0～3)\n'
    retstr += '\t\ty...無料回復数(0～9)\n'
    retstr += '\t\tz...修理数(0～3)\n'
    retstr += '\t\t※修理数は待機数に応じて補正あり\n'
    retstr += '\t\t(rw1)...修理時間(1台目)(省略可能)\n'
    retstr += '\t\t(rw2)...修理時間(2台目)(省略可能)\n'
    retstr += '\t\t(rw3)...修理時間(3台目)(省略可能)\n'
    retstr += '\t\t※修理時間の単位は分\n'
    retstr += '\t\t※修理時間指定数に対して\n'
    retstr += '\t\t　修理時間を少なく指定した場合は\n'
    retstr += '\t\t　修理時間を\n'
    retstr += '\t\t　全台に適用します\n'
    retstr += '\t\t\n'
    retstr += '\t\tex.\n'
    retstr += '\t\t/320\n'
    retstr += '\t\t/102 120 110\n'
    return retstr

#半角数値文字列をアイコン文字列に置き換えます
def NumIcomStr(numstr):
    retstr = ''
    numstrlist = list(numstr)
    for value in numstrlist:
        retstr+=NumIcon(value)
    return retstr

#半角数字1文字をアイコンに置き換えます
def NumIcon(value):
    ret = ''
    if value=='0':
        ret = ':zero:'
    elif value=='1':
        ret = ':one:'
    elif value=='2':
        ret = ':two:'
    elif value=='3':
        ret = ':three:'
    elif value=='4':
        ret = ':four:'
    elif value=='5':
        ret = ':five:'
    elif value=='6':
        ret = ':six:'
    elif value=='7':
        ret = ':seven:'
    elif value=='8':
        ret = ':eight:'
    elif value=='9':
        ret = ':nine:'

    return ret

#メンバー一人分の状態管理クラス
class Statinfo:
    def __init__(self, user, wait, recover, repair, rw1, rw2, rw3):
        self.User = user
        self.recover = recover
        self.repair = repair
        self.rw1 = rw1
        self.rw2 = rw2
        self.rw3 = rw3
    def stat(self):
        return str(self.wait) + str(self.recover) +str(self.repair)
    def showstat(self):
        retstr = NumIcomStr(self.stat())+'\t:'+self.User.display_name
        retsubstr = ''
        if self.rw1!='':
            retsubstr += self.rw1

        trw2 = ''
        if self.rw2!='':
            trw2=self.rw2
        elif self.repair>1:
            trw2=self.rw1
        if trw2!='':
            if(len(retsubstr)>0):
                retsubstr += ','
            retsubstr += trw2

        trw3 = ''
        if self.rw3!='':
            trw3=self.rw3
        elif self.repair>2:
            trw3=trw2

        if trw3!='':
            if(len(retsubstr)>0):
                retsubstr += ','
            retsubstr += trw3

        if retsubstr !='':
            retstr += '\t待('+retsubstr+')'

        retstr += '\n'

        return retstr

        
#実行する環境の環境変数に'DISCORD_BOT_TOKEN'を登録しておけば、
#ローカルPC実行、Heloku実行どちらでも対応可能です。
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

# 接続に必要なdiscord.Clientオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('gogocats logged in')

#============================================================
# ループ処理のコア実装
# 60秒に一回ループ
#============================================================
@tasks.loop(seconds=60)
async def loop():
    now_time = datetime.datetime.now().strftime('%H:%M')
    # デバック用コメント
    #text = str(wait_time_end) + ":" + str(wait_flg_end) 
    print(now_time)


#============================================================
#ループ処理実行
#メモ：bot接続前にループ開始する
#============================================================
loop.start()

#サーバーID毎のメンバー状態ハッシュリスト管理用
server_infos = {}

#============================================================
# メッセージ受信時に動作する処理
#============================================================
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    # メモ：こうしておかないと、Botへ応答送信したメッセージを再度受信することになる
    if message.author.bot:
        return

    # 受信メッセージを解析して配列にしておく
    # 区切り文字はコマンドの区切り文字
    # ex."/test 1 2 3"　なら"['/test','1','2','3']の配列が取得できる
    params = message.content.split(" ")
    paramslen = len(params)
    command = params[0]
    #
    print('■受信メッセージ', message.content)
    print('  SPで区切った要素', params, '要素数', paramslen)
    print('  送信者', message.author.name, message.author.id)
    print('  discordサーバー名/ID', message.guild.name, message.guild.id)
    print('  チャンネル名/ID', message.channel.name, message.channel.id)

    # 1番目の要素(=コマンド名)によって分岐する
    result = re.match(r'(/)([0-9]{3})', command)
    if result:
        #============================================================
        #状態登録
        #params[0] /abc
        # a...残機数
        # b...回復数
        # c...入院数
        #params[1] 退院時間1(省略可)
        #params[2] 退院時間2(省略可)
        #params[3] 退院時間3(省略可)
        #============================================================
        #パラメータチェック
        if(paramslen<1):
            await message.channel.send('パラメータが足りません。\n(/helpで使い方を表示)')
            return
        statstr = result.group(2)
        wait = int(statstr[0])
        if(wait > 3):
            wait = 3
        recover = int(statstr[1])
        repair = int(statstr[2])
        if(repair > 3):
            repair = 3
        if(wait + repair > 3):
            repair = 3 - wait

        rw1 = ''
        rw2 = ''
        rw3 = ''
        if(paramslen > 1 and repair > 0):
            rw1 = params[1]
        if(paramslen > 2 and repair > 1):
            rw2 = params[2]
        if(paramslen > 3 and repair > 2):
            rw3 = params[3]



        #サーバーID文字列の取得(メンバー状態ハッシュリストを取り出すためのキーとして使用)
        guild_key = str(message.guild.id)
        #送信者ID文字列の取得(メンバー状態ハッシュリストのキーとして使用)
        author_key = str(message.author.id)

        #サーバーIDに対応するメンバー状態ハッシュリストが生成されていない場合は生成する
        if not guild_key in server_infos:
            server_infos[guild_key] = {}

        #サーバーIDに対応するメンバー状態ハッシュリストの取得
        stat_infos = server_infos[guild_key]

        #送信者メンバーが状態ハッシュリストに存在しない場合は
        if not author_key in stat_infos:
            #送信者メンバー状態をハッシュリストに追加
            stat_infos[author_key] = Statinfo(message.author, wait, recover, repair, rw1, rw2, rw3)
        #送信者メンバー状態の更新
        stat_infos[author_key].wait = wait
        stat_infos[author_key].recover = recover
        stat_infos[author_key].repair = repair
        stat_infos[author_key].rw1 = rw1
        stat_infos[author_key].rw2 = rw2
        stat_infos[author_key].rw3 = rw3

        #登録完了
        retstr = stat_infos[author_key].showstat()+'\n'
        await message.channel.send(retstr)
        return
    elif command == '/init':
        #============================================================
        #状態初期化
        #============================================================
        #サーバーID文字列の取得(メンバー状態ハッシュリストを取り出すためのキーとして使用)
        guild_key = str(message.guild.id)
        #サーバーIDに対応するメンバー状態ハッシュリストを初期化
        server_infos[guild_key] = {}
        #stat_infos = server_infos[guild_key]
        #for User in message.channel.Users:
            #stat_infos[author_key] = Statinfo(User, 3, 2, 0)

        await message.channel.send('**待機状況を初期化しました**')
        return

    elif command == '/stat':
        #============================================================
        #状態一覧表示
        #============================================================
        guild_key = str(message.guild.id)
        stat_infos = server_infos[guild_key]

        c_player = 0
        c_wait = 0
        c_repair = 0
        c_all = 0
        for stat_info in stat_infos.values():
            c_player +=1
            c_wait += stat_info.wait
            c_repair += stat_info.repair
        c_all = c_player * 3
        c_go = c_all - c_wait - c_repair

        retstr = '**待機状況**(登録メンバー数:'+str(c_player)+')\n'

        retstr += '待機数/機体数:'+ str(c_wait)+ '/' + str(c_all)
        if(c_player>0):
            retstr +='('+str(c_wait*100//c_all)+'%)'
        retstr+='\n'
        retstr += '出撃数/機体数:'+ str(c_go)+ '/' + str(c_all)
        if(c_player>0):
            retstr +='('+str(c_go*100//c_all)+'%)'
        retstr+='\n'
        for stat_info in stat_infos.values():
            retstr += stat_info.showstat()+'\n'

        await message.channel.send(retstr)
        return

    elif command == '/chlist':
        #============================================================
        #chlist
        #============================================================
        # コマンド'/test'の実装
        #テストコード：接続先サーバーの全テキストチャンネルの抽出
        text_channel_list = []
        for channel in message.guild.text_channels:
            text_channel_list.append(channel)
        #これだと全サーバー分の抽出
        #for guild in client.guilds:
        #    for channel in guild.text_channels:
        #        text_channel_list.append(channel)
        retstr = '**テキストチャンネル一覧**\n'
        for text_channel in text_channel_list:
            retstr += '・['+str(text_channel.id)+']'+text_channel.name+'\n'
        await message.channel.send(retstr)
        print(retstr)

        return
    elif command == '/gogohelp':
        await message.channel.send(helpstr())
        return

#============================================================
#clientの接続
#これで実行開始します
#成功すると、discord側のbotメンバーがアクティブになります
#============================================================
client.run(token)

