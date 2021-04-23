#основная библиотека
import discord

#конфиги бота
from identification import Settings
from handler import Handler
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
hndlr = Handler(client)



#Информация о подключении бота к серверу
@client.event
async def on_ready():
    for guild in client.guilds:
        is_exist = False
        for role in guild.roles:
            if (Settings.admin_role_name) in str(role):
                is_exist = True
        if not is_exist:
            await guild.create_role(name=Settings.admin_role_name, colour = 0xff0000 )
            print("Role \"MIREA bootcamp admin\" has been created")
        else:
            print("Role \"MIREA bootcamp admin\" exist")

    print('We have logged in as {0.user}'.format(client))

'''
Обработка входящих сообщений
'''
@client.event
async def on_message(message):
    # не реагируем на свои же сообщения
    if message.author == client.user:
        return
    await hndlr.checkEvent(message)
        
    
client.run(Settings.token)