import random
import dict_progression, dict_emojis

#==============================================#
#--------------------USERS---------------------#
#==============================================#

async def select_users(cursor):
    try:
        get_registered_users_query = "SELECT id FROM users"
        cursor.execute(get_registered_users_query)
        users = cursor.fetchall()

        return users, None
    
    except Exception as err:
        return None, "Error retrieving your user ID"
    

async def insert_user(conn, cursor, user_id, username):
    try:
        # Insert values into the users table
        insert_user_query = "INSERT INTO users (id, username) VALUES (%s, %s)"
        data = (user_id, username,)
        cursor.execute(insert_user_query, data)

        # Insert values into the currencies table
        insert_currencies_query = "INSERT INTO currencies (USERS_id) VALUES (%s)"
        currencies_data = (user_id,)
        cursor.execute(insert_currencies_query, currencies_data)

        conn.commit()

        return None

    except Exception as err:
        conn.rollback()
        print("Error on 'functions_sql.insert_user':\n", err)
        return "Error creating a new user"


#==============================================#
#------------------CHARACTERS------------------#
#==============================================#

async def select_characters(cursor, user_id, character_id = None):
    try:
        if character_id:
            get_character_query = "SELECT * FROM characters WHERE USERS_id = %s AND id = %s"
            cursor.execute(get_character_query, (user_id, character_id))
            character = cursor.fetchone()

            return character, None
        
        else:
            get_characters_query = "SELECT * FROM characters WHERE USERS_id = %s"
            cursor.execute(get_characters_query, (user_id,))
            characters = cursor.fetchall()

            return characters, None
    
    except Exception as err:
        print("Error on 'functions_sql.select_characters':\n", err)
        return None, "Error retrieving the characters information"


async def insert_characters(conn, cursor, user_id, character_name, character, attributes):
    try:
        insert_character_query = """
            INSERT INTO characters (
                class, name, vitality, power, defense, 
                critical, speed, taunt, accuracy, dodge, USERS_id
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            character,
            character_name, 
            attributes['vitality'],
            attributes['power'],
            attributes['defense'],
            attributes['critical'],
            attributes['speed'],
            attributes['taunt'],
            attributes['accuracy'],
            attributes['dodge'],
            user_id,
            )
        
        cursor.execute(insert_character_query, data)
        character_id = cursor.lastrowid

        conn.commit()

        return character_id, None
    
    except Exception as err:
        conn.rollback()
        print("Error on 'functions_sql.insert_characters':\n", err)
        return None, "Error creating new character"
    

async def select_max_characters(cursor, user_id):
    try:
        get_max_characters_query = "SELECT max_characters FROM currencies WHERE USERS_id = (%s)"
        cursor.execute(get_max_characters_query, (user_id,))
        max_characters = cursor.fetchone()[0]

        return max_characters, None

    except Exception as err:
        print("Error on 'functions_sql.select_max_characters':\n", err)
        return None, "Error retrieving the max number of characters of your account"
    

async def select_characters_count(cursor, user_id):
    try:
        get_character_count_query = "SELECT COUNT(*) FROM characters WHERE USERS_id = (%s)"
        cursor.execute(get_character_count_query, (user_id,))
        current_characters = cursor.fetchone()[0]

        return current_characters, None

    except Exception as err:
        print("Error on 'functions_sql.select_characters_count':\n", err)
        return None, "Error counting the characters in your account"


async def delete_characters(conn, cursor, user_id, character_id, character):
    try:
        remove_from_team_query = "DELETE FROM team WHERE USERS_id = (%s) AND CHARACTERS_id = (%s)"
        cursor.execute(remove_from_team_query, (user_id, character_id))


        insert_into_deleted_query = """
            INSERT INTO deleted_characters 
            (id, class, name, level, experience, vitality, power, defense, critical, speed, taunt, accuracy, dodge, skill1, skill2, USERS_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            character[0], character[1], character[2], character[3], character[4], character[5],
            character[6], character[7], character[8], character[9], character[10],
            character[11], character[12], character[13], character[14], user_id
        )
        cursor.execute(insert_into_deleted_query, data)

        delete_character_query = "DELETE FROM characters WHERE id = %s"
        cursor.execute(delete_character_query, (character_id,))

        conn.commit()

        return None

    except Exception as err:
        conn.rollback()
        print("Error on 'functions_sql.select_characters_count':\n", err)
        return "Error counting the characters in your account"


async def update_character_xp( conn,cursor,character,xp):
    try:
        update_xp_query = """
        UPDATE characters
        SET experience = %s
        WHERE id = %s
        """
        cursor.execute(update_xp_query, (xp, character.id))

        conn.commit()
        return None

    except Exception as err:
        conn.rollback()
        print("Error on /functions_sql.update_character_xp:\n",err)
        return "Error increasing character experience"


async def update_character_level(conn, cursor, character, level):
    try:
        str_upgrades = f"# {character.emoji} {character.name} is now level {level}!\n"

        class_table = getattr(dict_progression, character.character_class.lower())
        class_table_level = class_table[level]

        general_table = dict_progression.general[level]

        if general_table:
            str_upgrades += "## > General Roll\n"
            primary_attribute = class_table["primary"]

            pool_attributes = ["vitality", "power", "defense"]

            pool_distribution = random.randint(1, 3)
            pool = general_table['pool'][pool_distribution]


            pool_attributes = random.sample(pool_attributes, len(pool_attributes))

            while pool_attributes[-1] == primary_attribute:
                random.shuffle(pool_attributes)

            for i, attribute in enumerate(pool_attributes):
                bonus = pool[i]

            
                if attribute == "vitality":
                    bonus = bonus * 5

                current_value = getattr(character, attribute)
                new_value = current_value + bonus
                setattr(character, attribute, new_value)

                try:
                    update_query = f"UPDATE characters SET {attribute} = {new_value} WHERE id = {character.id};"

                    cursor.execute(update_query)
                    conn.commit()

                    str_upgrades += f"## {dict_emojis.attributes[attribute]}{'':<5} `{current_value:>5}`     >>     `{new_value:>5}`\n"

                except Exception as err:
                    conn.rollback()
                    print('Error on /functions_sql.update_character_level:\n', err)
                    return None, "Error trying to update general attributes on database"

            ## Skills
            to_change = None

            if general_table["skill1"]:
                class_table_skill = class_table["skill1"]
                to_change = "skill1"
                n = random.randint(1, 100)
                if n <= 70:
                    skill_name = random.choice(class_table_skill["Common"])
                elif n <= 95:
                    skill_name = random.choice(class_table_skill["Rare"])
                else:
                    skill_name = random.choice(class_table_skill["Epic"])

            if general_table["skill2"]:
                class_table_skill = class_table["skill2"]
                to_change = "skill2"
                n = random.randint(1, 100)
                if n <= 70:
                    skill_name = random.choice(class_table_skill["Common"])
                elif n <= 95:
                    skill_name = random.choice(class_table_skill["Rare"])
                else:
                    skill_name = random.choice(class_table_skill["Epic"])

            if to_change:
                try:
                    update_query = f"UPDATE characters SET {to_change} = '{skill_name}' WHERE id = {character.id};"

                    cursor.execute(update_query)
                    conn.commit()

                    str_upgrades += f"## {dict_emojis.attributes['skill']}{'':<5} `{skill_name}`\n"

                except Exception as err:
                    conn.rollback()
                    print('Error on /functions_sql.update_character_level:\n', err)
                    return None, "Error trying to update skills on database"
                
        if class_table_level:
            str_upgrades += f"## > Class Roll\n"
            n = len(class_table_level)
            pool_distribution = random.randint(1, 3)
            pool = class_table_level[pool_distribution]

            for attribute in pool:
                bonus = pool[attribute]

                current_value = getattr(character, attribute)
                new_value = current_value + bonus
                setattr(character, attribute, new_value)

                try:
                    update_query = f"UPDATE characters SET {attribute} = {new_value} WHERE id = {character.id};"

                    cursor.execute(update_query)
                    conn.commit()

                    str_upgrades += f"## {dict_emojis.attributes[attribute]}{'':<5} `{current_value:>5}`     {'>>'}     `{new_value:>5}`\n"
                    
                except Exception as err:
                    conn.rollback()
                    print('Error on /functions_sql.update_character_level:\n', err)
                    return None, "Error trying to update class attributes on database"

        update_level_query = """
        UPDATE characters
        SET level = %s
        WHERE id = %s
        """
        cursor.execute(update_level_query, (level, character.id))
        conn.commit()

        return str_upgrades, None

    except Exception as err:
        conn.rollback()
        print('Error on /functions_sql.update_character_level:\n', err)
        return None, "Error trying to update character level on database"


#==============================================#
#---------------------TEAM---------------------#
#==============================================#

async def select_team(
    cursor,
    user_id,
    ):   
    try:
        get_team_query = """
            SELECT *
            FROM characters c
            JOIN team t ON c.id = t.CHARACTERS_id
            WHERE t.USERS_id = %s
        """
        cursor.execute(get_team_query, (user_id,))
        characters = cursor.fetchall()

        return characters, None

    except Exception as err:
        print("Error on 'functions_sql.select_team':\n", err)
        return None, "Error retrieving information of your team"


async def is_in_team(   
    cursor,
    user_id,
    character_id,
    ):
    try:
        check_in_team_query = "SELECT * FROM team WHERE USERS_id = (%s) AND CHARACTERS_id = (%s)"
        cursor.execute(check_in_team_query, (user_id, character_id))
        character_in_team = cursor.fetchone()

        return bool(character_in_team), None

    except Exception as err:
        print("Error on 'functions_sql.is_in_team':\n", err)
        return None, "Error checking if character is in your team"


async def select_team_count(cursor, user_id):
    try:
        get_team_count_query = "SELECT COUNT(*) FROM team WHERE USERS_id = (%s)"
        cursor.execute(get_team_count_query, (user_id,))
        team_count = cursor.fetchone()[0]

        return team_count, None
    
    except Exception as err:
        print("Error on 'functions_sql.select_team_count':\n", err)
        return None, "Error counting the characters in your team"
    

async def insert_character_in_team(conn, cursor, user_id, character_id):
    try: 
        add_to_team_query = "INSERT INTO team (USERS_id, CHARACTERS_id) VALUES (%s, %s)"
        cursor.execute(add_to_team_query, (user_id, character_id))
        conn.commit()

        return None
    
    except Exception as err:
        print("Error on 'functions_sql.select_team_count':\n", err)
        return "Error inserting the character in your team"
    

async def delete_character_in_team(conn, cursor, user_id, character_id):
    try:
        remove_from_team_query = "DELETE FROM team WHERE USERS_id = (%s) AND CHARACTERS_id = (%s)"
        cursor.execute(remove_from_team_query, (user_id, character_id))
        conn.commit()

        return None

    except Exception as err:
        conn.rollback()
        print("Error on 'functions_sql.is_in_team':\n", err)
        return None, "Error checking if character is in your team"



#==============================================#
#-----------------ACHIEVEMENTS-----------------#
#==============================================#


async def select_achievements(cursor, user_id):
    try:
        get_achievements_query = "SELECT * FROM achievements WHERE USERS_id = %s AND achievement_value = 1"
        cursor.execute(get_achievements_query, (user_id,))
        achievements = cursor.fetchall()

        return achievements, None

    except Exception as err:
        print("Error on 'functions_sql.select_team_count':\n", err)
        return None, "Error retrieving your achievements"


async def insert_achievement(conn, cursor, user_id, achievement):
    try:
        print(user_id, achievement)
        insert_achievement_query = """
        INSERT INTO achievements (USERS_id, achievement_name, achievement_value)
        VALUES (%s, %s, 1)
        """
        cursor.execute(insert_achievement_query, (user_id, achievement))

        match achievement:
            case "First Victory":
                err = await increase_max_characters(conn, cursor, user_id)
            case "Outnumbered no more":
                err = await increase_max_characters(conn, cursor, user_id)
            case "Rat Trap":
                err = await insert_unlocked_character(conn, cursor, user_id, "Slink")
                
        if err:
            conn.rollback()
            return err

        conn.commit()

    except Exception as err:
        print("Error on functions_sql.insert_achievements:\n", err)
        return "Error inserting achievement to database"

#==============================================#
#--------------------QUESTS--------------------#
#==============================================#

async def select_completed_quests(cursor, user_id):
    try:
        get_completed_quests_query = """
        SELECT act, quest
        FROM completed_quests
        WHERE USERS_id = %s
        """

        cursor.execute(get_completed_quests_query, (user_id,))
        completed_quests = cursor.fetchall()

        return completed_quests, None

    except Exception as err:
        print(err)
        return None, "Error retrieving your completed quests"


async def insert_quest(conn, cursor, user_id, quest):
    try:
        insert_quest_query = """
        INSERT INTO completed_quests (USERS_id, act, quest)
        VALUES (%s, 1, %s)
        """
        cursor.execute(insert_quest_query, (user_id, quest))

        conn.commit()

        return None

    except Exception as err:
        conn.rollback()
        print("Error on /functions_sql.insert_quest:\n", err)

        return "Error marking the quest as completed"


#==============================================#
#------------------CURRENCIES------------------#
#==============================================#
    
async def increase_max_characters(conn,cursor,user_id,):
    try:
        increase_max_characters_query = """
        UPDATE currencies
        SET max_characters = max_characters + 1
        WHERE USERS_id = %s
        """

        cursor.execute(increase_max_characters_query, (user_id,))
        conn.commit()

        return None

    except Exception as err:
        conn.rollback()
        print("Error on /functions_sql.increase_max_characters:\n", err)
        return "Error increasing the max character amount"


async def select_energy(conn, cursor, user_id):
    try:
        select_query = "SELECT energy FROM currencies WHERE USERS_id = %s"
        cursor.execute(select_query, (user_id,))
        result = cursor.fetchone()

        if result:
            energy = result[0]
            return energy, None
        else:
            return None, f"No energy value found for you, please contact an admin"

    except Exception as err:
        conn.rollback()
        print("Error on /functions_sql.select_energy:\n", err)
        return None, "Error retrieving your current Energy value"


async def update_energy( conn,cursor,user_id):
    try:
        update_energy_query = "UPDATE currencies SET energy = GREATEST(0, energy - 1) WHERE USERS_id = %s"
        cursor.execute(update_energy_query, (user_id,))

        conn.commit()
        return None

    except Exception as err:
        conn.rollback()
        print("Error on /functions_sql.update_energy:\n", err)
        return "Error updating energy value"




#==============================================#
#-------------UNLOCKED_CHARACTERS--------------#
#==============================================#

async def select_unlocked_characters(cursor, user_id, character):
    try:
        select_unlocked_characters_query = "SELECT * FROM unlocked_characters WHERE USERS_id = %s AND character_class = %s;"
        cursor.execute(select_unlocked_characters_query, (user_id, character))
        
        result = cursor.fetchone()

        if result:
            return True, None
        else:
            return False, None

    except Exception as err:
        print("Error on /functions_sql.update_energy:\n", err)
        return None, "Error updating energy value"


async def insert_unlocked_character(conn, cursor, user_id, character):
    try:
        insert_query = "INSERT INTO unlocked_characters (USERS_id, character_class) VALUES (%s, %s);"
        cursor.execute(insert_query, (user_id, character))
        conn.commit()

        return None

    except Exception as err:
        conn.rollback()
        print("Error on /functions_sql.insert_unlocked_character:\n", err)
        return "Error inserting unlocked character"
