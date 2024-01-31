import dict_emojis, dict_progression, dict_characters
import functions_sql

# Formatting and generating the message to display character information
def format_character_show(character):
    try:
        # Index to access different attributes in the 'character' list
        index = {
            "id": 0,
            "character_class": 1,
            "name": 2,
            "level": 3,
            "experience": 4,
            "vitality": 5,
            "power": 6,
            "defense": 7,
            "critical": 8,
            "speed": 9,
            "taunt": 10,
            "accuracy": 11,
            "dodge": 12,
            "skill1": 13,
            "skill2": 14
        }
        # Add 'emoji' and 'name' to the message
        reply_message = f"# {dict_emojis.characters.get(character[index['character_class']], '')}" 
        reply_message += f" {character[index['name']]}\n"

        # Add 'level' and 'experience' to the message
        reply_message += f"Level {character[index['level']]}"
        reply_message += f" [{character[index['experience']]}/{dict_progression.level_required_xp.get(character[index['level']], '')}]\n"

        # Add 'id' to the message
        reply_message += f"`id: {character[index['id']]}`\n\n"

        # Add 'vitality' and 'taunt' to the message
        reply_message += f"## {dict_emojis.attributes['vitality']}{'':<5} `{character[index['vitality']]:>4}`{'':<15}"
        reply_message += f" {dict_emojis.attributes['taunt']}{'':<5} `{character[index['taunt']]:>4}`\n"

        # Add 'power' and 'defense' to the message
        reply_message += f"## {dict_emojis.attributes['power']}{'':<5} `{character[index['power']]:>4}`{'':<15}"
        reply_message += f" {dict_emojis.attributes['defense']}{'':<5} `{character[index['defense']]:>4}`\n"

        # Add 'critical' and 'speed' to the message
        reply_message += f"## {dict_emojis.attributes['critical']}{'':<5} `{character[index['critical']]:>4}`{'':<15}"
        reply_message += f" {dict_emojis.attributes['speed']}{'':<5} `{character[index['speed']]:>4}`\n"

        # Add 'accuracy' and 'dodge' to the message
        reply_message += f"## {dict_emojis.attributes['accuracy']}{'':<5} `{character[index['accuracy']]:>4}`{'':<15}"
        reply_message += f" {dict_emojis.attributes['dodge']}{'':<5} `{character[index['dodge']]:>4}`\n\n"

        # Add 'skill1' to the message
        reply_message += f"## {dict_emojis.attributes['skill']}{'':<5} `{character[13] if character[13] else '-'}`\n"

        # Add 'skill2' to the message
        reply_message += f"## {dict_emojis.attributes['skill']}{'':<5} `{character[14] if character[14] else '-'}`\n\n"

        return reply_message, None
    except Exception as err:
        return None, err


# Command to show all characters
async def show(
    ctx,
    cursor,
    user_id,
    ):
    try:
        # Get characters associated with the user
        characters, err = await functions_sql.select_characters(cursor, user_id)

        if err:
            return err

        if characters:
            # Create a thread to display characters' information
            thread = await ctx.channel.create_thread(name="Characters Information", auto_archive_duration=60)

            for character in characters:
                # Generate the message for each character
                reply_message, err = format_character_show(character)
                if err:
                    return err
                
                await thread.send(reply_message)

            return None

        else:
            await ctx.send("You have no characters created.")
            return None

    except Exception as err:
        print("Error on 'cmd_char.show':\n", err)
        return "General error handling the /char show command."

# Command to create a new character
async def create(
    ctx,
    conn,
    cursor,
    user_id,
    character,
    character_name
    ):
    try:
        # Check if the selected character is valid
        if character not in dict_characters.characters_attributes:
            return "Please, select a valid character. You can list them with /list char"

        # Check if the character is unlock
        if character not in ["Grizzor", "Quill", "Whizz"]:
            is_unlocked, err = await functions_sql.select_unlocked_characters(cursor, user_id, character)
            if err:
                return err
        
            if not is_unlocked:
                return f"You haven't unlocked `{character}` yet."

        # Check maximum number of characters allowed
        max_characters, err = await functions_sql.select_max_characters(cursor, user_id)
        if err:
            return err

        # Check current characters count for the user
        current_characters, err = await functions_sql.select_characters_count(cursor, user_id)
        if err:
            return err

        if current_characters >= max_characters:
            return "You can't create new characters. Please, increase the number of characters you can have, or delete one of your characters."

        attributes = dict_characters.characters_attributes[character]

        # Insert the new character into the database
        character_id, err = await functions_sql.insert_characters(conn, cursor, user_id, character_name, character, attributes)
        if err:
            return err
        
        current_team_size, err = await functions_sql.select_team_count(cursor, user_id)
        if err:
            return err
        
        # Add the character to the team if applicable
        if current_team_size < 3:
            err = await functions_sql.insert_character_in_team(conn, cursor, user_id, character_id)
            if err:
                return err

        # Get the newly created character's information
        newly_created_character, err = await functions_sql.select_characters(cursor, user_id, character_id)
        if err:
            return err
        
        # Generate the message for the newly created character
        formatted_message, err = format_character_show(newly_created_character)
        if err:
            return err

        # Create a thread to display character creation information
        thread = await ctx.channel.create_thread(name="Character Creation", auto_archive_duration=60)

        await thread.send(formatted_message)

        return None

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return "A general error occurred while deleting your character, please contact an admin."


async def delete(
    ctx,
    conn,
    cursor,
    user_id,
    character_id,
    ):
    try:
        # Check if the character exists and belongs to the user
        character, err = await functions_sql.select_characters(cursor, user_id, character_id)
        if err:
            return err
        
        if not character:
            await ctx.send("The character does not exist or does not belong to you.")
            return None

        in_team, err = await functions_sql.is_in_team(cursor,user_id,character_id)
        if err:
            return err
        
        if in_team:
            await ctx.send("You can't delete a character that is currently part of your team.")
            return None

        err = await functions_sql.delete_characters(conn, cursor, user_id, character_id, character)
        if err:
            return err
        
        return None

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return "A general error occurred while deleting your character, please contact an admin."