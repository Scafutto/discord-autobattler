import random
from dict_colours import colours
from dict_progression import level_required_xp


class Character:
    def __init__(self, id, character_class, name, level, experience, vitality, power, defense, critical, speed, taunt, accuracy, dodge, skill1, skill2, emoji, attack):
        self.id = id
        self.character_class = character_class
        self.name = name
        self.level = level
        self.xp = experience
        self.vitality = vitality
        self.current_vitality = vitality
        self.power = power
        self.defense = defense
        self.critical = critical
        self.speed = speed
        self.taunt = taunt
        self.accuracy = accuracy
        self.dodge = dodge
        self.is_dead = False
        self.skill1 = skill1
        self.skill2 = skill2
        self.emoji = emoji
        self.attack = attack
        self.statistics = {
            "damage_dealt": 0,
            "damage_taken": 0,
            "number_hits": 0,
            "missed_attacks": 0,
            "dodged_attacks": 0,
            "critical_hits": 0,
            "health_healed": 0,
            "health_received": 0,
        }
        self.conditions = {
            "poison": 0,
            "bleed": [],
            "burn": [],
            "shock": False,
            "protection": False,
            }
        self.temporary_attributes = {
            "vitality": 0,
            "power": 0,
            "defense": 0,
            "critical": 0,
            "speed": 0,
            "taunt": 0,
            "accuracy": 0,
            "dodge": 0
        }
        
        
    def turn_wrapper(self, round_number, blue_team, red_team):
        
        conditions_str, err = self.resolve_conditions(self in blue_team)
        
        if err:
            return None, err
        
        if self.is_dead:
            turn_report =  f"# {':blue_square:' if self in blue_team else ':red_square:'} {self.emoji} {self.name} faints.\n```ansi\n"
            turn_report += conditions_str
            return turn_report, None
        
        action, err = self.define_action(round_number)

        if err:
            return None, err

        turn_report = f"# {':blue_square:' if self in blue_team else ':red_square:'} {self.emoji} {self.name} uses {action['name']}\n```ansi\n"

        turn_report += conditions_str

        targets, err = self.define_targets(blue_team, red_team, action)

        if err:
            return None, err

        match action["type"]:
            case "attack":
    
                if action.get("special"):                      
                    special_value = action.get("special")
                    match special_value:
                        case "chain":
                            str, err = self.resolve_chain_attack(action, targets, True if (self in blue_team) else False)
                        case _:
                            str, err = self.resolve_attack(action, targets, True if (self in blue_team) else False)
                else:
                    str, err = self.resolve_attack(action, targets, True if (self in blue_team) else False)

                if err:
                    return None, err

                turn_report += str

            case "heal":
                str, err = self.resolve_heal(
                    action, targets, True if (self in blue_team) else False)

                if err:
                    return None, err

                turn_report += str

        return turn_report, None

    def define_action(self, round_number):
        try:
            if round_number % 3 == 0 and self.skill2:
                return self.skill2, None
            if round_number % 2 == 0 and self.skill1:
                return self.skill1, None
            else:
                return self.attack, None
        except Exception as err:
            print("Error on /Character.define_action: \n", err)
            return None, f"Error trying to resolve {self.name}'s turn"

    def define_targets(self, blue_team, red_team, action):
        try:
            targets = []
            target_team = None

            # Define which team is the target
            if self in blue_team:
                target_team = red_team.copy() if action.get(
                    'is_target_enemy') else blue_team.copy()
            else:
                target_team = blue_team.copy() if action.get(
                    'is_target_enemy') else red_team.copy()

            # Define which members of the team are the targets
            if action['number_target'] >= len(target_team):
                targets = target_team
            else:
                if action['type'] == "attack":
                    for _ in range(action['number_target']):
                        taunt_sum = sum(enemy.taunt for enemy in target_team)
                        # Randomize a number to decide the target based on taunt values
                        random_num = random.uniform(0, taunt_sum)

                        # Loop through the enemy team's characters to select the target based on taunt values
                        cumulative_taunt = 0
                        for target in target_team:
                            cumulative_taunt += target.taunt
                            if cumulative_taunt >= random_num:
                                targets.append(target)
                                target_team.remove(target)
                                break  # Stop after selecting the target

                elif action['type'] == "heal":
                    target_team.sort(
                        key=lambda x: x.current_vitality / x.vitality)
                    targets = target_team[:action['number_target']]

            return targets, None

        except Exception as err:
            print("Error on /Character.define_targets: \n", err)
            return None, f"Error trying to resolve {self.name}'s targets"

    def resolve_attack(self, action, targets, is_blue_team):
        try:
            str = ""
            for target in targets:
                post_attack_str = ""
                is_hit, err = self.resolve_hit_chance(target, action)

                if err:
                    return None, err

                if is_hit:
                    
                    if target.conditions["protection"] == True:
                        str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name} {colours['reset']}{action['text']} {colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']} with {action['name']} but {colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']} was Protected and takes no damage. {colours['red'] if is_blue_team else colours['blue']}{target.name}'s HP: [{target.current_vitality}/{target.vitality}]{colours['reset']}.\n"
                        target.conditions["protection"] = False
                        continue
                    
                    
                    guaranteed_critical = False
                    if target.conditions["shock"] == True:
                        guaranteed_critical = True
                        target.conditions["shock"] = False
                        post_attack_str += f"{colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']} is no longer shocked.\n"
                    
                    damage, is_critical, err = self.calculate_damage(action, guaranteed_critical)

                    if err:
                        return None, err

                    final_damage, err = target.receive_damage(damage, self)

                    if err:
                        return None, err

                    self.statistics["damage_dealt"] += final_damage
                    self.statistics["number_hits"] += 1

                    str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name} {colours['reset']}{action['text']} {colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']} with {action['name']} for {final_damage}{'[!]' if is_critical else ''} HP. {colours['red'] if is_blue_team else colours['blue']}{target.name}'s HP: [{target.current_vitality}/{target.vitality}]{colours['reset']}.\n"
                    str += post_attack_str

                    if action.get("apply_conditions"):
                        applied_conditions = action.get("apply_conditions", {})
                        for condition_name, condition_data in applied_conditions.items():
                            if condition_data.get('apply_to') == 'target':
                                conditions_str, err = target.handle_condition(condition_name, condition_data, is_blue_team)
                            if condition_data.get('apply_to') == 'self':
                                conditions_str, err = self.handle_condition(condition_name, condition_data, is_blue_team)

                            if err:
                                return None, err

                            str += conditions_str                        

                else:
                    target.statistics["dodged_attacks"] += 1
                    self.statistics["missed_attacks"] += 1

                    str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name}{colours['reset']} missed the {action['type']} on {colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']}. {colours['red'] if is_blue_team else colours['blue']}{target.name}'s HP: [{target.current_vitality}/{target.vitality}]{colours['reset']}.\n"

            return str, None

        except Exception as err:
            print("Error on /Character.resolve_attack: \n", err)
            return None, f"Error trying to resolve {self.name}'s attack"

    def resolve_chain_attack(self, action, targets, is_blue_team):
        try:
            str = ""
            for target in targets:
                consecutive_hits = 0
                post_attack_str = ""
                while True:
                    is_hit, err = self.resolve_hit_chance(target, action)

                    if err:
                        return None, err

                    if is_hit:
                        consecutive_hits += 1
                        self.temporary_attributes['accuracy'] -= 15

                        if target.conditions["protection"] == True:
                            str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name} {colours['reset']}{action['text']} {colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']} with {action['name']} but {colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']} was Protected and takes no damage. {colours['red'] if is_blue_team else colours['blue']}{target.name}'s HP: [{target.current_vitality}/{target.vitality}]{colours['reset']}.\n"
                            target.conditions["protection"] = False
                            continue

                        guaranteed_critical = False
                        if target.conditions["shock"] == True:
                            guaranteed_critical = True
                            post_attack_str += f"{colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']} is no longer shocked.\n"

                        damage, is_critical, err = self.calculate_damage(action, guaranteed_critical)

                        if err:
                            return None, err

                        final_damage, err = target.receive_damage(damage, self)

                        if err:
                            return None, err

                        self.statistics["damage_dealt"] += final_damage
                        self.statistics["number_hits"] += 1

                        str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name} {colours['reset']}{action['text']} {colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']} with {action['name']} for {final_damage}{'[!]' if is_critical else ''} HP. {colours['red'] if is_blue_team else colours['blue']}{target.name}'s HP: [{target.current_vitality}/{target.vitality}]{colours['reset']}.\n"
                        str += post_attack_str

                        if action.get("apply_conditions"):
                            applied_conditions = action.get("apply_conditions", {})
                            for condition_name, condition_data in applied_conditions.items():
                                if condition_data.get('apply_to') == 'target':
                                    conditions_str, err = target.handle_condition(condition_name, condition_data, is_blue_team)
                                if condition_data.get('apply_to') == 'self':
                                    conditions_str, err = self.handle_condition(condition_name, condition_data, is_blue_team)

                                if err:
                                    return None, err

                                str += conditions_str

                    else:
                        self.temporary_attributes['accuracy'] += (15*consecutive_hits)
                        target.statistics["dodged_attacks"] += 1
                        self.statistics["missed_attacks"] += 1

                        str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name}{colours['reset']} missed the {action['type']} on {colours['red'] if is_blue_team else colours['blue']}{target.name}{colours['reset']}. {colours['red'] if is_blue_team else colours['blue']}{target.name}'s HP: [{target.current_vitality}/{target.vitality}]{colours['reset']}.\n"

                        break

            return str, None

        except Exception as err:
            print("Error on /Character.resolve_attack: \n", err)
            return None, f"Error trying to resolve {self.name}'s attack"

    def resolve_hit_chance(self, target, action):
        try:
            hit_chance = self.accuracy + self.temporary_attributes['accuracy'] + action['accuracy_modifier'] - target.dodge
            is_hit = random.random() < (hit_chance / 100)
            return is_hit, None

        except Exception as err:
            print("Error on /Character.resolve_hit_chance: \n", err)
            return None, f"Error trying to resolve {self.name} hit chance against {target.name}"

    def calculate_damage(self, action, guaranteed_critical = False):
        try:
            damage = action['base_value'] * random.uniform(0.8, 1.2)
            is_critical = False
            if guaranteed_critical or random.random() < ((self.critical+action['critical_modifier'])/100):
                damage *= action['critical_multiplier']
                is_critical = True
                self.statistics["critical_hits"] += 1
            return int(damage), is_critical, None

        except Exception as err:
            print("Error on /Character.calculate_damage: \n", err)
            return None, None, f"Error trying to calculate damage for {self.name}."

    def receive_damage(self, damage, attacker):
        try:
            power_difference = attacker.power - self.defense

            if power_difference > 0:
                damage_modifier = 1 + (0.02 * power_difference)
            else:
                damage_modifier = 1 / (1 + (0.02 * abs(power_difference)))

            final_damage = max(int(damage * damage_modifier), 1)

            self.statistics["damage_taken"] += final_damage

            self.current_vitality -= final_damage

            if self.current_vitality <= 0:
                self.current_vitality = 0
                self.is_dead = True

            return int(final_damage), None

        except Exception as err:
                print("Error on /Character.receive_damage: \n", err)
                return None, f"Error trying to apply the damage to {self.name}."

    def resolve_heal(self, action, targets, is_blue_team):
        try:
            str = ""
            for target in targets:
                
                # Conditions before healing

                if target.conditions['poison']:
                    str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name}{colours['reset']} tried to heal {colours['blue'] if is_blue_team else colours['red']}{target.name}{colours['reset']} with {action['name']} but the Poison negated it. {colours['blue'] if is_blue_team else colours['red']}{target.name}'s HP: [{target.current_vitality}/{target.vitality}]{colours['reset']}.\n"
                    str += f"{colours['blue'] if is_blue_team else colours['red']}{target.name}{colours['reset']} is no longer Poisoned.\n"
                    
                    target.conditions['poison'] = 0
                    
                    continue

                heal, is_critical, err = self.calculate_heal(action)

                if err:
                    return None, err

                final_heal, err = target.receive_heal(heal, self)

                if err:
                    return err
                
                self.statistics["health_healed"] += final_heal

                str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name} {colours['reset']}{action['text']} {colours['blue'] if is_blue_team else colours['red']}{target.name}{colours['reset']} with {action['name']} for {final_heal}{'[!]' if is_critical else ''} HP. {colours['blue'] if is_blue_team else colours['red']}{target.name}'s HP: [{target.current_vitality}/{target.vitality}]{colours['reset']}.\n"


                # Conditions after healing
                    
                if target.conditions['bleed']:
                    str += f"{colours['blue'] if is_blue_team else colours['red']}{target.name}{colours['reset']} is no longer Bleeding.\n"
                    target.conditions["bleed"] = []

                if action.get("apply_conditions"):
                    applied_conditions = action.get("apply_conditions", {})

                    for condition_name, condition_data in applied_conditions.items():
                        if condition_data.get('apply_to') == 'target':
                            conditions_str, err = target.handle_condition(condition_name, condition_data, not is_blue_team)
                        if condition_data.get('apply_to') == 'self':
                            conditions_str, err = self.handle_condition(condition_name, condition_data, not is_blue_team)

                        if err:
                            return None, err

                        str += conditions_str


            return str, None

        except Exception as err:
            print("Error on /Character.resolve_heal: \n", err)
            return None, f"Error trying to resolve {self.name}'s heal"

    def calculate_heal(self, action):
        try:
            heal = action['base_value'] * random.uniform(0.8, 1.2)
            is_critical = False

            if random.random() < ((self.critical+action['critical_modifier'])/100):
                heal *= action['critical_multiplier']
                is_critical = True

            return int(heal), is_critical, None

        except Exception as err:
            print("Error on /Character.calculate_heal: \n", err)
            return None, None, f"Error trying to calculate heal from {self.name}."

    def receive_heal(self, heal, healer):
        try: 
            final_heal = int(heal+(healer.power/10))

            self.statistics["health_received"] += final_heal

            self.current_vitality += final_heal  # Update current_vitality

            if self.current_vitality > self.vitality:
                self.current_vitality = self.vitality

            return int(final_heal), None
    
        except Exception as err:
            print("Error on /Character.receive_heal: \n", err)
            return None, f"Error trying to calculate heal for {self.name}."

    def required_xp(self):
        return level_required_xp[self.level]

    def handle_condition(self, condition_name, condition_data, is_blue_team):
        try:
            match condition_name:
                case "poison":
                    value = condition_data.get('value')
                    self.conditions["poison"] += value
                    
                    str = f"{colours['red'] if is_blue_team else colours['blue']}{self.name}{colours['reset']} is now Poisoned ({value}).\n"

                    return str, None
                
                case "protection":
                    self.conditions["protection"] = condition_data.get('value')
                    
                    str = f"{colours['red'] if is_blue_team else colours['blue']}{self.name}{colours['reset']} is now Protected.\n"
                    
                    return str, None
                   
                case "bleed":
                    array_values = condition_data.get('value')
                    self.conditions["bleed"].append(array_values) 
                    
                    str = f"{colours['red'] if is_blue_team else colours['blue']}{self.name}{colours['reset']} is now Bleeding ({array_values[0]}) for {array_values[1]} {'turns' if (array_values[1] > 1) else 'turn'}.\n"
                    
                    return str, None
                
                case "burn":
                    array_values = condition_data.get('value')
                    self.conditions["burn"].append(array_values) 
                    
                    str = f"{colours['red'] if is_blue_team else colours['blue']}{self.name}{colours['reset']} is now Burning ({array_values[0]}) for {array_values[1]} {'turns' if (array_values[1] > 1) else 'turn'}.\n"
                    
                    return str, None
                
                case "shock":
                    self.conditions["shock"] = condition_data.get('value')
                    
                    str = f"{colours['red'] if is_blue_team else colours['blue']}{self.name}{colours['reset']} is now Shocked.\n"
                    
                    return str, None
                
                case _:
                    return None, f"Condition not found: {condition_name}"
                
        except Exception as err:
            print("Error on /Character.handle_condition:\n", err)
            return None, f"Error handling conditions for {self.name}"

    def resolve_conditions(self, is_blue_team):
        try:
            str = ""
            end_condition_str = ""
            
            if self.conditions.get("poison"):
                poison_value = self.conditions["poison"]
                
                self.reduce_vitality(poison_value)
                
                str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name}{colours['reset']} took {poison_value} damage from poison. {colours['blue'] if is_blue_team else colours['red']}{self.name}'s HP: [{self.current_vitality}/{self.vitality}]{colours['reset']}.\n"

                self.conditions["poison"] -= self.level
                
                if self.conditions['poison'] <= 0:
                    self.conditions['poison'] = 0
                    end_condition_str += f"The effects of poison are over.\n"

            if self.conditions.get("bleed"):

                bleed_value = 0 

                for bleed_effect in self.conditions["bleed"]:
                    value, duration = bleed_effect

                    bleed_value += value
                    duration -= 1

                    if duration <= 0:
                        self.conditions["bleed"].remove(bleed_effect)
                        end_condition_str += f"The effects of bleed [{value}] are over.\n"

                    else:
                        bleed_effect[1] = duration

                self.reduce_vitality(bleed_value)

                str += f"{colours['blue'] if is_blue_team else colours['red']}{self.name}{colours['reset']} took {bleed_value} damage from bleed. {colours['blue'] if is_blue_team else colours['red']}{self.name}'s HP: [{self.current_vitality}/{self.vitality}]{colours['reset']}.\n"
            
            str += end_condition_str
            
            return str, None

                
        except Exception as err:
            print("Error on /Character.resolve_conditions:\n", err)
            return None, f"Error resolving conditions for {self.name}"

    def reduce_vitality(self, damage):
        self.statistics["damage_taken"] += damage

        self.current_vitality -= damage

        if self.current_vitality <= 0:
            self.current_vitality = 0
            self.is_dead = True

        return None
    


