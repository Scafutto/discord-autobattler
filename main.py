import dict_quests
import cmd_char, cmd_team, cmd_achievement, cmd_act
import functions_sql
from interactions import Client, Intents, listen, slash_command, OptionType, slash_option, SlashCommandChoice
import mysql.connector
import re

#==============================================#
#------------------VARIABLES-------------------#
#==============================================#

guild_id = 1184985395256103005
registered_users = []

#==============================================#
#---------------------SQL----------------------#
#==============================================#

db_config = {
    'user': 'user',
    'password': 'password',
    'host': 'localhost',
    'database': 'database_name',
}

#==============================================#
#---------------------BOT----------------------#
#==============================================#

bot = Client(intents=Intents.DEFAULT, delete_unused_application_cmds=True)


@listen() 
async def on_ready():
    await retrieve_registered_users()
    print("Ready")

#==============================================#
#---------------QUALITY OF LIFE----------------#
#==============================================#

async def retrieve_registered_users():
    conn = None
    cursor = None

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    users, err = await functions_sql.select_users(cursor)

    if err:
        print("Error on 'main.retrieve_registered_users':\n", err)
        return

    if users:
        for user in users:
            registered_users.append(user[0])

    if cursor:
        cursor.close()
    if conn:
        conn.close()

    return

def is_registered(user_id):
    if user_id not in registered_users:
        return False
    else:
        return True
  
def is_string_valid(str):
    pattern = r'^[a-zA-Z\s]*$'
    return bool(re.match(pattern, str))

#==============================================#
#------------------COMMANDS--------------------#
#==============================================#
    
#-------------------register-------------------#
@slash_command(
        name="register",
        description="Register to the game",
        scopes=[1184985395256103005],
)
@slash_option(
    name="username",
    description="What's your username? If no value is provided, we will use your discord user instead.",
    required=False,
    opt_type=OptionType.STRING,
    max_length=32
)
async def register(
    ctx,
    username: str = None
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        # Check if the user is already registered
        if is_registered(user_id) == True:
            await ctx.send("You are already registered.")
            return
        
        # If no username provided, use author's name
        if not username:
            username = ctx.author.name

        # Check if the username contains special characters
        if username and is_string_valid(username) == False:
            await ctx.send("Your username contains special characters. Please provide a different username.")
            return

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        err = await functions_sql.insert_user(conn, cursor, user_id, username)

        if err:
            return await ctx.send("An error occurred while registering your user, please contact an admin.")

        registered_users.append(user_id)
        return await ctx.send("You are now registered!")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#---------------------char---------------------#
@slash_command(
    name='char',
    scopes=[1184985395256103005],
    )
async def char(
    ctx,
    ):
    pass

@char.subcommand(
    sub_cmd_name='show',
    sub_cmd_description='Show information of your characters'
    )
async def cmd_char_show(
    ctx,
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        if is_registered(user_id) == False:
            await ctx.send("Please, register first with /register [username]")
            return

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        err = await cmd_char.show(ctx, cursor, user_id,)

        if err:
            return await ctx.send(err)
            
        await ctx.send("Here's the information of your characters.")    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@char.subcommand(
    sub_cmd_name='create',
    sub_cmd_description='Create a new character'
    )
@slash_option(
    name="character",
    description="What character would you like to create",
    required=True,
    opt_type=OptionType.STRING,
    choices=[
        SlashCommandChoice(name="Grizzor", value="Grizzor"),
        SlashCommandChoice(name="Slink", value="Slink"),
        SlashCommandChoice(name="Whizz", value="Whizz"),
        SlashCommandChoice(name="Quill", value="Quill"),
        SlashCommandChoice(name="Pigwell", value="Pigwell")
    ],
)
@slash_option(
    name="character_name",
    description="The new character name",
    required=False,
    opt_type=OptionType.STRING,
    min_length=3,
    max_length=24
)
async def cmd_char_create(
    ctx,
    character: str,
    character_name: str = "",
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        if is_registered(user_id) == False:
            return await ctx.send("Please, register first with /register [username]")

        if character_name and is_string_valid(character_name) == False:
            return await ctx.send("This name contains special characters. Please provide a different one.")
            
        if not character_name:
            character_name = character

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        err =  await cmd_char.create(ctx, conn, cursor, user_id, character, character_name)

        if err:
            return await ctx.send(err)
        
        return await ctx.send("Character succesfully created!")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@char.subcommand(
    sub_cmd_name='delete',
    sub_cmd_description='Deletes a character'
    )
@slash_option(
    name="character_id",
    description="What's the character ID you want to delete",
    required=True,
    opt_type=OptionType.INTEGER,
)
async def cmd_char_delete(
    ctx,
    character_id: int,
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        if is_registered(user_id) == False:
            await ctx.send("Please, register first with /register [username]")
            return

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        err = await cmd_char.delete(ctx, conn, cursor, user_id, character_id)
        if err:
            return await ctx.send(err)

        return await ctx.send("Character successfully deleted.")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#---------------------team---------------------#
@slash_command(
    name='team',
    scopes=[1184985395256103005],
    )
async def team(
    ctx
    ):
    pass

@team.subcommand(
    sub_cmd_name='show',
    sub_cmd_description='Show your active team'
    )
async def cmd_team_show(
    ctx,
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        if is_registered(user_id) == False:
            await ctx.send("Please, register first with /register [username]")
            return

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        err = await cmd_team.show(ctx, cursor, user_id,)

        if err:
            return await ctx.send(err)
            
        return await ctx.send("Here's the information of your team")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@team.subcommand(
    sub_cmd_name='add',
    sub_cmd_description='Add a character to your team'
    )
@slash_option(
    name="character_id",
    description="Character ID to be added to the team.",
    required=True,
    opt_type=OptionType.INTEGER,
)
async def cmd_team_add(
    ctx,
    character_id: int
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        if is_registered(user_id) == False:
            return await ctx.send("Please, register first with /register [username]")

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        err = await cmd_team.add(ctx, conn, cursor, user_id, character_id)

        if err:
            return await ctx.send(err)
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@team.subcommand(
    sub_cmd_name='remove',
    sub_cmd_description='Remove a character from your team'
    )
@slash_option(
    name="character_id",
    description="Character ID to be removed from the team.",
    required=True,
    opt_type=OptionType.INTEGER,
)
async def cmd_team_remove(
    ctx,
    character_id: int
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        if is_registered(user_id) == False:
            return await ctx.send("Please, register first with /register [username]")

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        err = await cmd_team.remove(ctx, conn, cursor, user_id, character_id)

        if err:
            return await ctx.send(err)
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
   

#-----------------achievement------------------#
        
@slash_command(
    name='achievement',
    scopes=[1184985395256103005],
    )
async def achievement(
    ctx,
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        if is_registered(user_id) == False:
            await ctx.send("Please, register first with /register [username]")
            return

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        return await cmd_achievement.show(ctx, cursor, user_id)


    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#--------------------battle--------------------#
        
@slash_command(
    name='act1',
    scopes=[1184985395256103005],
)
@slash_option(
    name="quest",
    description="What quest would you like to launch?",
    required=True,
    opt_type=OptionType.STRING,
    choices=[
        SlashCommandChoice(name="1 - This ratto is fatto", value="This ratto is fatto"),
        SlashCommandChoice(name="2 - Double trouble", value="Double trouble"),
        SlashCommandChoice(name="3 - To the sewers!", value="To the sewers!"),
        SlashCommandChoice(name="4 - Going deeper", value="Going deeper"),
        SlashCommandChoice(name="5 - Ratgabash's Hexing Havoc", value="Ratgabash's Hexing Havoc"),
        SlashCommandChoice(name="6 - Embrace the mud", value="Embrace the mud"),
        SlashCommandChoice(name="7 - That one big fella", value="That one big fella"),
    ],
)
async def cmd_act1(
    ctx,
    quest,
    ):
    try:
        conn = None
        cursor = None

        user_id = str(ctx.author.id)

        if is_registered(user_id) == False:
            await ctx.send("Please, register first with /register [username]")
            return

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        energy, err = await functions_sql.select_energy(conn, cursor, user_id)
        
        if err:
            return await ctx.send(err)
        
        if energy <= 0:
            return await ctx.send("You don't have enough energy to start a battle now, please let your characters recover.")

        err = await functions_sql.update_energy(conn, cursor, user_id)

        if err:
            return await ctx.send(err)

        err = await cmd_act.act1(ctx, conn, cursor, user_id, quest)

        if err:
            return await ctx.send(err)
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

bot.start('TOKEN')
