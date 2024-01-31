import Character
import functions_sql
import dict_characters_select, dict_monsters, dict_quests, dict_colours, dict_actions, dict_emojis
import random

async def battle_wrapper(ctx, conn, cursor, user_id, quest, is_quest_complete):   
    try:

        characters, err = await functions_sql.select_team(cursor, user_id,)

        if err:
            return None, None, None, None, err

        if not characters:
            await ctx.send("You have no characters in your Team. Use `/team add [id]` to populate your team.")
            return None, None, None, None, None

        blue_team, err = handle_blue_team(characters)

        if err:
            return None, None, None, None, err

        blue_team_original = blue_team.copy()

        red_team, achievement, err = handle_red_team(quest)

        if err:
            return None, None, None, None, err

        header, err = format_header(quest, blue_team, red_team)

        if err:
            return None, None, None, None, err

        # Handle combat
        battle_report, is_victory, err = resolve_combat(blue_team, red_team)

        if err:
            return None, None, None, None, err

        # Handle quest/achievements
        achievement = dict_quests.quests_data[quest]["achievement"]
        achievement_message = None

        if is_victory and not is_quest_complete:
            err = await functions_sql.insert_quest(conn,cursor,user_id,quest)

            if err:
                return None, None, None, None, err
        
            if achievement:
                achievement_message , err = handle_quest_achievement(achievement)

                if err:
                    return None, None, None, None, err
                
                err = await functions_sql.insert_achievement(conn, cursor, user_id, achievement["name"])

                if err:
                    return None, None, None, None, err

        # Handle xp/leveling
        progression_report = None
        if is_victory:
            progression_report, str_xp, err = await handle_experience(conn, cursor, quest, blue_team, blue_team_original)
            if str_xp:
                battle_report[-1] += str_xp

        return header, battle_report, achievement_message, progression_report, None 

    except Exception as err:
        print("Error on /functions_battle.battle_wrapper: \n", err)
        return None, None, err


def handle_blue_team(characters):
    try:
        blue_team = []
        index = dict_characters_select.index

        for character in characters:
            blue_team.append(
                Character.Character(
                    character[index["id"]], character[index["character_class"]], character[index["name"]], character[index["level"]], character[index["experience"]],
                    character[index["vitality"]], character[index["power"]], character[index["defense"]], character[index["critical"]],
                    character[index["speed"]], character[index["taunt"]], character[index["accuracy"]], character[index["dodge"]],
                    dict_actions.skills1[character[index["skill1"]]],dict_actions.skills2[character[index["skill2"]]], dict_emojis.characters[character[index["character_class"]]],dict_actions.characters_attack[character[index["character_class"]]]
                )
            )

        return blue_team, None

    except Exception as err:
        print("Error on /functions_battle.handle_blue_team:\n", err)
        return None, "Error handling blue team's creation."
    

def handle_red_team(quest):
    try:
        red_team = []

        monsters = dict_quests.quests_data[quest]["monsters"]
        for monster in monsters:
            red_team.append(Character.Character(**dict_monsters.monsters_attributes[monster]))

        achievement = dict_quests.quests_data[quest].get("achievement", None)

        return red_team, achievement, None

    except Exception as err:
        print("Error on /functions_battle.handle_red_team: \n", err)
        return None, None, "Error handling red team's creation."
    

def format_header(quest, blue_team, red_team):
    try:
        header = f"## {quest}\n# "
        for char in blue_team:
            header += f" {char.emoji} "
        header += "x"
        for char in red_team:
            header += f" {char.emoji} "

        return header, None

    except Exception as err:
        print("Error on /functions_battle.handle_red_team: \n", err)
        return None, "Error formatting header."
    

def resolve_combat(blue_team, red_team):
    try:
        # Combine all characters into a single list
        all_characters = blue_team + red_team

        blue_team_original = blue_team.copy()
        red_team_original = red_team.copy()

        turn_order = sorted(all_characters, key=lambda x: (-x.speed, random.random()))

        is_victory = False
        battle_report = []

        round_number = 1

        flag = True
        while flag:
            
            if round_number > 1:
                round_overview = "_ _\n>>> **Overview**\n"

                for char in blue_team:
                    round_overview += f":blue_square: {char.emoji} {char.name}'s HP: [{char.current_vitality}/{char.vitality}]\n"

                round_overview += "\n"

                for char in red_team:
                    round_overview += f":red_square: {char.emoji} {char.name}'s HP: [{char.current_vitality}/{char.vitality}]\n"

                battle_report.append(round_overview)

            battle_report.append(f"# Round {round_number}\n")

            for char in turn_order:

                turn_report = ""
                
                str, err = char.turn_wrapper(round_number, blue_team, red_team)

                if err:
                    return err

                turn_report += str

                str, err = remove_dead_character(blue_team, red_team, turn_order)

                if err:
                    return err

                turn_report += str

                battle_report.append(turn_report)
                
                if not blue_team or not red_team:
                    round_overview = "_ _\n>>> **Overview**\n"
                    if blue_team:
                        is_victory = True
                        for char in blue_team:
                            round_overview += f":blue_square: {char.emoji} {char.name}'s HP: [{char.current_vitality}/{char.vitality}]\n"
                    else:
                        for char in red_team:
                            round_overview += f":red_square: {char.emoji} {char.name}'s HP: [{char.current_vitality}/{char.vitality}]\n"

                    battle_report.append(round_overview)

                    flag = False
                    break

            round_number += 1


        battle_status = f"# Battle Status \n"
        for char in blue_team_original:
            battle_status += f":blue_square: {char.emoji} {char.name}\n"
            battle_status += f"Damage dealt: `{char.statistics['damage_dealt']}` |  Hits: `{char.statistics['number_hits']}` | Critical Hits: `{char.statistics['critical_hits']}` | Misses: `{char.statistics['missed_attacks']}`\n"
            battle_status += f"Damage taken: `{char.statistics['damage_taken']}` | Dodged attacks: `{char.statistics['dodged_attacks']}` | Healing done: `{char.statistics['health_healed']}`\n"

        battle_status += "\n"

        for char in red_team_original:
            battle_status += f":red_square: {char.emoji} {char.name}\n"
            battle_status += f"Damage dealt: `{char.statistics['damage_dealt']}` |  Hits: `{char.statistics['number_hits']}` | Critical Hits: `{char.statistics['critical_hits']}` | Misses: `{char.statistics['missed_attacks']}`\n"
            battle_status += f"Damage taken: `{char.statistics['damage_taken']}` | Dodged attacks: `{char.statistics['dodged_attacks']}` | Healing done: `{char.statistics['health_healed']}`\n"

        battle_report.append(battle_status)

        if is_victory:
            battle_report.append(f"## :blue_square: Victory!\n")
        else:
            battle_report.append(f"## :red_square: Defeat!")

        return battle_report, is_victory, None
    
    except Exception as err:
        print("Error on /functions_battle.resolve_combat", err)
        return None, None, "Error trying to resolve the combat."


def remove_dead_character(blue_team, red_team, turn_order):
    try:
        str = ""    
        dead_characters = []

        for char in turn_order:
            if char.is_dead:
                dead_characters.append(char)

        for char in dead_characters:
            if char in blue_team:
                blue_team.remove(char)
                turn_order.remove(char)
                str += f"{dict_colours.colours['blue']}{char.name}{dict_colours.colours['reset']} is dead.\n"
            else:
                red_team.remove(char)
                turn_order.remove(char)
                str += f"{dict_colours.colours['red']}{char.name}{dict_colours.colours['reset']} is dead.\n"

        str += "```"

        return str, None

    except Exception as err:
        print("Error on /function_battle.remove_dead_character:\n", err)
        return None, f"Error checking if {char.name} is dead."


def handle_quest_achievement(achievement):
    try:
        achievement_message = f"# :trophy: Achievement unlocked :trophy:\n"
        achievement_message += f"## {achievement['name']}\n"
        achievement_message += f"`{achievement['description']}`\n"
        achievement_message += f"{achievement['award']}\n"

        return achievement_message, None

    except Exception as err:
        print("Error on functions_battle.handle_quest_achievement:\n",err)
        return None, "Error handling the achievement message"
    

async def handle_experience(conn, cursor, quest, blue_team, blue_team_original):
    try:
        progression_report = []
        str_xp = ""

        quest_level = dict_quests.quests_data[quest]["level"]
        quest_xp = dict_quests.quests_data[quest]["xp"]

        team_level = 0
        for char in blue_team_original:
            team_level += char.level

        level_modifier = (quest_level+10)/(team_level+10)
        calculated_xp = quest_xp * level_modifier

        for character in blue_team_original:
            current_xp = character.xp
            required_xp = character.required_xp()

            if character.level > (quest_level*2):
                gained_xp = int(calculated_xp/2)
            else:
                gained_xp = int(calculated_xp)

            if character not in blue_team:
                gained_xp = int(gained_xp/2)

            updated_xp = gained_xp + current_xp

            if (updated_xp >= required_xp) and character.level < 5:
                level_report, err = await functions_sql.update_character_level(conn,cursor,character,(character.level+1))

                if err:
                    return None, None, err

                progression_report.append(level_report)

                updated_xp = updated_xp - required_xp

            err = await functions_sql.update_character_xp(conn,cursor,character,updated_xp)

            if err:
                return None, None, err

            str_xp += (f"## {character.emoji} {character.name} gained {gained_xp} XP.\n")

        return progression_report, str_xp, err


    except Exception as err:
        print("Error on functions_battle.handle_experience:\n",err)
        return None, "Error handling the experience gain"
    


