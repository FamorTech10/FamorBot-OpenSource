from discord.ext import tasks,commands
from discord.utils import get
from numpy.random import f
from pymongo import MongoClient
import discord
import random
import rngmsg # el codigo de rngmsg esta hasta el final
import asyncio
import datetime
import math
import numpy as np
import praw
import pafy

roles = []
counter = 0
guilds_ids = []
cluster = MongoClient("el link de tu cluster ") #video 2 creo si no lo tienes
database = cluster["Discord"]# video 2 creo si no lo sabes
reddit = praw.Reddit(client_id = "___",
                    client_secret = "___",
                    username = "___",
                    password = "___",
                    user_agent = "___",
                    check_for_async=False) # no se si le hice video a esto pero debe de haber tutoriales

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
client = commands.Bot(command_prefix = "!",intents=intents)

#bot listo  
@client.event
async def on_ready():
    discord.AllowedMentions.all
    await client.change_presence(activity=discord.Game("!comandos"))
    print('FamorTest listo')
    bot_guilds.start()
#eventos
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        msg = "Comando no valido, escribe !comandos para consultarlo." 
        await output(ctx,msg)
    if isinstance(error, commands.CommandOnCooldown):
        tiempo_restante = str(datetime.timedelta(seconds=int(error.retry_after)))
        msg = f'Aún no puedes utilizar este comando, debes esperar {tiempo_restante}'
        await output(ctx,msg)
    if isinstance(error, commands.BotMissingPermissions):
        msg = 'Famorbot no tiene los permisos necesarios para realizar este comando.'
        await output(ctx,msg)
@client.event
async def on_guild_remove(ctx,guild = guilds_ids):
    guild_id = str(guild)
    newguilds_ids= []
    for x in client.guilds:
        newguilds_ids.append(x.id)
    removed_guild = set(guilds_ids) ^ set(newguilds_ids)

    str_removed_guild = str(removed_guild).replace("{","")
    str_removed_guild = str(str_removed_guild).replace("}","")
    cluster_data = database[str_removed_guild]
    cluster_data.drop()
@client.event
async def on_guild_join(guild):
    guild_id = str(guild.id)
    cluster_data = database[guild_id]
    serverconfig = cluster_data.find_one({"server_id": guild.id})

    if serverconfig == None:
        server_config = {"server_id": guild.id,"embed_color": [255, 127, 0],"join_channel": None,"roles": []}
        cluster_data.insert_one(server_config)
    else:
        return

@client.event
async def on_member_join(member):
    msg = f"Bienvenido al servidor {member.mention}"

#datos
async def user_delay():
    global counter
    if counter <= 0:
        counter += 1
async def abrir_cuenta(ctx,user):  
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    if datos == None:
        nom = user.name.replace(" ","")
        newuser = {
            "id": user.id, 
            "FamorCoins": 250, 
            "FamorMiner": 0,
            "EarningMultiplier": 1,
            "MinerosMultiplier": 0,
            "PrestigePoints": 0, 
            "PPmultiplier": 1, 
            "CardCounting": 0,
            "UpgradeCostDivider": 1,
            "xp": 0,
            "Nombre": nom
            }
        
        cluster_data.insert_one(newuser)
    else:
        return 
async def get_collection(ctx):
    guild_id = str(ctx.guild.id)
    cluster_data = database[guild_id]
    return cluster_data
async def get_embed_color(ctx):
    cluster_data = await get_collection(ctx)
    serverconfig = cluster_data.find_one({"server_id": ctx.guild.id})
    embedcolor = serverconfig["embed_color"]
    return embedcolor
async def get_server_roles(ctx):
    cluster_data = await get_collection(ctx)
    serverconfig = cluster_data.find_one({"server_id": ctx.guild.id})
    roles = serverconfig["roles"]
    return roles
async def output(ctx, msg = None):
    author = ctx.author.name
    embedcolor = await get_embed_color(ctx)

    embed=discord.Embed(title= author, description=msg,color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    await ctx.send(embed=embed)
@tasks.loop(seconds=10)
async def bot_guilds():
    guilds_ids.clear()
    for x in client.guilds:
        guilds_ids.append(x.id)

#comandos
#@client.command()
#async def snake(ctx):
    #Eliminado por que no me interesa arreglarlo
@client.command(name="ppt")
async def ppt(ctx, plr2:discord.Member=None, cantidad=None):
    plr1 = ctx.author
    if plr2 == None:
        msg = ("Escribe un usuario a retar")
        await output(ctx,msg)
        return 
    if plr1 == plr2:
        msg = ("No puedes retarte a ti mismo")
        await output(ctx,msg)
        return
    if cantidad == None:
        msg = ("Introduce una cantidad a apostar")
        await output(ctx,msg)
        return

    await abrir_cuenta(ctx,plr1)
    await abrir_cuenta(ctx,plr2)
    cluster_data = await get_collection(ctx)
    datos_plr1 = cluster_data.find_one({"id": plr1.id})
    datos_plr2 = cluster_data.find_one({"id": plr2.id})
    plr1_FamorCoins = datos_plr1["FamorCoins"]
    plr2_FamorCoins = datos_plr2["FamorCoins"]
    guild = ctx.guild
    famortest = get(guild.roles, name="Famortest")
    pptemoji = ['🪨','🧻','✂️']
    amt = int(cantidad)
    embedcolor = await get_embed_color(ctx)

    if amt > plr1_FamorCoins:
        msg = ("No tienes suficiente dinero")
        await output(ctx,msg)
        return
    if amt > plr2_FamorCoins:
        msg = (f"{plr2} no tiene suficiente dinero")
        await output(ctx,msg)
        return
    #Ahora que se mas el resultado de estos try deberian de ir en una funcion para no realizar tantas cosas cada vez que se ejecute el comando 
    try:
        role1 = get(guild.roles, name="jugador 1")
        role2 = get(guild.roles, name="jugador 2")
        ver = role1.id
    except:
        await guild.create_role(name = "jugador 1")
        await guild.create_role(name = "jugador 2")
        role1 = get(guild.roles, name="jugador 1")
        role2 = get(guild.roles, name="jugador 2")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role1: discord.PermissionOverwrite(read_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        famortest: discord.PermissionOverwrite(read_messages=True)}
    overwrites2 = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        role2: discord.PermissionOverwrite(read_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        famortest: discord.PermissionOverwrite(read_messages=True)}
    try:
        cat = get(guild.categories, name = "ppt")
        channel1= get(cat.text_channels, name = "jugador1")
        channel2 = get(cat.text_channels, name = "jugador2")
    except:
        await guild.create_category(name = "ppt")
        cat = get(guild.categories, name = "ppt")
        channel1 = await guild.create_text_channel(name = "jugador1",category = cat,overwrites = overwrites)
        channel2 = await guild.create_text_channel(name = "jugador2",category = cat,overwrites = overwrites2)

    embed = discord.Embed(description = f'{plr1.mention} esta retando a {plr2.mention} con {cantidad} Famorcoins, {plr2.mention} reacciona con ✅ para aceptar',color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    reto = await ctx.send(embed=embed)
    await reto.add_reaction('✅')
    def check(reaction, user):
        return user == plr2 and str(reaction.emoji) == '✅'
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
    except asyncio.TimeoutError:
        msg = f"{plr2.mention} no respondio..."
        await output(ctx,msg)
    else:
        await plr1.add_roles(role1)
        await plr2.add_roles(role2)
        sel2 = await channel2.send(f"{plr2.mention} selecciona un emoji")
        for emoji in pptemoji:
            await sel2.add_reaction(emoji)
        def check1(reaction, user):
            if user == plr2 and str(reaction.emoji) in pptemoji:
                return user,reaction
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check1)
        except asyncio.TimeoutError:
            msg = (f'{plr2} se retiro...')
            await output(ctx,msg)
            await plr1.remove_roles(role1)
            await plr2.remove_roles(role2)
            await sel2.delete(delay=None)
            return
        await sel2.delete(delay=None)
        sel1 = await channel1.send(f"{plr1.mention} selecciona un emoji")
        for emoji in pptemoji:
            await sel1.add_reaction(emoji)
        def check2(reaction2, user):
            if user == plr1 and str(reaction2.emoji) in pptemoji:
                return plr1,reaction2
        try:
            reaction2, plr1 = await client.wait_for('reaction_add', timeout=15.0, check=check2)
        except asyncio.TimeoutError:
            msg = (f'{plr1} se retiro...')
            await output(ctx,msg)
            await plr1.remove_roles(role1)
            await plr2.remove_roles(role2)
            await sel1.delete(delay=None)
            return
        await sel1.delete(delay=None)
        #tambien tengo demasiados if aqui, en este momento no se me ocurre una solucion para evitarlos, 
        #lo que si se puede hacer es una funcion que regrese el msg1,msg2,reward1,reward2 para no repetirlo tanto
        if str(reaction) == str(reaction2):
            msg1 =(f'<@{plr2.id}> escogio {reaction} mientras que <@{plr1.id}> escogio {reaction2}, eso significa que empataron!')
            msg2 = f"Nadie gano, asi que sus apuestas se regresaron"
        elif str(reaction) == '🪨' and str(reaction2 )== '🧻':
            msg1 = (f'<@{plr2.id}> escogio {reaction} mientras que <@{plr1.id}> escogio {reaction2}, eso significa que <@{plr1.id}> gana!')
            msg2 = f"<@{plr1.id}> ha ganado {amt} FamorCoins"
            reward1 = plr1_FamorCoins + amt
            reward2 = plr2_FamorCoins - amt
        elif str(reaction2) == '🪨' and str(reaction) == '🧻':
            msg1 = (f'<@{plr2.id}> escogio {reaction} mientras que <@{plr1.id}> escogio {reaction2}, eso significa que <@{plr2.id}> gana!')
            msg2 = f"<@{plr2.id}> ha ganado {amt} FamorCoins"
            reward1 = plr1_FamorCoins - amt
            reward2 = plr2_FamorCoins + amt
        elif str(reaction) == '🪨' and str(reaction2) == '✂️':
            msg1 = (f'<@{plr2.id}> escogio {reaction} mientras que <@{plr1.id}> escogio {reaction2}, eso significa que <@{plr2.id}> gana!')
            msg2 = f"<@{plr2.id}> ha ganado {amt} FamorCoins"
            reward1 = plr1_FamorCoins - amt
            reward2 = plr2_FamorCoins + amt
        elif str(reaction2) == '🪨' and str(reaction) == '✂️':
            msg1 = (f'<@{plr2.id}> escogio {reaction} mientras que <@{plr1.id}> escogio {reaction2}, eso significa que <@{plr1.id}> gana!')
            msg2 = f"<@{plr1.id}> ha ganado {amt} FamorCoins"
            reward1 = plr1_FamorCoins + amt
            reward2 = plr2_FamorCoins - amt
        elif str(reaction) == '🧻' and str(reaction2) == '✂️':
            msg1 = (f'<@{plr2.id}> escogio {reaction} mientras que <@{plr1.id}> escogio {reaction2}, eso significa que <@{plr1.id}> gana!')
            msg2 = f"<@{plr1.id}> ha ganado {amt} FamorCoins"
            reward1 = plr1_FamorCoins + amt
            reward2 = plr2_FamorCoins - amt
        elif str(reaction2) == '🧻' and str(reaction) == '✂️':
            msg1 = (f'<@{plr2.id}> escogio {reaction} mientras que <@{plr1.id}> escogio {reaction2}, eso significa que <@{plr2.id}> gana!')
            msg2 = f"<@{plr2.id}> ha ganado {amt} FamorCoins"
            reward1 = plr1_FamorCoins - amt
            reward2 = plr2_FamorCoins + amt

        await output(ctx,msg1)
        await output(ctx,msg2)
        await plr1.remove_roles(role1)
        await plr2.remove_roles(role2)
        cluster_data.update_one({"id": plr1.id}, {"$set":{"FamorCoins": reward1}})
        cluster_data.update_one({"id": plr2.id}, {"$set":{"FamorCoins": reward2}})
@client.command(name = "trabajar")
@commands.cooldown(1,300,commands.BucketType.user)
async def trabajar(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    earningmultiplier = datos["EarningMultiplier"]
    PPmultiplier = datos["PPmultiplier"]
    rwd = random.randint(200, 1000)
    reward = (rwd * earningmultiplier) * PPmultiplier
    #se pueden hacer mas bonitos pero funcionan
    job0 = (f'Ayudaste a un empresario a evadir impuestos y te han recompensado con {reward} FamorCoins')
    job1 = (f'Declaraste impuestos de tu pc gamer y recuperaste {reward} FamorCoins')
    job2 = (f'Fuiste recepcionista de una empresa y te pagaron {reward} FamorCoins')
    job3 = (f'Fuiste maestro de preescolar y te pagaron {reward} FamorCoins')
    job4 = (f'Le hiciste un dibujo NSFW a un furro y te pago {reward} FamorCoins')
    job5 = (f'Hiciste una animacion y la subiste a Youtube, ganaste {reward} FamorCoins gracias a los anuncios')
    job6 = (f'Programaste un bot de Discord y te pagaron {reward} FamorCoins')
    job7 = (f'Hiciste un videojuego y ganaste {reward} FamorCoins de personas mayores')
    job8 = (f'Minaste criptomonedas durante 24 horas y ganaste {reward} FamorCoins')
    job9 = (f'Trabaste como albañil y ganaste {reward} FamorCoins')
    job10 = (f'Contruiste una casa en el centro de la ciudad y ganaste {reward} FamorCoins')
    job11 = (f'salvaste la vida de un enfermo y te pago {reward} FamorCoins')
    job12 = (f'un adolescente te pidio un condón y no hiciste nada incomodo así que te dio {reward} FamorCoins como propina')
    job13 = (f'Limpiaste el baño de una escuela pública y te pagaron  {reward} FamorCoins por las molestias')
    job14 = (f'fuiste un presidente corrupto durante 6 años y ganaste {reward} FamorCoins')
    trabajo = ([job0,job1,job2,job3,job4,job5,job6,job7,job8,job9,job10,job11,job12,job13,job14])
    msg = random.choice(trabajo)
    new_FamorCoins = FamorCoins + reward
    await output(ctx,msg)

    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})
@client.command(name = "trabajoilegal")
async def trabajoilegal(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    earningmultiplier = datos["EarningMultiplier"]
    PPmultiplier = datos["PPmultiplier"]
    CardCounting = datos["CardCounting"]
    if FamorCoins <= 0:
        msg = "Tu dinero no puede ser negativo!"
        await output(ctx,msg)
        return
    rwd = random.randint(200, 1000)
    reward = (rwd * earningmultiplier) * PPmultiplier
    result = random.randint(0,100)
    prob = 50 + CardCounting
    #tampoco me gusta esto por que cada vez que se usa el comando define el monton de variables, esto se debe de mover a un archivo aparte donde ya esten definias
    # y aqui solo le agregue cuanto gano
    if result <= prob:
        job0 = (f'Ayudaste a un empresario a evadir impuestos y te han recompensado con {reward} FamorCoins')
        job1 = (f'Declaraste impuestos de tu pc gamer y recuperaste {reward} FamorCoins')
        job2 = (f'Fuiste recepcionista de una empresa y te pagaron {reward} FamorCoins')
        job3 = (f'Fuiste maestro de preescolar y te pagaron {reward} FamorCoins')
        job4 = (f'Le hiciste un dibujo NSFW a un furro y te pago {reward} FamorCoins')
        job5 = (f'Hiciste una animacion y la subiste a Youtube, ganaste {reward} FamorCoins gracias a los anuncios')
        job6 = (f'Programaste un bot de Discord y te pagaron {reward} FamorCoins')
        job7 = (f'Hiciste un videojuego y ganaste {reward} FamorCoins de personas mayores')
        job8 = (f'Minaste criptomonedas durante 24 horas y ganaste {reward} FamorCoins')
        job9 = (f'Trabaste como albañil y ganaste {reward} FamorCoins')
        job10 = (f'Contruiste una casa en el centro de la ciudad y ganaste {reward} FamorCoins')
        job11 = (f'salvaste la vida de un enfermo y te pago {reward} FamorCoins')
        job12 = (f'un adolescente te pidio un condón y no hiciste nada incomodo así que te dio {reward} FamorCoins como propina')
        job13 = (f'Limpiaste el baño de una escuela pública y te pagaron  {reward} FamorCoins por las molestias')
        job14 = (f'fuiste un presidente corrupto durante 6 años y ganaste {reward} FamorCoins')
        trabajo = ([job0,job1,job2,job3,job4,job5,job6,job7,job8,job9,job10,job11,job12,job13,job14])
        msg = random.choice(trabajo)
        new_FamorCoins = FamorCoins + reward
    else:
        job0 = (f'Te atraparon vendiendo sustancias alucinógenas, te dieron 10 años de carcel y una multa de {reward} FamorCoins')
        job1 = (f'Hacienda descubrió tu canal de Youtube y te cobraron {reward} FamorCoins de impuestos')
        job2 = (f'Intentaste prostituirte pero contragiste una ETS, el hospital te cobró {reward} FamorCoins')
        job3 = (f'Intentaste crear un OnlyFans siendo hombre, pero tus suscriptores se dieron cuenta y te demandaron por {reward} FamorCoins')
        job4 = (f'le apostaste a un extraño a que iba a ganar el boca, perdiste {reward} FamorCoins')
        job5 = (f'Entraste a un casino a jugar, creiste que tenias un juego perfecto y apostaste todo. Perdiste {reward} FamorCoins')
        job6 = (f'La policia te descubrio descargando juegos crackeados y te multaron por {reward} FamorCoins')
        job7 = (f'me quede sin ideas asi que perdiste {reward} FamorCoins')
        job8 = (f'Instalaste Twitter. El psicólogo te cobra {reward} FamorCoins')
        job9 = (f'No te cortaste el pelo entonces te pusieron una demanda de {reward} FamorCoins en tu escuela')
        #job10 = (f'Contruiste una casa en el centro de la ciudad y ganaste {reward} FamorCoin')
        #job11 = (f'salvaste la vida de un enfermo y te pago {reward} FamorCoin')
        #job12 = (f'un adolescente te pidio un condón y no hiciste nada incomodo así que te dio {reward} FamorCoin como propina')
        #job13 = (f'Limpiaste el baño de una escuela pública y te pagaron  {reward} FamorCoin por las molestias')
        #job14 = (f'fuiste un presidente corrupto durante 6 años y ganaste {reward} FamorCoin')
        trabajo = ([job0,job1,job2,job3,job4,job5,job6,job7,job8,job9])
        if FamorCoins < reward:
            test = reward - FamorCoins
            reward = reward - test
        msg = random.choice(trabajo)
        new_FamorCoins = FamorCoins - reward

    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})
@client.command(name = "reclamar")
@commands.cooldown(1,43200,commands.BucketType.user)
async def reclamar(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    minerosmultiplier = datos["MinerosMultiplier"]
    FamorMiners = datos["FamorMiner"]
    PPmultiplier = datos["PPmultiplier"]
    if FamorMiners == 0:
        msg = "No tienes ningun minero"
        await output(ctx,msg)
        return
    eficiencia_amt = minerosmultiplier * .10
    eficiencia = 1 + eficiencia_amt
    reward = int(PPmultiplier * ((1000 * eficiencia) * FamorMiners))
    new_FamorCoins = FamorCoins + reward

    msg = f"Recogiste tus {reward} Famorcoins"
    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})
@client.command(name = "apostar")
async def apostar(ctx, cantidad):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    CardCounting = datos["CardCounting"]

    if cantidad == None:
        msg = "Escribe un numero después de !apostar"
        await output(ctx,msg)
        return
    cantidad = int(cantidad)
    if cantidad > FamorCoins:
        msg = "No tienes suficiente dinero."
        await output(ctx,msg)
        return
    if cantidad <= 0:
        msg = "No puedes apostar 0 cabeza de mazapán"
        await output(ctx,msg)
        return
    result = random.randint(0,100)
    prob = 50 + CardCounting
    if result <= prob:
        msg = f"Felicidades, tus {cantidad} FamorCoins se multiplicaron y ganaste {cantidad} FamorCoins :partying_face: "
        cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": FamorCoins + cantidad}})
        await output(ctx,msg)
        return
    msg = f"Ay no, perdiste tus {cantidad} FamorCoins :cry:"
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": FamorCoins - cantidad}})
    await output(ctx,msg)
@client.command(name = "donar")
async def donar(ctx,usuario:discord.Member,cantidad):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]

    if usuario == None:
        msg = "Introduce un usuario a quien donar"
        await output(ctx,msg)
        return
    if user == usuario:
        msg = "No puedes donarte a ti mismo cara de choclo"
        await output(ctx,msg)
        return
    amt = int(cantidad)
    if amt <= 0:
        msg = "No puedes donar 0 higo de la verdura" 
    if FamorCoins < amt:
        msg = "No tienes suficiente dinero"
        return
    await abrir_cuenta(ctx,usuario)
    datos2 = cluster_data.find_one({"id": usuario.id})
    FamorCoins2 = datos2["FamorCoins"]
    new_FamorCoins = FamorCoins - amt
    new_FamorCoins2 = FamorCoins2 + amt
    msg = f"Enviaste {amt} FamorCoins a {usuario}"

    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})
    cluster_data.update_one({"id": usuario.id}, {"$set":{"FamorCoins": new_FamorCoins2}})

#personalizacion
@client.command(name = "color")
@commands.has_permissions(administrator = True)
async def change_color(ctx,red = None,green = None,blue = None):
    guild_id = str(ctx.guild.id)
    cluster_data = database[guild_id]
    serverconfig = cluster_data.find_one({"server_id": ctx.guild.id})

    if serverconfig == None:
        server_config = {"server_id": ctx.guild.id,"embed_color": [255, 127, 0],"join_channel": None,"roles": []}
        cluster_data.insert_one(server_config)


    if red == None or green == None or blue == None:
        msg = "Introduce el color en RGB ejemplo: 255 255 255"
        await output(ctx,msg)
        return
    try:
        red = int(red)
        green = int(green)
        blue = int(blue)
    except: 
        msg = "Asegurate que los numeros estén entre 0 y 255"
        await output(ctx,msg)
        return
    #estos 3 if se pueden combinar en uno solo pero no me gusta tener tantos or or or or asi que lo deje asi
    if red < 0 or red > 255:
        msg = "Asegurate que los numeros estén entre 0 y 255"
        await output(ctx,msg)
        return
    if green < 0 or green > 255:
        msg = "Asegurate que los numeros esteé entre 0 y 255"
        await output(ctx,msg)
        return
    if blue < 0 or blue > 255:
        msg = "Asegurate que los numeros estén entre 0 y 255" 
        await output(ctx,msg)
        return

    cluster_data = await get_collection(ctx)
    serverconfig = cluster_data.find_one({"server_id": ctx.guild.id})
    cluster_data.update_one({"server_id": ctx.guild.id}, {"$set":{"embed_color": [red,green,blue]}})

    msg = f"El color se ha establecido a ({red},{green},{blue})"
    await output(ctx,msg)
@client.command(name = "agregarrol")
@commands.has_permissions(administrator = True)
async def add_roles(ctx,*,role=None):
    if role == None:
        msg = "Introduce un rol a añadir"
        await output(ctx,msg)
        return
    try:
        role1 = get(ctx.guild.roles, name=role)
        ver = role1.id
    except:
        msg = "El rol introducido no existe, asegurate de haberlo escrito bien"
        await output(ctx,msg)
        return
    cluster_data = await get_collection(ctx)
    serverconfig = cluster_data.find_one({"server_id": ctx.guild.id})
    if serverconfig == None:
        server_config = {"server_id": ctx.guild.id,"embed_color": [255, 127, 0],"join_channel": None,"roles": []}
        cluster_data.insert_one(server_config)
    roles = serverconfig["roles"]

    if role in roles:
        msg = f"el rol ya esta en la lista"
        await output(ctx,msg)
        return
    roles.append(role)
    cluster_data.update_one({"server_id": ctx.guild.id}, {"$set":{"roles": roles}})
    msg = f"rol agregado, los roles existentes en orden son: {roles}"
    await output(ctx,msg)
@client.command(name = "quitarrol")
@commands.has_permissions(administrator = True)
async def remove_roles(ctx,*,role=None):
    if role == None:
        msg = "Introduce un rol a quitar"
        await output(ctx,msg)
        return
    try:
        role1 = get(ctx.guild.roles, name=role)
        ver = role1.id
    except:
        msg = "El rol introducido no existe, asegurate de haberlo escrito bien"
        await output(ctx,msg)
        return
    cluster_data = await get_collection(ctx)
    serverconfig = cluster_data.find_one({"server_id": ctx.guild.id})
    if serverconfig == None:
        server_config = {"server_id": ctx.guild.id,"embed_color": [255, 127, 0],"join_channel": None,"roles": []}
        cluster_data.insert_one(server_config)
    roles = serverconfig["roles"]

    if role not in roles:
        msg = f"el rol no esta en la lista"
        await output(ctx,msg)
        return

    roles.remove(role)
    cluster_data.update_one({"server_id": ctx.guild.id}, {"$set":{"roles": roles}})
    msg = f"rol eliminado, los roles restantes en orden son: {roles}"
    await output(ctx,msg)
@client.command(name = "roles")
@commands.has_permissions(administrator = True)
async def show_roles(ctx):
    cluster_data = await get_collection(ctx)
    serverconfig = cluster_data.find_one({"server_id": ctx.guild.id})
    if serverconfig == None:
        server_config = {"server_id": ctx.guild.id,"embed_color": [255, 127, 0],"join_channel": None,"roles": []}
        cluster_data.insert_one(server_config)
    roles = serverconfig["roles"]
    msg = f"los roles existentes en orden son: {roles}"
    await output(ctx,msg)


#tienda
#todo lo de la tienda recomiendo hacerlo de nuevo, no solo esta mal hecho sino que deberia de estar programado en OOP, pero en el momento no sabia como
@client.command(name = "tienda")
async def tienda(ctx):
    embedcolor = await get_embed_color(ctx)
    embed=discord.Embed(title="Tienda", description="Puedes comprar productos", color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    embed.add_field(name="1) Mensaje motivador para FamorTech   -   1000",value = "Yo FamorBot se lo enviaré y te enviaré el recibo.", inline=False)
    embed.add_field(name="2) Mensaje motivador para cualquier persona   -   1000",value = "Yo FamorBot le enviaré un mensaje motivador a quien quieras.", inline=False)
    embed.add_field(name="3) VIP en Twitch(solo primeras 3 personas)   -   100000000",value = "Te doy VIP en Twitch",inline=False)
    embed.set_footer(text="Escribe !comprar para comprar algo")
    await ctx.send(embed=embed)
@client.command(name = "comprar")
async def comprar(ctx,producto, usuario:discord.User):
    if producto == '1':
        await prod1(ctx)
    elif producto == '2':
        await prod2(ctx,usuario)
    else:
        msg = "Introduce el producto"
        await output(ctx,msg)
async def prod1(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    price = 1000
    await user_delay()
    FamorTech = await client.fetch_user(660309982138466324)
    motrandom = (random.choice(rngmsg.motivacion))

    if FamorCoins >= price:
        msg = ("Tu compra se ha realizado con exito")
        await user.send(f"Mensaje enviado a FamorTech: {motrandom}")
        await FamorTech.send(f"""{user} envio esto: {motrandom}""")  
        new_FamorCoins = FamorCoins - price
    else:
        msg = ("No tienes suficiente dinero")

    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})
async def prod2(ctx, usuario:discord.User):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    price = 1000
    motrandom = (random.choice(rngmsg.motivacion))

    if FamorCoins >= price:
        msg = ("Tu compra se ha realizado con exito")
        await user.send(f"Mensaje enviado a {usuario}: {motrandom}")
        await usuario.send(f"""{user} te envio esto, seguro le importas: 
        {motrandom}""") 
        new_FamorCoins = FamorCoins - price
    else:
        msg = ("No tienes suficiente dinero")

    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})


#mejoras
#lo mismo que la tienda
@client.command(name = "mejoras")
async def mejoras(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorMiner = datos["FamorMiner"]
    EarningMultiplier = datos["EarningMultiplier"]
    MinerosMultiplier = datos["MinerosMultiplier"]
    UpgradeCostDivider = datos["UpgradeCostDivider"]
    preciominero = int(10000 / UpgradeCostDivider)
    increaser = pow(1.75,EarningMultiplier)
    preciomultiplier = int((2000 * increaser) / UpgradeCostDivider)
    increaser2 = pow(1.50,MinerosMultiplier)
    preciomultiplier2 = int((2000 * increaser2) / UpgradeCostDivider)

    embedcolor = await get_embed_color(ctx)
    embed=discord.Embed(title="Mis mejoras",color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    embed.add_field(name = f"1) Mineros   -   Te dan 1000 FamorCoins al dia cada uno",value = f"Minero nivel: {FamorMiner}   -   siguiente nivel: {preciominero}", inline=False)
    embed.add_field(name = f"2) Multiplicador de ganancias   -   Multiplica tus ganancias por el nivel de tu multiplicador",value = f"Multiplicador nivel: {EarningMultiplier}   -   siguiente nivel: {preciomultiplier}", inline=False)
    embed.add_field(name = f"3) eficiencia energética   -   Tus Mineros son 10% mas eficientes por nivel, por lo tanto ganas 10% más",value = f"Eficiencia nivel: {MinerosMultiplier}   -   siguiente nivel: {preciomultiplier2}", inline=False)
    embed.set_footer(text="Escribe !mejorar para mejorar una habilidad")
    await ctx.send(embed=embed)
@client.command(name = "mejorar")
async def mejorar(ctx,mejora):
    if mejora == '1':
        await mineros(ctx)
    elif mejora == '2':
        await earning_multiplier(ctx)
    elif mejora == '3':
        await mineros_multiplier(ctx)
    else:
        msg = "Elige una mejora valida"
        await output(ctx,msg)
async def mineros(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    FamorMiner = datos["FamorMiner"]
    UpgradeCostDivider = datos["UpgradeCostDivider"]
    price = int(10000 / UpgradeCostDivider)

    if FamorCoins >= price:
        new_FamorMiner = FamorMiner + 1
        new_FamorCoins = FamorCoins - price
        msg = ("Tu compra se ha realizado con exito")
    else:
        msg = "No tienes suficiente dinero"
    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorMiner": new_FamorMiner}})
async def earning_multiplier(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    EarningMultiplier = datos["EarningMultiplier"]
    UpgradeCostDivider = datos["UpgradeCostDivider"]
    increase = pow(1.75,EarningMultiplier)
    price = int((2000 * increase) / UpgradeCostDivider)
    if FamorCoins >= price:
        new_EarningMultiplier = EarningMultiplier + 1
        new_FamorCoins = FamorCoins - price
        msg = ("Tu compra se ha realizado con exito")
    else:
        msg = "No tienes suficiente dinero"
    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})
    cluster_data.update_one({"id": user.id}, {"$set":{"EarningMultiplier": new_EarningMultiplier}})
async def mineros_multiplier(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    MinerosMultiplier = datos["MinerosMultiplier"]
    UpgradeCostDivider = datos["UpgradeCostDivider"]
    increase = pow(1.5,MinerosMultiplier)
    price = int((1000 * increase) / UpgradeCostDivider)
    if FamorCoins >= price:
        new_MinerosMultiplier = MinerosMultiplier + 1
        new_FamorCoins = FamorCoins - price
        msg = ("Tu compra se ha realizado con exito")
    else:
        msg = "No tienes suficiente dinero"
    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"FamorCoins": new_FamorCoins}})
    cluster_data.update_one({"id": user.id}, {"$set":{"MinerosMultiplier": new_MinerosMultiplier}})


#prestigios
#lo mismo que la tienda
@client.command(name = "prestigios")
async def prestigios(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    FamorCoins = datos["FamorCoins"]
    PrestigePoints = datos["PrestigePoints"]
    Next_Prestige_Points = int(math.sqrt(FamorCoins)) 
    embedcolor = await get_embed_color(ctx)

    embed=discord.Embed(title= "Prestigios", description= "Al hacer prestigio perderás todas tus mejoras y FamorCoins, pero ganarás Puntos de Prestigio con los cuales puedes comprar mejoras superiores!",color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    embed.add_field(name = f"Tienes {PrestigePoints} Puntos de Prestigio",value = f"Si reinicias ahora, ganarás {Next_Prestige_Points} Puntos de Prestigio", inline=False)
    embed.set_footer(text="Escribe !prestigiarse para realizar un prestigio")
    await ctx.send(embed=embed)
@client.command(name = "prestigiarse")
async def reiniciar(ctx):
    author = ctx.author
    await abrir_cuenta(ctx,author)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": author.id})
    FamorCoins = datos["FamorCoins"]
    FamorMiner = datos["FamorMiner"]
    EarningMultiplier = datos["EarningMultiplier"]
    MinerosMultiplier = datos["MinerosMultiplier"]
    PrestigePoints = datos["PrestigePoints"]
    if FamorCoins < 250000:
        msg = "Necesitas por lo menos 250,000 FamorCoins para realizar un prestigio"
        await output(ctx,msg)
        return
    Next_Prestige_Points = int(math.sqrt(FamorCoins))
    new_Prestige_Points = Next_Prestige_Points + PrestigePoints

    embedcolor = await get_embed_color(ctx)
    embed=discord.Embed(title= f"{author} estás seguro de que quieres reiniciar?",color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    embed.add_field(name = f"Si reinicias ahora, ganarás {Next_Prestige_Points} Puntos de Prestigio",value = f"Reacciona con ✅ para confirmar ", inline=False)
    reac = await ctx.send(embed=embed)
    await reac.add_reaction('✅')

    def check(reaction, user):
        return user == author and str(reaction.emoji) == '✅'
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        return
    else:
        cluster_data.update_one({"id": author.id}, {"$set":{"FamorCoins": 250}})
        cluster_data.update_one({"id": author.id}, {"$set":{"FamorMiner": 0}})
        cluster_data.update_one({"id": author.id}, {"$set":{"EarningMultiplier": 1}})
        cluster_data.update_one({"id": author.id}, {"$set":{"MinerosMultiplier": 0}})
        cluster_data.update_one({"id": author.id}, {"$set":{"PrestigePoints": new_Prestige_Points}})
        msg = "Te has prestigiado! escribe !prestigios para ver tus Puntos de Prestigio"
        await output(ctx,msg)
@client.command(name = "tiendaprestigios")
async def tiendaprestigios(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    PrestigePoints = datos["PrestigePoints"]
    PPmultiplier = datos["PPmultiplier"]
    CardCounting = datos["CardCounting"]
    UpgradeCostDivider = datos["UpgradeCostDivider"]
    PPmultiplier_increase = pow(1.75,PPmultiplier)
    PPmultiplier_price = int(57 * PPmultiplier_increase)
    divider_increase = pow(1.75,UpgradeCostDivider)
    divider_price = int(57 * divider_increase)
    CardCounting_increase = pow(1.5,CardCounting)
    CardCounting_price = int(10 * CardCounting_increase)

    embedcolor = await get_embed_color(ctx)

    embed=discord.Embed(title="Tienda de Prestigiados",description = f"Tienes {PrestigePoints} Puntos de Prestigio",color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    embed.add_field(name = f"1) Evasión de impuestos   -   incrementa tus ganancias en un 100% por nivel",value = f"Evasión de impuestos nivel: {PPmultiplier}   -   siguiente nivel: {PPmultiplier_price}", inline=False)
    embed.add_field(name = f"2) Card Counting   -   aumenta tus probabilidades de ganar en apuestas por 1% por nivel",value = f"Card Counting nivel: {CardCounting}   -   siguiente nivel: {CardCounting_price}", inline=False)
    embed.add_field(name = f"3) Divisor de coste de mejora   -   divide el precio de las mejoras por el numero de nivel",value = f"Divisor nivel: {UpgradeCostDivider}   -   siguiente nivel: {divider_price}", inline=False)
    embed.set_footer(text="Escribe !mejorarp para mejorar tus habilidades")
    await ctx.send(embed=embed)
@client.command(name = "mejorarp")
async def mejorarp(ctx,opcion):
    if opcion == '1':
        await PPmultiplier(ctx)
    elif opcion == '2':
        await CardCounting(ctx)
    elif opcion == '3':
        await UpgradeCostDivider(ctx)
    else:
        msg = "Escribe una mejora valida"
        await output(ctx,msg)
async def PPmultiplier(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    PrestigePoints = datos["PrestigePoints"]
    PPmultiplier = datos["PPmultiplier"]

    increase = pow(1.75,PPmultiplier)
    price = int(57.1428 * increase)
    if PrestigePoints <= price:
        msg = ("No tienes suficientes puntos")
        await output(ctx,msg)
        return
    msg = "Tu compra se ha relizado con exito"
    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"PrestigePoints": PrestigePoints - price}})
    cluster_data.update_one({"id": user.id}, {"$set":{"PPmultiplier": PPmultiplier + 1}})
async def CardCounting(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    PrestigePoints = datos["PrestigePoints"]
    CardCounting = datos["CardCounting"]

    increase = pow(1.5,CardCounting)
    price = int(10 * increase)
    if CardCounting >= 25:
        msg = "Mejora al máximo"
        await output(ctx,msg)
        return
    if PrestigePoints <= price:
        msg = "No tienes suficientes puntos"
        await output(ctx,msg)
        return
    msg = "Tu compra se ha realizado con exito"    
    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"PrestigePoints": PrestigePoints - price}})
    cluster_data.update_one({"id": user.id}, {"$set":{"CardCounting": CardCounting + 1}})
async def UpgradeCostDivider(ctx):
    user = ctx.author
    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    PrestigePoints = datos["PrestigePoints"]
    UpgradeCostDivider = datos["UpgradeCostDivider"]

    increase = pow(1.75,UpgradeCostDivider)
    price = int(57.1428 * increase)
    if PrestigePoints <= price:
        msg = "No tienes suficientes puntos"
        await output(ctx,msg)
        return
    msg = "Tu compra se ha realizado con exito"    
    await output(ctx,msg)
    cluster_data.update_one({"id": user.id}, {"$set":{"PrestigePoints": PrestigePoints - price}})
    cluster_data.update_one({"id": user.id}, {"$set":{"UpgradeCostDivider": UpgradeCostDivider + 1}})


#niveles
@client.listen()
async def on_message(ctx):
    if ctx.content.startswith("!"):
        return
    if ctx.author.bot == True:
        return
    user = ctx.author
    embedcolor = await get_embed_color(ctx)
    roles = await get_server_roles(ctx)

    await abrir_cuenta(ctx,user)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": user.id})
    xp=datos["xp"]
    cluster_data.update_one({"id": user.id}, {"$set":{"xp": xp + 5}})
    lvl = 0
    while True:
        if xp < ((50*(lvl**2))+(50*(lvl-1))):
            break
        lvl += 1
    xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
    if xp == 0:
        embed = discord.Embed(description=f"{user.mention} Subiste al nivel **{lvl}**!",color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
        embed.set_footer(text=random.choice(rngmsg.motivacion))
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.channel.send(embed=embed)
        for i in range(len(roles)):
            if lvl == (i + 1) * 5:
                await user.add_roles(discord.utils.get(user.guild.roles, name=roles[i]))
                embed = discord.Embed(description=f"{user.mention} Ganaste el rol **{roles[i]}**!",color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
                embed.set_thumbnail(url=user.avatar_url)
                await ctx.channel.send(embed=embed)
@client.command(name = "estadisticas")
async def estadisticas(ctx,usuario:discord.User = None):
    if usuario == None:
        usuario = ctx.author
    await abrir_cuenta(ctx,usuario)
    cluster_data = await get_collection(ctx)
    datos = cluster_data.find_one({"id": usuario.id})
    FamorCoins = datos["FamorCoins"]
    xp = datos["xp"]
    lvl = 0
    rank = 0
    embedcolor = await get_embed_color(ctx)

    while True:
        if xp < ((50*(lvl**2))+(50*(lvl-1))):
            break
        lvl += 1
    xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
    progreso = int(xp/((lvl * 100)/10))
    rankings = cluster_data.find().sort("FamorCoins",-1)
    for x in rankings:
        rank += 1 
        if datos["id"] == x["id"]:
            break
    embed = discord.Embed(title=f"Estadisticas de {usuario.name}",color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    embed.add_field(name="Nombre",value=usuario.mention,inline=True)
    embed.add_field(name="XP",value=f"{xp}/{int(200*((1/2)*lvl))}",inline=True)
    embed.add_field(name="Nivel",value=lvl,inline=True)
    embed.add_field(name="FamorCoins",value=FamorCoins,inline=True)
    embed.add_field(name="Top",value=f"{rank}/{ctx.guild.member_count}",inline=True)
    embed.add_field(name="Barra de progreso",value=progreso * ":blue_square:" + (10-progreso) *":white_large_square:",inline=False)
    embed.set_thumbnail(url=usuario.avatar_url)
    await ctx.channel.send(embed=embed)


#moderacion
@client.command(name = "banear")
@commands.has_permissions(ban_members = True)
async def ban(ctx,miembro:discord.User = None):
    embedcolor = await get_embed_color(ctx)

    if miembro == None:
        msg = "Introduce un usuario"
        await output(ctx,msg)
        return  
    embed = discord.Embed(title = ctx.author.name,description = f"Estas seguro que quieres banear a {miembro.name}", color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('✅')
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅'
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
    except asyncio.TimeoutError:
        a = await ctx.send(f"No reaccionaste al mensaje")
        await msg.delete()
        await a.delete(delay = 5.0)
        return
    await miembro.send(f"Te han baneado de {ctx.guild.name}")
    await ctx.guild.ban(miembro, reason=None)
    msg2 = f"Has baneado a {miembro.mention}"
    await output(ctx,msg2)
@client.command(name = "desbanear")
@commands.has_permissions(ban_members = True)
async def unban(ctx,miembro:discord.User = None):
    embedcolor = await get_embed_color(ctx)

    if miembro == None:
        msg = "Introduce un usuario"
        await output(ctx,msg)
        return

    embed = discord.Embed(title = ctx.author.name,description = f"Estas seguro que quieres desbanear a {miembro.name}", color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('✅')
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅'
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
    except asyncio.TimeoutError:
        a = await ctx.send(f"No reaccionaste al mensaje")
        await msg.delete()
        await a.delete(delay = 5.0)
        return
    usuarios_baneados = await ctx.guild.bans()
    for BanEntry in usuarios_baneados:
        user = BanEntry.user
        if (user.name, user.discriminator) == (miembro.name, miembro.discriminator):
            await ctx.guild.unban(user)
            await user.send(f"Te han desbaneado de {ctx.guild.name}")
            msg2 = f"Has desbaneado a {miembro.mention}"
            await output(ctx,msg2)  
@client.command(name = "expulsar")
@commands.has_permissions(ban_members = True)
async def kick(ctx,miembro:discord.User = None):
    embedcolor = await get_embed_color(ctx)
    if miembro == None:
        msg = "Introduce un usuario"
        await output(ctx,msg)
        return
    embed = discord.Embed(title = ctx.author.name,description = f"Estas seguro que quieres expulsar a {miembro.name}", color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('✅')
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅'
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
    except asyncio.TimeoutError:
        a = await ctx.send(f"No reaccionaste al mensaje")
        await msg.delete()
        await a.delete(delay = 5.0)
        return
    await miembro.send(f"Te han expulsado de {ctx.guild.name}")
    await ctx.guild.kick(miembro, reason=None)
    msg2 = f"Has expulsado a {miembro.mention}"
    await output(ctx,msg2)

#comandos varios
@client.command(name = "meme")
async def meme(ctx):
    subreddit = reddit.subreddit("SpanishMeme")
    memes = []
    top = subreddit.top(limit = 50)
    for submission in top:
        memes.append(submission)

    meme = random.choice(memes)
    nombre = meme.title
    imagen = meme.url

    embedcolor = await get_embed_color(ctx)
    embed = discord.Embed(title = nombre,color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    embed.set_image(url = imagen)
    embed.set_footer(text = "Memes provenientes de r/SpanishMeme")
    await ctx.send(embed=embed)
@client.command(name = "aww")
async def aww(ctx):
    subreddit = reddit.subreddit("aww")
    memes = []
    top = subreddit.top(limit = 50)
    for submission in top:
        memes.append(submission)

    meme = random.choice(memes)
    nombre = meme.title
    imagen = meme.url

    embedcolor = await get_embed_color(ctx)
    embed = discord.Embed(title = nombre,color=discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    embed.set_image(url = imagen)
    embed.set_footer(text = "imagenes provenientes de r/aww")
    await ctx.send(embed=embed)
@client.command(name = "comandos")
async def comandos(ctx):
    arrows = ["⬅️","➡️"]
    pag = 0
    author = ctx.author
    embedcolor = await get_embed_color(ctx)

    #todo esto igualmente se puede mover a una funcion que se ejecute una sola vez para no escribir 200 lineas cada vez que se ejecuta
    #o encontrando otra manera por que no creo que sea muy bueno
    pag0 = discord.Embed(title=f"Lista de comandos disponibles",description ="indice",color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    pag0.add_field(name="**Economia**",value="página 1",inline=False)
    pag0.add_field(name="**Tiendas**",value="página 2",inline=False)
    pag0.add_field(name="**Moderación**",value="página 3",inline=False)
    pag0.add_field(name="**Personalización**",value="página 4",inline=False)
    pag0.add_field(name="**Varios**",value="página 5",inline=False)
    pag0.set_footer(text = "puedes usar las flechas para cambiar de pagina")

    pag1 = discord.Embed(title=f"Lista de comandos disponibles página 1",description ="Economia",color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    pag1.add_field(name="**!ppt**",value="puedes retar a tus amigos a un piedra papel o tijera!",inline=False)
    pag1.add_field(name="**!trabajar**",value="trabajando ganas dinero",inline=False)
    pag1.add_field(name="**!trabajoilegal**",value="los trabajos ilegales pueden quitarte dinero",inline=False)
    pag1.add_field(name="**!reclamar**",value="util cuando tienes mineros",inline=False)
    pag1.add_field(name="**!apostar**",value="puedes apostar todos tus ahorros",inline=False)
    pag1.add_field(name="**!donar**",value="puedes donar tu dinero a quien lo necesite",inline=False)
    pag1.add_field(name="**!estadisticas**",value="te muestra tus estadisticas",inline=False)
    pag1.set_footer(text = "puedes usar las flechas para cambiar de pagina")

    pag2 = discord.Embed(title = f"Lista de comandos disponibles página 2",description ="Tiendas",color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))    
    pag2.add_field(name="**!tienda**",value="muestra la tienda",inline=False)
    pag2.add_field(name="**!comprar**",value="puedes comprar algo de la tienda",inline=False)
    pag2.add_field(name="**!mejoras**",value="muestra tus mejoras",inline=False)
    pag2.add_field(name="**!mejorar**",value="puedes mejorar tus mejoras",inline=False)
    pag2.add_field(name="**!prestigios**",value="obten informacion de los prestigios",inline=False)
    pag2.add_field(name="**!prestigiarse**",value="realiza un prestigio",inline=False)
    pag2.add_field(name="**!tiendaprestigios**",value="muestra las mejoras de prestigio",inline=False)
    pag2.add_field(name="**!mejorarp**",value="mejora tus mejoras de prestigio",inline=False)
    pag0.set_footer(text = "puedes usar las flechas para cambiar de pagina")

    pag3 = discord.Embed(title = f"Lista de comandos disponibles página 3",description ="Moderación (requiere permisos)",color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))    
    pag3.add_field(name="**!banear**",value="banea a un usuario",inline=False)
    pag3.add_field(name="**!desbanear**",value="desbanea a un usuario",inline=False)
    pag3.add_field(name="**!expulsar**",value="expulsa a un usuario",inline=False)
    pag0.set_footer(text = "puedes usar las flechas para cambiar de pagina")

    pag4 = discord.Embed(title = f"Lista de comandos disponibles página 4",description ="Personalización (requiere permisos de administrador)",color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))    
    pag4.add_field(name="**!color**",value="cambia el color de los mensajes",inline=False)
    pag4.add_field(name="**!agregarrol**",value="agrega un rol a los niveles",inline=False)
    pag4.add_field(name="**!quitarrol**",value="quita un rol de los niveles",inline=False)
    pag4.add_field(name="**!roles**",value="muestra los roles de los niveles",inline=False)
    pag0.set_footer(text = "puedes usar las flechas para cambiar de pagina")

    pag5 = discord.Embed(title = f"Lista de comandos disponibles página 5",description ="Varios",color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))    
    pag5.add_field(name="**!aww**",value="muestra una imagen linda",inline=False)
    pag5.add_field(name="**!meme**",value="muestra un meme",inline=False)
    pag5.add_field(name="**!comandos**",value="muestra todos los comandos disponibles",inline=False)
    pag5.add_field(name="**!detalles**",value="muestra los detalles de un comando",inline=False)
    pag0.set_footer(text = "puedes usar las flechas para cambiar de pagina")

    def check(reaction, user):
        if user == author and str(reaction.emoji) in arrows:
            return reaction,user
    paginas = [pag0,pag1,pag2,pag3,pag4,pag5]
    while True:
        embed = paginas[pag]
        msg = await ctx.send(embed=embed)
        if pag == 0:
            await msg.add_reaction(arrows[1])
        elif pag == 5:
            await msg.add_reaction(arrows[0])
        else:
            for x in arrows:
                await msg.add_reaction(x)
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return
        else:
            if str(reaction) == "⬅️":
                pag -= 1
            if str(reaction) == "➡️":
                pag += 1
        await msg.delete(delay = 10.0)
@client.command(name = "detalles")
async def commands_description(ctx,*,command = None):
    if command == None:
        await output(ctx,msg = "Introduce un comando a consultar")
    commands = rngmsg.commands
    if command not in commands:
        await output(ctx,msg = "El comando introducido no existe")
        return
    descripcion = commands[command]["descripcion"]
    uso = commands[command]["uso"]
    ejemplo = commands[command]["ejemplo"]
    notas = commands[command]["notas"]

    embedcolor = await get_embed_color(ctx)
    embed = discord.Embed(title = command,color = discord.Colour.from_rgb(embedcolor[0],embedcolor[1],embedcolor[2]))
    for x in commands[command]:
        embed.add_field(name = x,value= commands[command][x],inline=False)
    await ctx.send(embed=embed)

#todo esto no funciona, investigue mucho sobre esto y todo deberia de funcionar pero pues simplemente no lo hace asi que lo dejo ahi
#creo que el codigo de ahorita es uno modificado que no funciona de todos modos no es el original que mas o menos funcionaba
@client.command(name = "r")
async def play(ctx,url):
    if ctx.author.voice is None:
        await ctx.send("Unete a un canal de voz para empezar.")
        return
    author_vc = ctx.author.voice.channel
    await author_vc.connect()

    #{'format': 'bestaudio','source_address': '0.0.0.0','post_processorss': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferedquality': '192'}]}
    YDL_OPTIONS = {'format':'bestaudio'}
    FFMPEG_OPTIONS = {'options': '-vn'}
    vc = ctx.voice_client

    video = pafy.new(url).getbestaudio().url
    vc.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(video)))
    vc.source.volume = 0.5

@client.command(name = "d")
async def stop(ctx):
    voice_chat = ctx.voice_client
    await voice_chat.disconnect()

@client.command(name = "p")
async def pause(ctx):
    voice_chat = ctx.voice_client
    await voice_chat.pause()

@client.command(name = "c")
async def resumir(ctx):
    voice_chat = ctx.voice_client
    await voice_chat.resume()

client.run(rngmsg.token)   #rngmsg es un documento aparte donde esta mi token de discord

##rngmsg.py##
mot0 = "El único modo de hacer un gran trabajo es amar lo que haces - Steve Jobs"
mot1 = "Nunca pienso en las consecuencias de fallar un gran tiro… cuando se piensa en las consecuencias se está pensando en un resultado negativo - Michael Jordan"
mot2 = "El dinero no es la clave del éxito; la libertad para poder crear lo es - Nelson Mandela" 
mot3 = "Cuanto más duramente trabajo, más suerte tengo - Gary Player"
mot4 = "La inteligencia consiste no sólo en el conocimiento, sino también en la destreza de aplicar los conocimientos en la práctica - Aristóteles"
mot5 = "El trabajo duro hace que desaparezcan las arrugas de la mente y el espíritu - Helena Rubinstein "
mot6 = "Cuando algo es lo suficientemente importante, lo haces incluso si las probabilidades de que salga bien no te acompañan - Elon Musk"
mot7 = "Escoge un trabajo que te guste, y nunca tendrás que trabajar ni un solo día de tu vida - Confucio"
mot8 = "Un sueño no se hace realidad por arte de magia, necesita sudor, determinación y trabajo duro - Colin Powell"
mot9 = "Cuéntamelo y me olvidaré. enséñamelo y lo recordaré. involúcrame y lo aprenderé - Benjamin Franklin "
mot10 = "La lógica te llevará de la a a la z. la imaginación te llevará a cualquier lugar - Albert Einstein"
mot11 = "A veces la adversidad es lo que necesitas encarar para ser exitoso - Zig Ziglar "
mot12 = "Para tener éxito tu deseo de alcanzarlo debe ser mayor que tu miedo al fracaso - Bill Cosby"
mot13 = "Ejecuta tus conocimientos con la maestría del que sigue aprendiendo - Jonathan García-Allen"
mot14 = "Cuando pierdas, no pierdas la lección - Dalai Lama"
mot15 = "El amor es una magía,una simple fantasía, es como un sueño. Es como una luz que se esparce por el alma, y recorre como el agua hasta que llega al corazón -Tito "
mot16 = "Al corazón de un hombre se llega por el estómago"
mot17 = "La semilla debe tocar el suelo para poder crecer"
mot18 = "Si la risa es una curva ponle una linea continua, la felicidad no es tan ambigua"
mot19 = "Para ser buen aprendiz fijate donde te heriste, ya que en cada cicatríz podrás ver lo que aprendiste"
mot20 = "No busques el sentido de estar vivo y existir,pero procura vivir por aquello que has sentido"
mot21 = "Si no vez a cupido mejor esperar paciente, el amor a fuego lento llega mas rapidamente"
mot22 = "Hasta la tristeza sabe que reir es lo que toca, por que las lagrimas bajan de los ojos a la boca"
mot23 = "Puedes perseguir tu sombra dando pasos hacia atrás, o puedes seguir la mia que avanza donde tu estás"
mot24 = "El agua moja..."
mot25 = "Se como el corazón, que late y que late sin una razón"
mot26 = "Escribir un poema es facíl si existe un motivo y hasta puede esperarse un consuelo de la fantasía"
mot27 = "No busques los errores, busca un remedio - Henry Ford"
mot28 = "La vida es una aventura, atrévete - Teresa de Calcuta"
mot29 = "Tu actitud, no tu aptitud, determinará tu altitud - Zig Ziglar"
mot30 = "Si te caíste ayer, levántate hoy - H. G. Wells"
motivacion = ([mot0,mot1,mot2,mot3,mot4,mot5,mot6,mot7,mot8,mot9,mot10,mot11,mot12,mot13,mot14,mot15,mot16,mot17,mot18,mot19,mot20,mot21,mot22,mot23,mot24,mot25,mot25,mot26,mot27,mot28,mot29,mot30])

token = 'tu token' #ep 1

commands = {
        "!ppt": {
            "descripcion": "es un comando con el cual puedes retar a otro usuario a un duelo de piedra papel o tijera",
            "uso":"para utilizarlo, después del comando escribes el usuario a quien retar y la cantidad a apostar",
            "ejemplo": "!ppt @FamorTech 100",
            "notas": "ninguna"},
        "!trabajar": {
            "descripcion": "te da dinero",
            "uso":"solo escribes el comando",
            "ejemplo": "!trabajar",
            "notas": "puedes ganar más dinero con mejoras y solo se puede usar cada 5 minutos"},
        "!trabajoilegal": {
            "descripcion": "funciona como !trabajar, pero con una probabilidad de perder dinero",
            "uso":"solo escribes el comando",
            "ejemplo": "!trabajoilegal",
            "notas": "puedes ganar más dinero con mejoras"},
        "!reclamar": {
            "descripcion": "te da cada 24 horas dinero en relación a tus mineros",
            "uso":"solo escribes el comando",
            "ejemplo": "!reclamar",
            "notas": "puedes ganar más dinero con mejoras"},
        "!apostar": {
            "descripcion": "puedes apostar tu dinero y duplicarlo o perderlo",
            "uso":"escribes la cantidad a apostar después del comando",
            "ejemplo": "!trabajar",
            "notas": "puedes aumentar tu probabilidad de ganar con mejoras de prestigio"},
        "!donar": {
            "descripcion": "puedes donar dinero a otro usuario",
            "uso":"escribes el usuario y después la cantidad a donar ",
            "ejemplo": "!donar @FamorTech 100 ",
            "notas": "ninguna"},
        "!estadisticas": {
            "descripcion": "muestra tus estadísticas como la xp, famorcoins etc, o la de otros usuarios",
            "uso":"para ver tus estadísticas, escribes el comando, para ver las estadísticas de otro usuario, escribes su nombre",
            "ejemplo": "!estadisticas o !estadisticas @FamorTech",
            "notas": "ninguna"},
        "!tienda": {
            "descripcion": "muestra la tienda con cosas para comprar",
            "uso":"solo escribes el comando",
            "ejemplo": "!tienda",
            "notas": "ninguna"},
        "!comprar": {
            "descripcion": "sirve para comprar en la tienda",
            "uso":"escribes el número de producto despues del comando",
            "ejemplo": "!comprar 1",
            "notas": "ninguna"},
        "!mejoras": {
            "descripcion": "muestra la tienda de mejoras con cosas para comprar",
            "uso":"solo escribes el comando",
            "ejemplo": "!mejoras",
            "notas": "ninguna"},
        "!mejorar": {
            "descripcion": "sirve para comprar mejoras ",
            "uso":"escribes el número de mejora despues del comando",
            "ejemplo": "!mejorar 1",
            "notas": "ninguna"},
        "!prestigios": {
            "descripcion": "muestra información sobre prestigios",
            "uso":"solo escribes el comando",
            "ejemplo": "!prestigios",
            "notas": "para prestigiarte escribe !prestigiarse"},
        "!prestigiarse": {
            "descripcion": "reinicia tus datos y te da puntos de prestigio a cambio",
            "uso":"solo escribes el comando",
            "ejemplo": "!prestigiarse",
            "notas": "ninguna"},
        "!tiendaprestigios": {
            "descripcion": "muestra la tienda de mejoras de prestigio",
            "uso":"solo escribes el comando",
            "ejemplo": "!tiendaprestigios",
            "notas": "ninguna"},
        "!mejorarp": {
            "descripcion": "sirve para mejorar tus mejoras de prestigio",
            "uso":"escribes el número de mejora después del comando",
            "ejemplo": "!mejorarp 1",
            "notas": "ninguna"},
        "!banear": {
            "descripcion": "se usa para banear un usuario",
            "uso":"escribes el usuario después del comando",
            "ejemplo": "!banear @FamorTech",
            "notas": "el bot necesita permisos para banear al igual que el usuario que ejecuta el comando"},
        "!desbanear": {
            "descripcion": "se usa para desbanear un usuario",
            "uso":"escribes el usuario después del comando incluyendo su tag",
            "ejemplo": "!desbanear FamorTech#7672",
            "notas": "el bot necesita permisos para banear al igual que el usuario que ejecuta el comando"},
        "!expulsar": {
            "descripcion": "se usa para expulsar un usuario",
            "uso":"escribes el usuario después del comando",
            "ejemplo": "!expulsar @FamorTech",
            "notas": "el bot necesita permisos para expulsar al igual que el usuario que ejecuta el comando"},
        "!color": {
            "descripcion": "cambia el color de los mensajes en un formato rgb",
            "uso":"escribes el color en formato rgb después del comando",
            "ejemplo": "!color 255 255 255",
            "notas": "el color por defecto es 255 127 0"},
        "!agregarrol": {
            "descripcion": "agrega roles para recompensar a los usuarios cuando llegan a ciertos niveles",
            "uso":"escribes el nombre de un rol en tu servidor después del comando",
            "ejemplo": "!agregarrol los mas guapos",
            "notas": "los roles se dan cada 5 niveles, se van a dar en el orden que estén guardados osea que el primer rol guardado se dara al nivel 5 y asi sucesivamente, asi que agrega los roles en orden. Quien use el comando debe tener permisos de administrador"},
        "!quitarrol": {
            "descripcion": "quita los roles utilizados para recompensar a los usuarios cuando llegan a ciertos niveles",
            "uso":"escribes el nombre de un rol en tu servidor después del comando",
            "ejemplo": "!quitarrol los mas guapos",
            "notas": "los roles se dan cada 5 niveles, se van a dar en el orden que estén guardados osea que el primer rol guardado se dara al nivel 5 y asi sucesivamente, asi que agrega los roles en orden"},
        "!roles": {
            "descripcion": "muestra los roles utilizados para recompensar a los usuarios cuando llegan a ciertos niveles",
            "uso":"solo escribes el comando",
            "ejemplo": "!roles",
            "notas": "los roles se dan cada 5 niveles, se van a dar en el orden que estén guardados osea que el primer rol guardado se dara al nivel 5 y asi sucesivamente, asi que agrega los roles en orden"},
        "!aww": {
            "descripcion": "envia una imagen linda",
            "uso":"solo escribes el comando",
            "ejemplo": "!aww",
            "notas": "aveces puede fallar el comando, esto pasa cuando el meme enviado es un video"},
        "!meme": {
            "descripcion": "envia un meme",
            "uso":"solo escribes el comando",
            "ejemplo": "!meme",
            "notas": "ninguna"},
        "!comandos": {
            "descripcion": "muestra una lista de los comandos disponibles",
            "uso":"solo escribes el comando, y utilizas las flechas para cambiar de página",
            "ejemplo": "!comandos",
            "notas": "ninguna"},
        "!detalles": {
            "descripcion": "muestra los detalles de cada comando, en caso de que tengas dudas",
            "uso":"escribes !detalles y el comando a consultar",
            "ejemplo": "!detalles !comandos",
            "notas": "ninguna"}
}
