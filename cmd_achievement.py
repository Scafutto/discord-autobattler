import functions_sql

def format_achievement_show(achievements):
    try:
        achievements_name = []

        if achievements:
            for achievement in achievements:
                achievements_name.append(achievement[1])

        reply_message = f"# Achievements\n"
        reply_message += f"{'### :white_check_mark: First Victory' if 'First Victory' in achievements_name else '### :x: First Victory'}\n"
        reply_message += f"{'Win your first combat'}\n\n"
        reply_message += f"{'### :white_check_mark: Rat Trap' if 'Rat Trap' in achievements_name else '### :x: Rat Trap'}\n"
        reply_message += f"{'Kill the Ratgabash the Wicked for the first time'}\n\n"
        reply_message += f"{'### :white_check_mark: Rising Star' if 'Rising Star' in achievements_name else '### :x: Rising Star'}\n"
        reply_message += f"{'Complete Act I'}"

        return reply_message, None
    
    except Exception as err:
        return None, err

async def show(
    ctx,
    cursor,
    user_id,
    ):
    try:
        achievements, err = await functions_sql.select_achievements(cursor, user_id)
        if err:
            return err
        
        reply_message, err = format_achievement_show(achievements)
        if err:
            return err
        
        await ctx.send(reply_message)

    except Exception as e:
        print(e)
        await ctx.send("An error occured, please contact an admin")
