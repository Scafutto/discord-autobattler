import dict_emojis
import functions_sql
import cmd_char

# Formatting and generating the message to display character information

async def show(ctx, cursor, user_id):
    try:
        # Retrieve characters in the team for the user
        characters, err = await functions_sql.select_team(cursor, user_id)
        if err:
            return err

        # If the user has characters in their team
        if characters:
            # Create a thread to display team information
            thread = await ctx.channel.create_thread(name="Team Information", auto_archive_duration=60)

            # Iterate through each character in the team
            for character in characters:
                # Format and generate a message for each character
                reply_message, err = cmd_char.format_character_show(character)
                if err:
                    return err
                # Send the character information message to the thread
                await thread.send(reply_message)

            return None

        else:
            # If the user doesn't have any characters in their team, inform them
            await ctx.send("You have no characters created.")
            return None

    except Exception as err:
        print("Error on 'cmd_team.show':\n", err)
        return "General error handling the /team show command."


async def add(ctx, conn, cursor, user_id, character_id):
    try:
        # Retrieve character information for the specified character_id and user_id
        character, err = await functions_sql.select_characters(cursor, user_id, character_id)
        if err:
            return err

        # Check if the character exists and belongs to the user
        if not character:
            await ctx.send("The character does not exist or does not belong to you.")
            return None
        
        # Check the current team size for the user
        current_team_size, err = await functions_sql.select_team_count(cursor, user_id)
        if err:
            return err

        # Check if the team is already full (maximum team size is 3)
        if current_team_size >= 3:
            await ctx.send("Your team is already full.")
            return None
        
        # Insert the character into the user's team
        err = await functions_sql.insert_character_in_team(conn, cursor, user_id, character_id)
        if err:
            return err
        
        await ctx.send("Character added to your team.")
        return None

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return ("A general error occurred while adding your character to your team, please contact an admin.")


async def remove(ctx, conn, cursor, user_id, character_id):
    try:
        # Retrieve character information for the specified character_id and user_id
        character, err = await functions_sql.select_characters(cursor, user_id, character_id)
        if err:
            return err

        # Check if the character exists and belongs to the user
        if not character:
            await ctx.send("The character does not exist or does not belong to you.")
            return None
        
        # Check if the character is currently part of the user's team
        in_team, err = await functions_sql.is_in_team(cursor, user_id, character_id)
        if err:
            return err

        # If the character is not part of the user's team, notify the user
        if not in_team:
            await ctx.send("This character is already not part of your team.")
            return None

        # Remove the character from the user's team
        err = await functions_sql.delete_character_in_team(conn, cursor, user_id, character_id)
        if err:
            return err
        
        await ctx.send("Character removed from your team.")
        return None

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return ("A general error occurred while removing your character from your team, please contact an admin.")
