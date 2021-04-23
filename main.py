import discord
import os
import random
import requests
from replit import db
from keep_open import keep_open

client = discord.Client()

@client.event
async def on_ready():
    print("I am ready!")
    await client.change_presence(activity=discord.Game(name="!help"))

@client.event
async def on_message(message):
    if message.content.startswith("!"):
        query = message.content.split(" ")
        if query[0] == "!p":
            json = getPkmn(query[1]) if len(query) > 1 else getPkmn("random")
            embed = getPkmnEmbed(json)
            sent = await message.channel.send(embed = embed)
            if json != "-1":
                await sent.add_reaction("⭐")
        elif query[0] == "!favs":
            embed = getFavourites(message.author.id)
            await message.channel.send(embed = embed)     
        elif query[0] == "!del":
            embed = deleteFavourite(query[1],str(message.author.id))
            await message.channel.send(embed = embed)
        elif query[0] == "!help":
            embed = getHelp()
            await message.channel.send(embed = embed)


@client.event
async def on_reaction_add(reaction, user):
    if (user != client.user and reaction.message.author == client.user and reaction.emoji =="⭐"):
        footer = reaction.message.embeds[0].footer.text
        if footer != discord.Embed.Empty:
            pokemonId = footer
            if str(user.id) in db:
                db[str(user.id)].append(pokemonId)
            else:
                db[str(user.id)] = [pokemonId]

def getPkmn(id):
    pokemonId = random.randint(1,649)
    if id != "random":
        try:
            pokemonId = int(id)
            if pokemonId > 649 or pokemonId <= 0:
                return "-1"
        except ValueError:
            return "-1"
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemonId}/")
    json = r.json()
    return json

def getPkmnEmbed(json):
    if (json =="-1"):
        return discord.Embed(
            title="Error!",
            description="Choose a valid number between 1 and 649",
            color=0xF04343
        )
    typeList = list(map(lambda x: x["type"]["name"].capitalize(),json["types"]))
    embed = discord.Embed(
        title=json["name"].capitalize(),
        description=f"Type(s): {', '.join(typeList)}",
        color=0x318ca8
    )
    embed.set_thumbnail(url=json["sprites"]["versions"]["generation-v"]["black-white"]["animated"]["front_default"])
    embed.set_footer(text=str(json["id"]))
    embed.add_field(name="Height",value=str(json["height"] / 10) + " m",inline="true")
    embed.add_field(name="Weight",value=str(json["weight"] / 10) + " kg",inline="true")

    return embed

def getFavourites(id):
    embed = discord.Embed(title="Favourite Pokemon", color=0xF3B821)
    if str(id) in db:
        idList = "\n".join(db[str(id)])
        nameList = "\n".join(
            map(lambda x: getPkmn(x)["name"].capitalize(),db[str(id)])
        )
        embed.add_field(name="Name",value=nameList,inline="true")
        embed.add_field(name="Id",value=idList,inline="true")
    else:
        embed.add_field(name="No Favourites!",value="Add a pokemon your favourites with ⭐")
    return embed

def deleteFavourite(pokemonId, userId):
    try:
        db[userId].remove(pokemonId)
        if len(db[userId]) == 0:
            del db[userId]
    except ValueError:
        return discord.Embed(
            title="Error!",
            description="Pokemon does not exist in favourites list",
            color=0xF04343)
    return discord.Embed(
        title="Success!",
        description=f"Removed {pokemonId} from favourites"
    )

def getHelp():
    embed = discord.Embed(title="Command List", color=0xCD333F)
    embed.add_field(name="Command:",value="!p\n!p <id>\n!favs\n!del <id>",inline="true")
    embed.add_field(name="Description:",value="Displays a random pokemon\nDisplays pokemon number `id`\nLists your favourites\nRemoves `id` from your favourites",inline="true")
    return embed

keep_open()
client.run(os.environ['discord-secret'])
