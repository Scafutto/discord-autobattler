level_required_xp = {
    1: 5,
    2: 10,
    3: 25,
    4: 50,
    5: 75
}

general = {
    2: {
        "pool": {
            1: [7,3,1],
            2: [5,3,3],
            3: [4,4,3],
        },
        "skill1": True,
        "skill2": False,
    },
    3: {
        "pool": {
            1: [7,3,1],
            2: [5,3,3],
            3: [4,4,3],
        },
        "skill1": False,
        "skill2": False,
    },
    4: {
        "pool": {
            1: [8,3,1],
            2: [6,3,3],
            3: [4,4,4],
        },
        "skill1": False,
        "skill2": True,
    },
    5: {
        "pool": {
            1: [8,3,1],
            2: [6,3,3],
            3: [4,4,4],
        },
        "skill1": False,
        "skill2": False,
    },
}

quill = {
    "primary": "power",
    1: False,
    2: False,
    3: {
        1: {
            "critical": 5
        },
        2: {
            "dodge": 5,
            "accuracy": 5
        },
        3: {
            "speed": 2,
            "critical": 2,
            "dodge": 2,
            "accuracy": 2
        },
    },
    4: False,
    5: {
        1: {
            "critical": 10,
            "power": 20,
        },
        2: {
            "dodge": 20,
            "speed": 5,
            "vitality": 40
        },
        3: {
            "critical": 5,
            "accuracy": 20,
            "power": 10
        },
    },
    "skill1": {
        "Common": ["Volley"], # 70%
        "Rare": ["Headshot"], # 25%
        "Epic": ["Headshot"], # 5%
    },
    "skill2": {
        "Common": ["Rain of Arrows"], # 70%
        "Rare": ["Rain of Arrows"], # 25%
        "Epic": ["Rain of Arrows"], # 5%
    }
}

grizzor = {
    "primary": "vitality",
    1: False,
    2: False,
    3: {
        1: {
            "taunt": 5,
        },
        2: {
            "defense": 10,
            "vitality": 40
        },
        3: {
            "taunt": 2,
            "vitality": 20,
            "dodge": 2,
            "accuracy": 2,
        },
    },
    4: False,
    5: {
        1: {
            "taunt": 5,
            "power": 10,
            "critical": 5,
        },
        2: {
            "dodge": 3,
            "taunt": 3,
            "defense": 10,
            "vitality": 20,
        },
        3: {
            "vitality": 100,
        },
    },
    "skill1": {
        "Common": ["Swing"], # 70%
        "Rare": ["Cleave"], # 25%
        "Epic": ["Berserk"], # 5%
    },
        "skill2": {
        "Common": ["Heroic Strike"], # 70%
        "Rare": ["Heroic Strike"], # 25%
        "Epic": ["Heroic Strike"], # 5%
    }
}

slink = {
    "primary": "power",
    1: False,
    2: False,
    3: {
        1: {
            "critical": 7
        },
        2: {
            "power": 20,
            "speed": 5
        },
        3: {
            "dodge": 5,
            "accuracy": 5
        },
    },
    4: False,
    5: {
        1: {
            "critical": 15,
        },
        2: {
            "dodge": 10,
            "accuracy": 10,
            "speed": 5
        },
        3: {
            "dodge": 5,
            "accuracy": 5,
            "power": 30
        },
    },
    "skill1": {
        "Common": ["Backstab"], # 70%
        "Rare": ["Shadowstep"], # 25%
        "Epic": ["Shadowstep"], # 5%
    },
        "skill2": {
        "Common": ["Cutthroat"], # 70%
        "Rare": ["Cutthroat"], # 25%
        "Epic": ["Cutthroat"], # 5%
    }
}

whizz = {
    "primary": "power",
    1: False,
    2: False,
    3: {
        1: {
            "power": 30
        },
        2: {
            "speed": 2,
            "power": 15,
            "critical": 5,
        },
        3: {
            "power": 20,
            "dodge": 5,
            "accuracy": 5
        },
    },
    4: False,
    5: {
        1: {
            "critical": 10,
            "power": 20,
        },
        2: {
            "accuracy": 10,
            "dodge": 5,
            "critical": 5,
        },
        3: {
            "power": 50,
        },
    },
    "skill1": {
        "Common": ["Fireball"], # 70%
        "Rare": ["Lightning Bolt"], # 25%
        "Epic": ["Lightning Bolt"], # 5%
    },
    "skill2": {
        "Common": ["Finger of Death"], # 70%
        "Rare": ["Finger of Death"], # 25%
        "Epic": ["Finger of Death"], # 5%
    }
}

pigwell = {
    "primary": "power",
    1: False,
    2: False,
    3: {
        1: {
            "power": 30
        },
        2: {
            "speed": 2,
            "power": 15,
            "dodge": 5,
        },
        3: {
            "speed": 5,
        },
    },
    4: False,
    5: {
        1: {
            "speed": 10,
            "power": 20,
        },
        2: {
            "dodge": 5,
            "critical": 5,
            "defense": 20
        },
        3: {
            "power": 50,
        },
    },
    "skill1": {
        "Common": ["Greasy Heal"], # 70%
        "Rare": ["Greasy Heal"], # 25%
        "Epic": ["Greasy Heal"], # 5%
    },
    "skill2": {
        "Common": ["Sanctuary"], # 70%
        "Rare": ["Sanctuary"], # 25%
        "Epic": ["Sanctuary"], # 5%
    }
}










