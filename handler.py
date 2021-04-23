import discord
import docs
from discord.utils import get
from identification import Settings

class Handler:
    """Обработчик сообщений"""
    def __init__(self, client):
        self.client = client
        self.tournament = Tournament(client)
        self.balance = Balance(client)
        self.roles = Roles(client)
        self.dummy = Dummy(client)
        self.channel = Channel(client)

        self.handlers = {
                "!турнир":  self.tournament.checkArgs,
                "!баланс":  self.balance.checkArgs,
                "!роли":    self.roles.checkArgs,
                "!канал":   self.channel.checkArgs,
                "!echo":    self.dummy.echo,
                "!привет":  self.dummy.hello
        }

    async def checkEvent(self, message):
        is_admin = False
        for role in message.author.roles:
            if (Settings.admin_role_name) in str(role):
                is_admin = True
        if is_admin:
            command = (message.content.split()[0]).lower()
            if command in self.handlers.keys():
                await self.handlers[command](message)
            elif command == "!help" or command == "!Help":
                commands = ''.join([(str(i) + "\n") for i in self.handlers])
                await message.channel.send("Доступные команды:\n" + commands)
        else:
            await message.channel.send("У вас недостаточно прав")
        

class Balance:
    """Обработчик аргументов для !Баланс"""
    def __init__(self, client):
        self.client = client
        self.commands = {
            "получить":self.b_get,
            "пополнить":self.b_set,
            "убавить":self.b_set
        }

    async def checkArgs(self, message):
        args = message.content.split()
        if len(args) < 2:
            await self.error(message, 'Список аргументов для команды !Баланс')
        else:
            if args[1] in self.commands.keys():
                await self.commands[args[1]](message)
            else:
                await self.error(message, f"Аргумент {args[1]} не найден.")

    async def error(self, message, err):
        await message.channel.send(err)

    async def b_get(self, message):
        await message.channel.send("Ваш баланс:")

    async def b_set(self, message):
        await message.channel.send("Новый баланс:")



class Roles:
    """Обработчик аргументов для !Роли"""
    def __init__(self, client):
        self.client = client
        self.possible_args  = {
            "создать":self.create_roles,
            "выдать":self.give_roles,
            "синтаксис":self.print_info,
        }
        # делаем строку из ключей возможных аргументов
        self.role_command_args =  (''.join([(a + ', ') for a in self.possible_args.keys()]))[0:-2]
        
    async def checkArgs(self, message):
        input_args = message.content.split()[1:]
        if len(input_args) < 1:
            await self.error(message, 'Доступные аргументы: ' + self.role_command_args)
        else:
            if input_args[0] in self.possible_args.keys():
                await self.possible_args[input_args[0]](message, input_args)
            else:
                await self.error(message, f"Аргумент {input_args[0]} не найден.")

                
    async def error(self, message, err):
        await message.channel.send(err)

    async def _give_role(self, message, role, nicknames):
        for nick in [int(nick) for nick in nicknames]:
            user = self.client.get_user(nick)
            user = message.guild.get_member(user.id)
            for r in user.roles:
                # Проверяем, если роль уже добавлена
                if r.id == role.id:
                    print(r.id, "already added")
                    return
            await user.add_roles(role)

    async def create_roles(self, message, args):
        role = args[1][1:]
        print(role)
        nicknames = [i[3:-1] for i in args[2:]]
        await message.guild.create_role(name=role)
        role = discord.utils.get(message.guild.roles, name=role)
        print(role)
        await self._give_role(message, role, nicknames)
        await message.channel.send("Роль создана и выдана")

    async def give_roles(self, message, args):
        role = args[1][3:-1]
        print(role)
        nicknames = [i[3:-1] for i in args[2:]]
        #print(message.guild.roles)
        role = discord.utils.get(message.guild.roles, id=int(role))
        #message.guild.get_role(role[2:-1])
        print(role)
        if role != None:
            await self._give_role(message, role, nicknames)
            await message.channel.send("Роль выдана")
        else:
            await message.channel.send("Роль не найдена.")

    async def print_info(self, message, _):
        await message.channel.send(docs.rolesinstr)

class Tournament:
    """Обработчик аргументов для !Турнир"""
    def __init__(self, client):
        self.client = client
        self.commands = {
            "создать":self.tournament_create,
            "удалить":self.tournament_delete,
            "синтаксис":self.print_info,
        }  
    
    async def checkArgs(self, message):
        input_args = message.content.split()[1:]
        if len(input_args) < 1:
            await self.sendMsg(message, docs.tournamentstr)
        else:
            if input_args[0] in self.commands.keys():
                await self.commands[input_args[0]](message, input_args)
            else:
                await self.sendMsg(message, f"Аргумент {input_args[0]} не найден.")

    async def sendMsg(self, message, err):
        await message.channel.send(err)

    async def tournament_create(self, message, name):
        #большая страшная функция, которая создаёт нужные роли, категорию и каналы
        role_name = "".join([(i + " ") for i in name[1:]])
        is_duplicate = False
        member_role = None
        capitan_role = None
        for role in message.guild.roles:
            if (role_name + " участник") in str(role):
                member_role = role
                is_duplicate = True
            if (role_name + " капитан") in str(role):
                is_duplicate = True
                capitan_role = role
        if not is_duplicate: # if the role doesn't exist
            member_role = await message.guild.create_role(name=role_name + " участник")
            capitan_role = await message.guild.create_role(name=role_name + " капитан")
            await message.channel.send("Созданы соответствующие роли.")
        else:
            await message.channel.send("Данная роль уже существует. Будет создана только секция каналов.")
        
        category_overwrites = {
            message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            message.guild.get_role(member_role.id): discord.PermissionOverwrite(read_messages=True),
            message.guild.get_role(capitan_role.id): discord.PermissionOverwrite(read_messages=True)
        }
        capitan_overwrites = {
            message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            message.guild.get_role(member_role.id): discord.PermissionOverwrite(read_messages=False),
            message.guild.get_role(capitan_role.id): discord.PermissionOverwrite(read_messages=True)
        }
        category = await message.guild.create_category(role_name, overwrites=category_overwrites)
        await category.create_text_channel("важное")
        await category.create_text_channel("время-встречи", overwrites = capitan_overwrites)
        await category.create_text_channel("флуд")
        await category.create_voice_channel("Общий голосовой")
        await category.create_voice_channel("Комната #1", user_limit = 5)
        await category.create_voice_channel("Комната #2", user_limit = 5)
        await category.create_voice_channel("Комната #3", user_limit = 5)
        await category.create_voice_channel("Капитанский", overwrites = capitan_overwrites)

        await message.channel.send("Категория с каналами создана.")

    async def tournament_delete(self, message, arg):
        cat_name = "".join([(i + " ") for i in arg[1:]])
        category = None
        for i in message.guild.categories:
            if str(i) in cat_name:
                category = i
                break
        if category != None:
            for channel in category.channels:
                await channel.delete()
            await category.delete()
            await message.channel.send("Категория и каналы удалены.")
        else:
            await message.channel.send("Категория с названием " + cat_name +" не существует.")

        server_roles = message.guild.roles
        for role in server_roles:
            if (cat_name + " участник" ) in str(role):
                await role.delete()
            if (cat_name + " капитан") in str(role):
                await role.delete()
        await message.channel.send("Роли категории удалены (если они вообще были)")
    async def print_info(self, message, _):
        await message.channel.send(docs.tournamentstr)


class Channel:
    """Обработчик аргументов для !Канал"""
    def __init__(self, client):
        self.client = client
        self.commands = {
            #"список":self.list_get,
            "создать":self.list_create,
            "создать_текст":self.text_create,
            "создать_голос":self.voice_create
        }

    async def checkArgs(self, message):
        args = message.content.split()
        if len(args) < 2:
            await self.sendMsg(message, docs.channelinstr)
        else:
            if args[1] in self.commands.keys():
                await self.commands[args[1]](message, args)
            else:
                await self.sendMsg(message, f"Аргумент {args[1]} не найден.")

    async def _createPrivateText(self, message, name):
        overwrites = {
                message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                message.guild.me: discord.PermissionOverwrite(read_messages=True)
            }

        channel = await message.guild.create_text_channel(name, overwrites=overwrites)
        return channel

    async def _createPrivateVoice(self, message, name):
        overwrites = {
                message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                message.guild.me: discord.PermissionOverwrite(read_messages=True)
            }

        channel = await message.guild.create_voice_channel(name, overwrites=overwrites)
        return channel

    async def _createRoleChannel(self, message, channel, role_t, overwrite):
        role = discord.utils.get(message.guild.roles, name=role_t)
        if role == None:
            await self.sendMsg(message, f"Ошибка: роль {role_t} не найдена!")
        else:
            #await self.sendMsg(message, f"РОЛЬ ${role_t} НАЙДЕНА! ]")
            await channel.set_permissions(role, overwrite=overwrite)

    async def sendMsg(self, message, err):
        await message.channel.send(err)

    async def list_get(self, message, _):
        await self.sendMsg(message, f"Мне лень")

    async def list_create(self, message, args):
        guild = message.guild
        # Thanks python for spaghetti, very cool!
        if len(args) == 2:
            await self.sendMsg(message, f"Недостаточно аргументов для создания канала. Напишите !Канал для инструкции.")
        elif len(args) == 3:
            # Общий канал для всех
            await guild.create_text_channel(args[2])
            await guild.create_voice_channel(args[2])
        else:
            # Канал для ролей
            txtchannel = await self._createPrivateText(message, args[2])
            voicechannel = await self._createPrivateVoice(message, args[2])
            overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            for role in args[3:]:
                await self._createRoleChannel(message, txtchannel, role, overwrite)
                await self._createRoleChannel(message, voicechannel, role, overwrite)

    async def text_create(self, message, args):
        guild = message.guild
        # Thanks python for spaghetti, very cool!
        if len(args) == 2:
            await self.sendMsg(message, f"Недостаточно аргументов для создания канала. Напишите !Канал для инструкции.")
        elif len(args) == 3:
            # Общий канал для всех
            await guild.create_text_channel(args[2])
        else:
            # Канал для ролей
            # Канал для ролей
            txtchannel = await self._createPrivateText(message, args[2])
            overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            for role in args[3:]:
                await self._createRoleChannel(message, txtchannel, role, overwrite)

    async def voice_create(self, message, args):
        guild = message.guild
        # Thanks python for spaghetti, very cool!
        if len(args) == 2:
            await self.sendMsg(message, f"Недостаточно аргументов для создания канала. Напишите !Канал для инструкции.")
        elif len(args) == 3:
            # Общий канал для всех
            await guild.create_voice_channel(args[2])
        else:
            # Канал для ролей
            voicechannel = await self._createPrivateText(message, args[2])
            overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            for role in args[3:]:
                await self._createRoleChannel(message, voicechannel, role, overwrite)

class Dummy:
    """Dummy-функции"""
    def __init__(self, client):
        self.client = client

    async def echo(self, message):
        await message.channel.send(message.content)

    async def hello(self, message):
        await message.channel.send(f"Привет, {message.author}!")