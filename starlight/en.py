import csvloader
import functools
import os
import enums
from .formulas import *

# skill describer

SKILL_DESCRIPTIONS = {
    1: """all Perfect notes will receive a <span class="let">{0}</span>% score bonus""",
    2: """all Great and Perfect notes will receive a <span class="let">{0}</span>% score bonus""",
    4: """you will gain an extra <span class="let">{0}</span>% combo bonus""",
    5: """all Great notes will become Perfect notes""",
    6: """all Great and Nice notes will become Perfect notes""",
    7: """all Great, Nice, and Bad notes will become Perfect notes""",
    9: """Nice notes will not break combo""",
    12: """you will not lose health""",
    17: """all Perfect notes will restore <span class="let">{0}</span> health""" }


def describe_skill_html(skill):
    fire_interval = skill.condition
    effect_val = skill.value
    # TODO symbols
    if skill.skill_type in [1, 2, 4]:
        effect_val -= 100

    effect_clause = SKILL_DESCRIPTIONS.get(
        skill.skill_type, "").format(effect_val)
    interval_clause = """Every <span class="let">{0}</span> seconds:""".format(
        fire_interval)
    probability_clause = """there is a <span class="var">{0}</span>% chance that""".format(
        skill_chance(skill.probability_type))
    length_clause = """for <span class="var">{0}</span> seconds.""".format(
        skill_dur(skill.available_time_type))

    return " ".join((interval_clause, probability_clause, effect_clause, length_clause))


def describe_lead_skill_html(skill):
    assert skill.up_type == 1 and skill.type == 20

    target_attr = enums.lskill_target(skill.target_attribute)
    target_param = enums.lskill_param(skill.target_param)

    built = """Raises {0} of {1} members by <span class="let">{2}</span>%.""".format(
        target_param, target_attr, skill.up_value)
    return built