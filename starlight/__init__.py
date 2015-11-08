import re
from collections import defaultdict

from .dataloader import *
from . import en

# chains
def discover_evolutionary_chains(card_list):
    chains = bucketize(lambda x: x.series_id, [
                       card_list[key] for key in card_list])

    chain_by_card = {}
    for chain in chains:
        for card in chains[chain]:
            chain_by_card[card.id] = chain
        chains[chain] = order_chain(chains[chain])

    return chains, chain_by_card


def bucketize(key, a_list):
    ret = defaultdict(lambda: [])

    for item in a_list:
        ret[key(item)].append(item)

    return ret


def order_chain(chain):
    new_chain = [next(filter(lambda x: x.evolution_id == 0, chain))]
    chain.remove(new_chain[0])

    while chain:
        for card in chain:
            if card.evolution_id == new_chain[-1].id:
                break
        else:
            raise ValueError(
                "Invalid chain group: could not find a card with evolution_id of {0}".format(new_chain[-1].id))
        chain.remove(card)
        new_chain.append(card)

    new_chain.reverse()
    return new_chain


def pick_random_card_of_chara(self, chara):
    return random.choice(list(filter(lambda x: card_db[x].chara_id == chara, card_db)))

# needed arks
TITLE_ONLY_REGEX = r"^［(.+)］"
NAME_ONLY_REGEX = r"^(?:［.+］)?(.+)$"

# name_table=ntl_object,
# chara_db=chara_db,
# card_db=card_db,
# card_db_by_id=cards_by_id,
#
# evolve_chains=evolutionary_chains,
# card_evolve_chain=chains_by_card,

names = cached_keyed_db(private_data_path("names.csv"))
skills = csvloader.load_keyed_db_file(ark_data_path("skill_data.txt"))
lead_skills = csvloader.load_keyed_db_file(ark_data_path("leader_skill_data.txt"))
rarity_dep = csvloader.load_keyed_db_file(ark_data_path("card_rarity.txt"))

chara_db = csvloader.load_keyed_db_file(ark_data_path("chara_data.txt"),
    kanji_spaced=lambda obj: names.get(obj.chara_id).kanji_spaced,
    kana_spaced=lambda obj: names.get(obj.chara_id).kana_spaced,
    conventional=lambda obj: names.get(obj.chara_id).conventional)
card_db = csvloader.load_keyed_db_file(ark_data_path("card_data.txt"),
    chara=lambda obj: chara_db.get(obj.chara_id),
    has_spread=lambda obj: obj.rarity > 4,
    name_only=lambda obj: re.match(NAME_ONLY_REGEX, obj.name).group(1),
    title=lambda obj: re.match(TITLE_ONLY_REGEX, obj.name).group(1) if obj.title_flag else None,
    skill=lambda obj: skills.get(obj.skill_id),
    lead_skill=lambda obj: lead_skills.get(obj.leader_skill_id),
    rarity_dep=lambda obj: rarity_dep.get(obj.rarity))
evolutionary_chains, chains_by_card = discover_evolutionary_chains(card_db)