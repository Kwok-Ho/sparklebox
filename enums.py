def enum(kv):
    i = iter(kv)
    dic = dict(zip(i, i))

    def f(key):
        return dic.get(key, "<missing string: {0}>".format(key))
    return f

rarity = enum([
    1, "Normal",
    2, "Normal+",
    3, "Rare",
    4, "Rare+",
    5, "SR",
    6, "SR+",
    7, "SSR",
    8, "SSR+",
])

attribute = enum([
    1, "Cute",
    2, "Cool",
    3, "Passion",
    4, "Office",
])

skill_type = enum([
    1, "Perfect Score Bonus",
    2, "Score Bonus",
    4, "Combo Bonus",
    5, "Lesser Perfect Lock",
    6, "Greater Perfect Lock",
    7, "Extreme Perfect Lock",
    9, "Combo Support",
    12, "Life Support",
    17, "Healer",
])

skill_probability = enum([
    2, "small",
    3, "fair",
    4, "high",
])

skill_length_type = enum([
    3, "short",
    4, "medium",
    5, "long",
])

lskill_target = enum([
    1, "all Cute",
    2, "all Cool",
    3, "all Passion",
    4, "all",
])

lskill_effective_target = enum([
    1, "ca_cute",
    2, "ca_cool",
    3, "ca_passion",
    4, "ca_all",
])

lskill_param = enum([
    1, "the Vocal appeal",
    2, "the Visual appeal",
    3, "the Dance appeal",
    4, "all appeals",
    5, "the life",
    6, "the skill probability",
])

lskill_effective_param = enum([
    1, "ce_vocal",
    2, "ce_visual",
    3, "ce_dance",
    4, "ce_anyappeal",
    5, "ce_life",
    6, "ce_skill",
])

skill_class = enum([
    1, "s_scorebonus",
    17, "s_heal",
    4, "s_combobonus",
    5, "s_pl",
    9, "s_cprot",
    7, "s_pl",
    2, "s_scorebonus",
    6, "s_pl",
    12, "s_life",
])

# TODO need enum defs for
# constellation
# blood_type
# hand
# personality
# home_town