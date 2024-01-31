import functions_sql, functions_battle
import dict_quests

async def act1(ctx, conn, cursor, user_id, quest):
    try:
        completed_quests, err = await functions_sql.select_completed_quests(cursor, user_id)

        if err:
            return err
        
        completed_quests_names = []

        if completed_quests:
            completed_quests_names = [name[1] for name in completed_quests]

        is_quest_complete = quest in completed_quests_names

        if quest == "This ratto is fatto":
            pass
        elif not is_quest_complete:
            previous_quest = None

            for current_quest in dict_quests.quests_data:
                if current_quest == quest:
                    break
                previous_quest = current_quest

            if previous_quest not in completed_quests_names:
                await ctx.send(f"You must complete `{previous_quest}` before launching `{quest}`")
                return None

        header, battle_report, achievement_message, progression_report, err = await functions_battle.battle_wrapper(ctx, conn, cursor, user_id, quest, is_quest_complete)

        if err:
            return err

        await ctx.send(header)

        thread = await ctx.channel.create_thread(name="Battle Report", auto_archive_duration=60)

        for message in battle_report:
            await thread.send(message)

        if achievement_message:
            await ctx.send(achievement_message)

        if progression_report:
            for message in progression_report:
                await ctx.send(message)

    except Exception as err:
        print("Error on /cmd_act1.act1:", err)
        return "General error handling act1 command, please contact an admin"