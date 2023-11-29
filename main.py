
#developer = @sudohunter
from pyrogram import Client, filters, enums, errors
from pyrogram.enums import UserStatus,ChatMemberStatus
from pyrogram.errors import FloodWait
from pyromod import listen
import os, sys, time, re, requests, asyncio, json, random
from db import(
    data,
    accounts
)

admins = [] 
token = '' 
app = Client("sudohunter",api_id,api_hash,bot_token=token)
app.set_parse_mode(enums.ParseMode.MARKDOWN)

apis = [
    ['api_id','api_hash']
] 

def Random_API():
    return random.choice(apis)


async def check(event):
    group = data.get_or_none(data.group_id == event.chat.id)
    if group is None:
        await event.reply('❌ ربات در این گروه نصب نیست.')
        return app.leave_chat(event.chat.id)
    if int(group.charge) > int(time.time()):
        return True
    else:
        await app.send_message(chat_id=event.chat.id, text='⌛️ اشتراک این گروه به پایان رسیده است!\nجهت تمدید اشتراک به پشتیبانی پیام دهید.\nخرید هاست پرسرعت مخصوص پایتون و ربات تلگرام : \n@CheetahCloud\nCheetahCloud.site')
        await app.leave_chat(event.chat.id)

async def join_group(event,group_link, session):
    api_id , api_hash = Random_API()
    tempapp = Client(random.randint(11111,999999), api_id=api_id,api_hash=str(api_hash),session_string = session)
    try:
        await tempapp.stop()
    except:
        pass
    await tempapp.connect()
    try:
        chat = await tempapp.join_chat(group_link)
        await tempapp.disconnect()
        return chat.id
    except errors.exceptions.bad_request_400.UserAlreadyParticipant:
        chat = await tempapp.get_chat(group_link)
        await tempapp.disconnect()
        return chat.id
    except FloodWait as e:
        await event.reply(f'♻️ اکانت {e.value} ثانیه محدود شده است!')
        await tempapp.disconnect()
        return False
    except (errors.ChannelPrivate,errors.exceptions.bad_request_400.ChannelPrivate,errors.ChannelPrivate,errors.exceptions.bad_request_400.ChatInvalid,errors.ChannelPrivate,errors.exceptions.bad_request_400.UserBannedInChannel):
        await event.reply('اکانت در این بن شده است!')
        await tempapp.disconnect()
        return False 
    except (errors.ChannelPrivate,errors.exceptions.bad_request_400.InviteHashExpired):
        await event.reply('لینک گروه منقضی شده است!')
        await tempapp.disconnect()
        return False
    except errors.exceptions.bad_request_400.PeerIdInvalid:
        chat = await tempapp.get_chat(group_link)
        await tempapp.disconnect()
        return chat.id
    except Exception as e:
        await event.reply(str(e))
        await tempapp.disconnect()
        return False

def chunk(list: list, number: int) -> list:
    return [list[i:i+number] for i in range(0, len(list), number)]

proc = {}

@app.on_message(filters.command('start') & filters.private)
async def start(_,event):
    await event.reply('سلام!\nجهت فعال سازی ربات برای گروه خود به آیدی زیر مراجعه کنید : \n@AsleKare\n\nخرید هاست پرسرعت مخصوص پایتون و ربات تلگرام : \n@CheetahCloud\nCheetahCloud.site')

@app.on_message(filters.command(['ping','bot']))
async def start(_,event):
    await event.reply(':D')

@app.on_message(filters.command('install') & filters.group & filters.user(admins))
async def install(_,event):
    group = data.get_or_none(data.group_id == event.chat.id)
    if group is None:
        data.create(
            group_id = event.chat.id,
            charge = int(time.time()) + 86400
        )
        await event.reply(f'✅ ربات با موفقیت در گروه {event.chat.title} نصب شد !\n⏰ این گروه به صورت خودکار به مدت یک روز شارژ شد.')
    else :
        await event.reply('❌ ربات در این گروه نصب بوده است!')

@app.on_message(filters.regex(r'/charge (\d+)') & filters.group & filters.user(admins))
async def charge(_, event):
    info = re.findall(r'/charge (\d+)', event.text)
    group = data.get_or_none(data.group_id == event.chat.id)
    if group is None:
        return await event.reply('❌ ربات در این گروه نصب نیست.')
    group.charge = int(time.time()) + (86400 * int(info[0]))
    group.save()
    await event.reply(f'✅ این گروه به مدت {info[0]} روز شارژ شد!')

@app.on_message(filters.command('setcreator') & filters.group & filters.user(admins))
async def setcreator(_,event):
    app.set_parse_mode(enums.ParseMode.HTML)
    group = data.get_or_none(data.group_id == event.chat.id)
    if group is None:
        return await event.reply('❌ ربات در این گروه نصب نیست.')
    if event.reply_to_message is None : 
        return await event.reply('بر روی یک پیام ریپلی کنید!')
    group.creator = event.reply_to_message.from_user.id
    group.save()
    mention = f'<a href="tg://user?id={event.reply_to_message.from_user.id}">{event.reply_to_message.from_user.first_name}</a>'
    await event.reply(f'✅ کاربر {mention} به عنوان مالک این گروه ثبت شد!')

@app.on_message(filters.regex(r'^/add (\+\d+)$') & filters.group)
async def addAccount(_,event):
    if await check(event):
        group = data.get(data.group_id == event.chat.id)
        admins = json.loads(group.admins)
        user = event.from_user.id
        if user in admins or user == group.creator:
            wait = await event.reply('در حال پردازش ..')
            info = re.findall(r'^/add (\+\d+)$', event.text)
            phonenumber = info[0]
            api_id, api_hash = Random_API()
            tempapp = Client(f'sessions/{phonenumber}', api_id=api_id,api_hash=str(api_hash))
            try:
                await tempapp.stop()
            except:
                pass
            await tempapp.connect()
            await wait.delete()

            try:
                sentcode = await tempapp.send_code(phonenumber)
                ask = await app.ask(event.chat.id, f'🔢 کد 5 رقمی ارسال شده به شماره {phonenumber} را ارسال کنید\n🗝 در صورتی که اکانت شما رمز دو مرحله ای دارد آن را همراه با کد ارسال کنید\n⏳ بعد از دریافت این پیام 120 ثانیه زمان جهت تکمیل فرایند افزودن اکانت دارید.\n\nنمونه ارسال کد : \n65413 mohammadAmin', filters.user(event.from_user.id) & filters.regex(r'^(\d{5})(?:\s(.+))?$'), timeout=120)
            except asyncio.exceptions.TimeoutError:
                await ask.edit('مهلت زمان ارسال کد به پایان رسید !')
                return False
            except FloodWait as e:
                await event.reply(f'⚠️ این شماره به مدت {e.value} ثانیه محدود شده است و امکان ارسال کد نیست.')
                os.remove(f'sessions/{phonenumber}.session')
                await tempapp.disconnect()
                return False
            except errors.exceptions.bad_request_400.PhoneNumberBanned:
                await event.reply(f'🚫 این شماره بن شده است!')
                os.remove(f'sessions/{phonenumber}.session')
                await tempapp.disconnect()
                return False
            except errors.exceptions.not_acceptable_406.PhonePasswordFlood:
                await event.reply(f'♻️ این شماره محدود شده است')
                os.remove(f'v{phonenumber}.session')
                await tempapp.disconnect()
                return False
            except errors.exceptions.bad_request_400.PhoneNumberInvalid:
                await event.reply(f'❌ شماره ارسالی نامعتبر است')
                os.remove(f'sessions/{phonenumber}.session')
                await tempapp.disconnect()
                return False
            except asyncio.exceptions.TimeoutError:
                await ask.delete()
                await event.reply('فرصت ارسال کد به پایان رسید!')
            
            sent = await event.reply('در حال پردازش ..')
            info = re.findall(r'^(\d{5})(?:\s(.+))?$', ask.text)[0]
            try:
                await tempapp.sign_in(phonenumber, sentcode.phone_code_hash, info[0])
                if group.account is None:
                    group.account = phonenumber
                    group.save()
                me = await tempapp.get_me()
                session_string = await tempapp.export_session_string()
                accounts.create(
                    group_id = event.chat.id,
                    number = phonenumber,
                    session_string = session_string,
                    owner = event.from_user.id,
                    uid = me.id,
                    name = me.first_name
                )
                await sent.edit(f'✅ اکانت {me.first_name} به لیست اکانت های شما اضافه شد.')
                await tempapp.disconnect()
                os.remove(f'sessions/{phonenumber}.session')
            except errors.exceptions.bad_request_400.PhoneCodeExpired:
                await sent.edit('❌ کد منقضی شده است')
                await tempapp.disconnect()
                os.remove(f'sessions/{phonenumber}.session')
            except errors.exceptions.bad_request_400.PhoneCodeInvalid:
                await sent.edit('❌ کد نامعتبر است')
                await tempapp.disconnect()
                os.remove(f'sessions/{phonenumber}.session')
            except:
                try:
                    await tempapp.check_password(info[1])
                    if group.account is None:
                        group.account = phonenumber
                        group.save()
                    me = await tempapp.get_me()
                    session_string = await tempapp.export_session_string()
                    accounts.create(
                        group_id = event.chat.id,
                        number = phonenumber,
                        session_string = session_string,
                        owner = event.from_user.id,
                        uid = me.id,
                        name = me.first_name
                    )
                    await sent.edit(f'✅ اکانت {me.first_name} به لیست اکانت های شما اضافه شد.')
                    await tempapp.disconnect()
                    os.remove(f'sessions/{phonenumber}.session')
                except:
                    await sent.edit('❌ رمز دو مرحله ای ارسال شده اشتباه است')

@app.on_message(filters.regex(r'/get (list|admins|status|members|history|status-history) (.*)') & filters.group)
async def get(_,event):
    if await check(event):
        group = data.get(data.group_id == event.chat.id)
        admins = json.loads(group.admins)
        user = event.from_user.id
        if user in admins or user == group.creator:
            if group.account is None:
                return await event.reply('هیچ اکانتی بر روی ربات جهت جمع اوری لیست ثبت نشده است!')
            wait = await event.reply('در حال پردازش ..')
            info = re.findall(r'^/get (list|admins|status|members|history|status-history) (.*)$', event.text)
            Type = info[0][0]
            link = info[0][1]
            account = accounts.get(accounts.number == group.account)
            gr = await join_group(event,link,account.session_string)
            allusers = []
            if gr:
                api_id , api_hash = Random_API()
                try:
                    tempapp = Client(random.randint(11111,999999), api_id=api_id,api_hash=str(api_hash),session_string = account.session_string)
                except ValueError:
                    return await event.reply('خطایی پیش آمد دوباره امتحان کنید!')
                try:
                    await tempapp.stop()
                except:
                    pass
                try :
                    await tempapp.connect()
                    chatinfo = await tempapp.get_chat(gr)
                    users = []
                    ids = []
                    if Type not in ('status-history','history'):
                        async for i in tempapp.get_chat_members(chat_id=chatinfo.id):
                            if Type == 'list':
                                file = f'List {chatinfo.id}.txt'
                                if i.user.username and i.user.is_bot == False and i.user.status in [UserStatus.ONLINE,UserStatus.RECENTLY]:
                                    users.append(f'@{i.user.username}')
                            elif Type == 'admins':
                                file = f'Admins {chatinfo.id}.txt'
                                if i.user.username and i.user.is_bot == False and i.user.status in [UserStatus.ONLINE,UserStatus.RECENTLY] and i.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                                    users.append(f'@{i.user.username}')
                            elif Type == 'members':
                                file = f'Members {chatinfo.id}.txt'
                                if i.user.username and i.user.is_bot == False and i.user.status in [UserStatus.ONLINE,UserStatus.RECENTLY] and not i.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                                    users.append(f'@{i.user.username}')
                            elif Type == 'status' :
                                file = f'Status {chatinfo.id}.txt'
                                if i.user.username and i.user.is_bot == False and i.user.status in [UserStatus.ONLINE,UserStatus.RECENTLY] and not i.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                                    users.append(f'@{i.user.username}|{i.user.id}')
                        for x in users:
                            if not x in allusers:
                                if Type == 'status':
                                    userx = x.split('|')
                                    if userx[0] not in ids:
                                        try:
                                            res = requests.get(f'https://Tgwerewolf.com/stats/playerstats/?pid={userx[1]}&json=true')
                                            jso = res.json()
                                            if len(jso) > 5:
                                                allusers.append(f'{userx[0]}|{jso["gamesPlayed"]}')
                                                ids.append(f'{userx[0]}')
                                        except :
                                            pass
                                else :
                                    allusers.append(x)
                    else :
                        file = f'History {chatinfo.id}.txt'
                        async for i in tempapp.get_chat_members(chat_id=chatinfo.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                            if i.user.username and i.user.is_bot == False:
                                users.append(i.user.username)
                            
                        async for message in tempapp.get_chat_history(chatinfo.id,limit = 300000):
                            if message.from_user is None :
                                continue
                            else :
                                if message.from_user.status in [UserStatus.LAST_WEEK, UserStatus.LAST_MONTH, UserStatus.LONG_AGO]:
                                    continue
                                elif message.from_user.is_bot:
                                    continue
                                else:
                                    if message.from_user.username:
                                        if message.from_user.username not in users:
                                            try:
                                                if Type == 'status-history':
                                                    res = requests.get(f'https://Tgwerewolf.com/stats/playerstats/?pid={message.from_user.id}&json=true')
                                                    jso = res.json()
                                                    if len(jso) > 5:
                                                        allusers.append(f'@{message.from_user.username}|{jso["gamesPlayed"]}')
                                                        users.append(message.from_user.username)
                                                else :
                                                    allusers.append(f'@{message.from_user.username}')
                                                    users.append(message.from_user.username)
                                            except :
                                                pass
                                    else:
                                        continue
                except:
                    await wait.edit('مشکلی در گرفتن لیست بوجود آمد!')
                await tempapp.disconnect()
                if len(allusers) > 0:
                    members_file = open(str(file), 'w+')
                    members_file.write('\n'.join(allusers))
                    members_file.close()
                    await event.reply_document(file,caption = f'⚙️ ایدی عددی گروه : `{chatinfo.id}`\n🆔 لینک گروه : {link}\n🔢 تعداد ایدی های جمع اوری شده : `{len(allusers)}`')
                    await wait.delete()
                    os.remove(file)
                else:
                    await wait.edit('مشکلی در گرفتن لیست گروه مورد نظر وجود دارد !')

@app.on_message(filters.regex(r'^/select (\+\d+)$') & filters.group)
async def select(_,event):
    if await check(event):
        info = re.findall(r'^/select (\+\d+)$', event.text)
        group = data.get(data.group_id == event.chat.id)
        admins = json.loads(group.admins)
        user = event.from_user.id
        if user in admins or user == group.creator:
            acc = accounts.get_or_none(accounts.number == info[0],accounts.group_id == event.chat.id)
            if acc is None:
                return await event.reply('❌ اکانتی با این شماره برای این گروه ثبت نشده است!')
            group.account = info[0]
            group.save()
            await event.reply(f'✅ اکانت {info[0]} ({acc.name}) برای دریافت لیست ها تنظیم شد.')

@app.on_message(filters.command('accounts') & filters.group)
async def account(_,event):
    if await check(event):
        group = data.get(data.group_id == event.chat.id)
        admins = json.loads(group.admins)
        user = event.from_user.id
        if user in admins or user == group.creator:
            info = accounts.select().where(accounts.group_id == event.chat.id)
            if info.exists():
                txt = '📲 لیست اکانت های ثبت شده این گروه :\n\n'
                for i in info:
                    txt += f'`{i.number}` ({i.name})\n'
                await event.reply(f'{txt}\nخرید هاست پرسرعت مخصوص پایتون و ربات تلگرام : \n@CheetahCloud\nCheetahCloud.site')
            else :
                await event.reply('هیچ اکانتی ثبت نشده است!') 


@app.on_message(filters.command('addadmin') & filters.group)
async def addadmin(_,event):
    app.set_parse_mode(enums.ParseMode.HTML)
    if await check(event):
        group = data.get_or_none(data.group_id == event.chat.id)
        if event.from_user.id == group.creator:
            if event.reply_to_message is None : 
                return await event.reply('بر روی یک پیام ریپلی کنید!')
            get = json.loads(group.admins)
            if event.reply_to_message.from_user.id in get:
                return await event.reply('این کاربر در ربات ادمین است!')
            get.append(int(event.reply_to_message.from_user.id))
            group.admins = json.dumps(get)
            group.save()
            mention = f'<a href="tg://user?id={event.reply_to_message.from_user.id}">{event.reply_to_message.from_user.first_name}</a>'
            await event.reply(f'✅ کاربر {mention} به عنوان ادمین ربات در این گروه ثبت شد!')

@app.on_message(filters.command('deladmin') & filters.group)
async def deladmin(_,event):
    app.set_parse_mode(enums.ParseMode.HTML)
    if await check(event):
        group = data.get_or_none(data.group_id == event.chat.id)
        if event.from_user.id == group.creator:
            if event.reply_to_message is None : 
                return await event.reply('بر روی یک پیام ریپلی کنید!')
            get = json.loads(group.admins)
            if not event.reply_to_message.from_user.id in get:
                return await event.reply('این کاربر در ربات ادمین نیست!')
            get.remove(int(event.reply_to_message.from_user.id))
            group.admins = json.dumps(get)
            group.save()
            mention = f'<a href="tg://user?id={event.reply_to_message.from_user.id}">{event.reply_to_message.from_user.first_name}</a>'
            await event.reply(f'✅ کاربر {mention} از ادمینی ربات در این گروه حذف شد!')

@app.on_message(filters.regex(r'^/setgroup (.*)$') & filters.group)
async def select(_,event):
    if await check(event):
        info = re.findall(r'^/setgroup (.*)$', event.text)
        group = data.get(data.group_id == event.chat.id)
        admins = json.loads(group.admins)
        admins = list(map(lambda e:int(e),admins))
        user = event.from_user.id
        if user in admins or user == group.creator:
            account = accounts.get(accounts.number == group.account)
            try:
                gr = await join_group(event,info[0],account.session_string)
                group.main_link = info[0]
                group.save()
                await event.reply('لینک گروه با موفقیت ثبت شد!')
            except :
                return await event.reply(f'خطایی پیش آمد!')


@app.on_message(filters.regex(r'^/del (.*)$') & filters.group)
async def delaccount(_,event):
    if await check(event):
        group = data.get(data.group_id == event.chat.id)
        admins = json.loads(group.admins)
        admins = list(map(lambda e:int(e),admins))
        user = event.from_user.id
        if user in admins or user == group.creator:
            info = re.findall(r'^/del (.*)$', event.text)
            account = accounts.get_or_none(accounts.number == info[0])
            if account is not None:
                account.delete_instance()
                await event.reply('اکانت مورد نظر از لیست اکانت ها حذف شد!')
                api_id , api_hash = Random_API()
                tempapp = Client(random.randint(11111,999999), api_id=api_id,api_hash=str(api_hash),session_string = account.session_string)
                try:
                    await tempapp.stop()
                except:
                    pass
                await tempapp.connect()
                await tempapp.log_out()
                await tempapp.stop()
                await tempapp.disconnect()
            else :
                await event.reply('اکانتی با این شماره مربوط به گروه شما یافت نشد!')

            

@app.on_message(filters.regex('/check (.*)') & filters.group & filters.reply)
async def split_check(client,event):
    if await check(event):
        dd = await event.reply('درحال پردازش ...')
        group = data.get(data.group_id == event.chat.id)
        admins = json.loads(group.admins)
        admins = list(map(lambda e:int(e),admins))
        user = event.from_user.id
        if user in admins or user == group.creator:
            if group.main_link is None:
                return await event.reply('ابتدا گروه اصلی را با دستور /setgroup تنظیم کنید!')
            try :
                account = accounts.get(accounts.number == group.account)
                gr = await join_group(event,group.main_link,account.session_string)
                api_id , api_hash = Random_API()
                tempapp = Client(random.randint(11111,999999), api_id=api_id,api_hash=str(api_hash),session_string = account.session_string)
                try:
                    await tempapp.stop()
                except:
                    pass
                await tempapp.connect()
                count = event.text.split(' ')[1]
                ids = []
                joins = []
            
                try:
                    async for member in tempapp.get_chat_members(chat_id=gr):
                        if member.user.username:
                            ids.append(str(member.user.username).lower())
                    await dd.edit('اعضای گروه اصلی گرفته شد!')
                except :
                    return await event.reply('خظایی در دریافت لیست اعضای گروه اصلی به وجود آمد!')
                fiile = await app.download_media(event.reply_to_message.document.file_id,file_name = event.reply_to_message.document.file_name)
                f = open(f"downloads/{event.reply_to_message.document.file_name}", "r")
                os.unlink(fiile)
                line = f.readlines()
                
                x = chunk(line,int(count))
                txt = ''
                for i in x:
                    for m in i:
                        if '|' not in m:
                            id = str(m.replace('@','')).lower().strip()
                            if id not in ids :
                                txt += f'@{id}\n'
                            else :
                                joins.append(f'@{id}')
                        else:
                            t = m.split('|')[0]
                            id = str(t.replace('@','')).lower()
                            plays  = m.split('|')[1]
                            if id not in ids :
                                txt += f'@{id} | {plays}'
                            else :
                                joins.append(f'@{id}')

                    await event.reply(txt)
                    txt = ''
                    await asyncio.sleep(1)
                await event.reply('عملیات ارسال آیدی ها به پایان رسید\nخرید هاست پرسرعت مخصوص پایتون و ربات تلگرام : \n@CheetahCloud\nCheetahCloud.site')
                if len(joins) > 1:
                    rand = random.randint(111111,9999999)
                    with open(f'join-{rand}.txt', 'w') as f:
                        for member in joins:
                            f.write(f'{member}\n')
                    f.close()
                    await event.reply_document(document=f'join-{rand}.txt', caption=f'لیست کاربرانی که در لیست های بالا به دلیل عضویت در گروه قرار نگرفتند')
                    os.remove(f'join-{rand}.txt')
            except Exception as e:
                await dd.edit('خطایی پیش آمد ؛ دوباره امتحان کنید.')
                
@app.on_message(filters.regex('/split (.*)') & filters.group & filters.reply)
async def split(client,event):
    if await check(event):
        group = data.get(data.group_id == event.chat.id)
        admins = json.loads(group.admins)
        admins = list(map(lambda e:int(e),admins))
        user = event.from_user.id
        if user in admins or user == group.creator:
            count = event.text.split(' ')[1]
            try :
                fiile = await app.download_media(event.reply_to_message.document.file_id,file_name = event.reply_to_message.document.file_name)
                f = open(f"downloads/{event.reply_to_message.document.file_name}", "r")
                line = f.readlines()
                os.unlink(fiile)

                x = chunk(line,int(count))
                txt = ''
                for i in x:
                    for m in i:
                        if '|' in m:
                            t = m.split('|')[0]
                            plays  = m.split('|')[1]
                            txt += f'{t}|{plays}'
                        else:
                            id = m.replace('@','')
                            txt += f'@{id}'
                    await event.reply(txt)
                    txt = ''
                    await asyncio.sleep(1)
                await event.reply('عملیات ارسال آیدی ها به پایان رسید\nخرید هاست پرسرعت مخصوص پایتون و ربات تلگرام : \n@CheetahCloud\nCheetahCloud.site')
            except Exception as e:
                pass

@app.on_message(filters.command(['help']))
async def help(_,event):
    await event.reply('''
• راهنمای دستورات ربات به شرح زیر است :

▪︎ /add <number>

- با استفاده از این دستور شما میتوانید یک اکانت جدید به ربات جهت دریافت لیست گروه ها اضافه کنید 
□ /del <number>

- با استفاده از این دستور شما میتوانید اکانت مورد نظر را از لیست اکانت های ربات حذف کنید

▪︎ /addadmin & reply only

- با استفاده از این دستور شما میتوانید یک ادمین جدید جهت کار با ربات و دریافت لیست به ربات اضافه کنید

□ /deladmin & reply only

- با استفاده از این دستور شما میتوانید کاربر مورد نظر را از ادمینی ربات حذف کنید

▪︎ /setgroup <link>

- با استفاده از این دستور شما میتوانید لینک گروه اصلی را برای جدا سازی کاربران حاضر در گروه شما در بین لیست ها را تنظیم کنید

□ /check <usernames-per-list>

- با استفاده از این دستور شما میتوانید کاربرانی که در گروه اصلی شما حضور دارند در بین لیست ها را جدا کنید

▪︎ /split <usernames-per-list>

- با استفاده از این دستور شما میتوانید ایدی های یک فایل را ( لیست ) به تعداد دلخواه استخراج کنید

□ /accounts 

- با استفاده از این دستور شما میتوانید لیست اکانت های ثبت شده در ربات را دریافت کنید                     

آموزش لیست گیری :
/get <type> <link>

- types :

× admins : دریافت ادمین های گروه 
× members : دریافت ممبر های گروه
× list : دریافت تمامی اعضای گروه
× history : استخراج ایدی ها ار روی چت
× status : دریافت اعضای استیت دار (مخصوص گروه های ولفی)
× status-history : استخراج کارابران استیت دار (ولفی) از روی چت
                      
- link : لینک گروه مورد نظر

🆔 @DarkBotsChannel
                      
خرید هاست پرسرعت مخصوص پایتون و ربات تلگرام : \n@CheetahCloud\nCheetahCloud.site''')

@app.on_message(filters.command('reload') & filters.user(admins))
async def Reload(_,event):
    await event.reply('Reloaded Successfully')
    python = sys.executable
    os.execl(python, python, *sys.argv)

app.run()

#developer = @sudohunter