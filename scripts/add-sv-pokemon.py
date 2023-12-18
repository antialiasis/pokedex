# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import json
import re

# Usage: pipe into psql with python add-sv-pokemon.py | psql -U tcod pokedex

GROWTH_RATES = {
    'Slow': 'slow',
    'MediumFast': 'medium',
    'Fast': 'fast',
    'MediumSlow': 'medium-slow',
    'Erratic': 'slow-then-very-fast',
    'Fluctuating': 'fast-then-very-slow',
}

# Pokémon that have forms, but they're not counted as separate Pokemon objects in the database (only PokemonForms), as they have identical stats etc. Must be updated to include all Pokémon in the new Pokédex.
PSEUDOFORMS = [
    421,
    422,
    423,
    493,
    585,
    586,
    649,
    664,
    665,
    666,
    669,
    670,
    671,
    716,
    773,
    854,
    855
]

# Pokémon with a default form that is 'anonymous', i.e. has the same identifier as the species in the pokemon table, rather than the same identifier as the form.
ANON_DEFAULT_FORM = [
    720
]

# Special form names that we can't construct with a simple rule of capitalizing the identifier.
SPECIAL_FORM_NAMES = {
    'maushold-family-of-four': "Family of Four",
    'maushold-family-of-three': "Family of Three",
}

DEX_REGEX = re.compile(r'^(\d+) - \[(\d+)\]')

def make_identifier(name):
    """Make a string safe to use as an identifier.

    Valid characters are lowercase alphanumerics and "-". This function may
    raise ValueError if it can't come up with a suitable identifier.

    This function is useful for scripts which add things with names.
    """
    if isinstance(name, bytes):
        identifier = name.decode('utf-8')
    else:
        identifier = name
    identifier = identifier.lower()
    identifier = identifier.replace(u'+', u' plus ')
    identifier = re.sub(u'[ _–]+', u'-', identifier)
    identifier = re.sub(u"['./;’(),:]", u'', identifier)
    identifier = identifier.replace(u'é', u'e')
    identifier = identifier.replace(u'\u2640', '-f')
    identifier = identifier.replace(u'\u2642', '-m')

    if identifier.startswith('route-'):
        identifier = 'galar-' + identifier

    if not identifier.replace(u"-", u"").isalnum():
        raise ValueError(identifier)
    return identifier

data = json.load(open('C:\\Users\\antialiasis\\Documents\\TCoD\\Flask\\tcod\\tcod\\data-files\\sv-pokemon-indigo-disk.json'))
forms_data = json.load(open(r'C:\\Users\\antialiasis\\Documents\\TCoD\\Flask\\tcod\\scripts\\data-files\\forms.json'))

# Compensate for original veekun data including all the pseudoforms for Minior.
forms_data['774'] = ["red-meteor", "orange-meteor", "yellow-meteor", "green-meteor", "blue-meteor", "indigo-meteor", "violet-meteor", "red-core", "orange-core", "yellow-core", "green-core", "blue-core", "indigo-core", "violet-core"]

# This was used because the original S/V data rip didn't use the proper National Pokédex identifiers for the Paldean Pokémon.
# natdex_map = {}
# with open('C:\\Users\\antialiasis\\Documents\\TCoD\\Flask\\tcod\\scripts\\data-files\\sv-pokemon.txt') as natdex_data:
#     for line in natdex_data.readlines():
#         split = line.split(";")
#         try:
#             natdex_num = int(split[0])
#         except ValueError:
#             break
#         natdex_map[split[1]] = natdex_num

hisui = "Hisui"
hisui_ident = make_identifier(hisui)

region = "Paldea"
region_ident = make_identifier(region)

kitakami = "Kitakami"
kitakami_ident = make_identifier(kitakami)

blueberry = "Blueberry Academy"
blueberry_ident = make_identifier(blueberry)
# first_form_id is the first internal ID that's a form, separating the default form identifiers from the form ones.
# Usually you'll get National Pokédex identifiers for the defaults, then a gap, and then the form identifiers.
first_form_id = 1034

print("BEGIN;")
print("INSERT INTO regions (id, identifier) VALUES (9, '%s') ON CONFLICT DO NOTHING;" % hisui_ident)
print("INSERT INTO region_names (region_id, local_language_id, name) SELECT id, 9, '%s' FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (hisui, hisui_ident))
print("INSERT INTO regions (id, identifier) VALUES (10, '%s') ON CONFLICT DO NOTHING;" % region_ident)
print("INSERT INTO region_names (region_id, local_language_id, name) SELECT id, 9, '%s' FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (region, region_ident))
print("INSERT INTO regions (id, identifier) VALUES (11, '%s') ON CONFLICT DO NOTHING;" % kitakami_ident)
print("INSERT INTO region_names (region_id, local_language_id, name) SELECT id, 9, '%s' FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (kitakami, kitakami_ident))
print("INSERT INTO regions (id, identifier) VALUES (12, '%s') ON CONFLICT DO NOTHING;" % blueberry_ident)
print("INSERT INTO region_names (region_id, local_language_id, name) SELECT id, 9, '%s' FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (blueberry, blueberry_ident))

print("INSERT INTO pokedexes (id, region_id, identifier, is_main_series) SELECT 29, id, '%s', true FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (hisui_ident, hisui_ident))
print("INSERT INTO pokedexes (id, region_id, identifier, is_main_series) SELECT 30, id, '%s', true FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (region_ident, region_ident))
print("INSERT INTO pokedexes (id, region_id, identifier, is_main_series) SELECT 31, id, '%s', true FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (kitakami_ident, kitakami_ident))
print("INSERT INTO pokedexes (id, region_id, identifier, is_main_series) SELECT 32, id, '%s', true FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % ("blueberry", blueberry_ident))

print("INSERT INTO generations (id, main_region_id, identifier) SELECT 9, id, '%s' FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % ('generation-ix', region_ident))
print("INSERT INTO version_groups (id, identifier, generation_id, \"order\") VALUES (21, 'brilliant-diamond-shining-pearl', 8, 21) ON CONFLICT DO NOTHING;")
print("INSERT INTO version_groups (id, identifier, generation_id, \"order\") VALUES (22, 'legends-arceus', 8, 22) ON CONFLICT DO NOTHING;")
print("INSERT INTO version_groups (id, identifier, generation_id, \"order\") VALUES (23, 'scarlet-violet', 9, 23) ON CONFLICT DO NOTHING;")

evolution_map = {}
name_map = {}

for pokemon in data:
    species_id = None
    if pokemon['id'] < first_form_id:
        # Not a form
        # Correct non-natdex IDs for Paldean Pokémon. (No longer necessary with Teal Mask data file.)
        # if pokemon['name'] in natdex_map:
        #     pokemon['id'] = natdex_map[pokemon['name']]
        name_map[pokemon['name']] = pokemon
        species_id = pokemon['id']
    else:
        species_id = name_map[pokemon['name'].rsplit('-', 1)[0]]['id']
    if pokemon['evolutions']:
        for evolution in pokemon['evolutions']:
            if re.search(r'-\d+$', evolution['species']) is not None:
                evolution_map[evolution['species'].rsplit('-', 1)[0]] = species_id
            else:
                evolution_map[evolution['species']] = species_id

# pokemon_order is whichever is the highest order value in the pokemon table currently. Right now we're just lazily incrementing it for each new Pokémon/form.
pokemon_order = 3192

for pokemon in data:
    pokemon_ident = None
    pokemon_form_ident = None
    form_ident = None
    species = None
    form_num = 0
    if pokemon['id'] < first_form_id:
        pokemon_ident = make_identifier(pokemon['name'])
        pokemon_form_ident = pokemon_ident
        species = pokemon
        if pokemon['name'] not in evolution_map and not pokemon['evolutions']:
            print("INSERT INTO evolution_chains (id) SELECT MAX(id) + 1 FROM evolution_chains;")
        print("INSERT INTO pokemon_species (id, identifier, generation_id, evolves_from_species_id, evolution_chain_id, color_id, shape_id, habitat_id, gender_rate, capture_rate, base_happiness, is_baby, hatch_counter, has_gender_differences, growth_rate_id, forms_switchable, is_legendary, is_mythical, \"order\") SELECT %s, '%s', %s, %s, %s, %s, 1, NULL, -1, %s, 70, false, %s, false, %s, false, %s, %s, %s ON CONFLICT (id) DO UPDATE SET capture_rate = excluded.capture_rate;" % (
            pokemon['id'],
            pokemon_ident,
            8 if pokemon['id'] < 906 else 9,
            evolution_map[pokemon['name']] if pokemon['name'] in evolution_map else 'NULL',
            ('(SELECT evolution_chain_id FROM pokemon_species WHERE id = \'%s\')' % evolution_map[pokemon['name']]) if pokemon['name'] in evolution_map else '(SELECT MAX(evolution_chain_id) + 1 FROM pokemon_species)',
            '(SELECT id FROM pokemon_colors WHERE identifier = \'%s\')' % pokemon['color'].lower(),
            pokemon['catch_rate'],
            pokemon['hatch_cycles'],
            '(SELECT id FROM growth_rates WHERE identifier = \'%s\')' % GROWTH_RATES[pokemon['exp_group']],
            "true" if pokemon_ident in ('koraidon', 'miraidon', 'chi-yu', 'teng-lu', 'chien-pao', 'wo-chien', 'okidogi', 'munkidori', 'fezandipiti', 'ogerpon') else "false",
            "false",
            pokemon['id']
        ))

        print("INSERT INTO pokemon_species_names (pokemon_species_id, local_language_id, name, genus) VALUES (%s, 9, E'%s', '') ON CONFLICT DO NOTHING;" % (
            pokemon['id'],
            pokemon['name'].encode('unicode-escape').replace('\\x', '\\u00')
        ))

        print("INSERT INTO pokemon_dex_numbers (species_id, pokedex_id, pokedex_number) VALUES (%s, 1, %s) ON CONFLICT DO NOTHING;" % (pokemon['id'], pokemon['id']))

    else:
        name, form_num = pokemon['name'].rsplit('-', 1)
        species = name_map[name]
        pokemon_ident = make_identifier(name)
        pokemon_form_ident = pokemon_ident

    if pokemon['dex']:
        print("INSERT INTO pokemon_dex_numbers (species_id, pokedex_id, pokedex_number) VALUES (%s, 30, %s) ON CONFLICT DO NOTHING;" % (species['id'], pokemon['dex']))

    if pokemon['kitakami_dex']:
        print("INSERT INTO pokemon_dex_numbers (species_id, pokedex_id, pokedex_number) VALUES (%s, 31, %s) ON CONFLICT DO NOTHING;" % (
            species['id'], pokemon['kitakami_dex']))

    if pokemon['blueberry_dex']:
        print("INSERT INTO pokemon_dex_numbers (species_id, pokedex_id, pokedex_number) VALUES (%s, 32, %s) ON CONFLICT DO NOTHING;" % (species['id'], pokemon['blueberry_dex']))

    if str(species['id']) in forms_data:
        form_ident = forms_data[str(species['id'])][int(form_num)]
        if form_ident:
            if form_ident == 'dusk-mane':
                form_ident = 'dusk'
            elif form_ident == 'dawn-wings':
                form_ident = 'dawn'
            elif form_ident.endswith('-core'):
                form_ident = form_ident[:-5]
            elif form_ident == 'original-color':
                form_ident = 'original'
            elif form_ident == '50-percent':
                form_ident = '50'
            elif form_ident == '10-percent':
                form_ident = '10'
            pokemon_form_ident += '-' + form_ident
        elif form_ident is None and form_num > 0:
            # Ignore null forms after the first.
            continue


    pokemon_order += 1

    pokemon_table_ident = pokemon_ident if species['id'] in PSEUDOFORMS or (pokemon['id'] < first_form_id and species['id'] in ANON_DEFAULT_FORM) else pokemon_form_ident

    # print("SELECT '%s', '%s', '%s', '%s';" % (pokemon_ident, pokemon_form_ident, pokemon['id'], species['id']))
    print("INSERT INTO pokemon (id, identifier, species_id, height, weight, base_experience, \"order\", is_default) VALUES (%s, '%s', %s, %s, %s, 65, %s, %s) ON CONFLICT DO NOTHING;" % (
        pokemon['id'] if pokemon['id'] < first_form_id else ("COALESCE((SELECT id FROM pokemon WHERE identifier = '%s'), (SELECT MAX(id) + 1 FROM pokemon))" % pokemon_table_ident),
        pokemon_table_ident,
        species['id'],
        int(pokemon['height'] * 10),
        int(pokemon['weight'] * 10),
        pokemon_order,
        "true" if pokemon['id'] < first_form_id else "false"
    ))

    for i, t in enumerate(pokemon['types']):
        print("SELECT '%s';" % pokemon_table_ident)
        print("SELECT id, '%s', '%s' FROM pokemon WHERE identifier = '%s';" % (pokemon_ident, pokemon_form_ident, pokemon_table_ident))
        print("INSERT INTO pokemon_types (pokemon_id, type_id, slot) SELECT %s, id, %s FROM types WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (
            "(SELECT id FROM pokemon WHERE identifier = '%s')" % pokemon_table_ident,
            i + 1,
            make_identifier(t)
        ))

    for i, stat in enumerate(pokemon['base_stats']):
        print("INSERT INTO pokemon_stats (pokemon_id, stat_id, base_stat, effort) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;" % (
            "(SELECT id FROM pokemon WHERE identifier = '%s')" % pokemon_table_ident,
            i + 1,
            stat,
            pokemon['ev_yield'][i]
        ))

    print("INSERT INTO pokemon_forms (id, identifier, form_identifier, pokemon_id, introduced_in_version_group_id, is_default, is_battle_only, is_mega, form_order, \"order\") VALUES (%s, '%s', %s, %s, %s, %s, false, false, 1, (SELECT MAX(\"order\") + 1 FROM pokemon_forms)) ON CONFLICT DO NOTHING;" % (
        pokemon['id'] if pokemon['id'] < first_form_id else ("(COALESCE((SELECT id FROM pokemon_forms WHERE identifier = '%s'), (SELECT MAX(id) + 1 FROM pokemon_forms)))" % pokemon_form_ident),
        pokemon_form_ident,
        form_ident and ("'%s'" % form_ident) or 'NULL',
        "(SELECT id FROM pokemon WHERE identifier = '%s')" % pokemon_table_ident,
        22 if species['id'] < 906 and species['id'] > 898 or form_ident and 'hisui' in form_ident else 23,
        "true" if pokemon['id'] < first_form_id or species['id'] not in PSEUDOFORMS else "false"
    ))

    form_name = ("E'%s %s'" % (' '.join(('Paldean' if word == 'paldea' else 'Hisuian' if word == 'hisui' else word.capitalize()) for word in form_ident.split('-')), species['name'])).encode('unicode-escape').replace('\\x', '\\u00') if form_ident else 'NULL'

    print("INSERT INTO pokemon_form_names (pokemon_form_id, local_language_id, form_name, pokemon_name) VALUES (%s, 9, %s, %s) ON CONFLICT DO NOTHING;" % (
        pokemon['id'] if pokemon['id'] < first_form_id else ("(SELECT id FROM pokemon_forms WHERE identifier = '%s')" % pokemon_form_ident),
        form_name,
        form_name
    ))

print("COMMIT;")
