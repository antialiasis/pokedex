# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import json
import re

GROWTH_RATES = {
    'Slow': 'slow',
    'MediumFast': 'medium',
    'Fast': 'fast',
    'MediumSlow': 'medium-slow',
    'Erratic': 'slow-then-very-fast',
    'Fluctuating': 'fast-then-very-slow',
}

PSEUDOFORMS = [
    421,
    422,
    423,
    649,
    716,
    773,
    854,
    855,
]

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

data = json.load(open('C:\\Users\\antialiasis\\Documents\\TCoD\\Flask\\tcod\\tcod\\data-files\\pokemon.json'))
forms_data = json.load(open(r'C:\\Users\\antialiasis\\Documents\\TCoD\\Flask\\tcod\\scripts\\data-files\\forms.json'))
armor_dex_file = open('C:\\Users\\antialiasis\\Documents\\TCoD\\Flask\\tcod\\tcod\\data-files\\armor-dex.txt')
tundra_dex_file = open('C:\\Users\\antialiasis\\Documents\\TCoD\\Flask\\tcod\\tcod\\data-files\\tundra-dex.txt')

armor_dex = {}
for line in armor_dex_file:
    match = DEX_REGEX.match(line)
    if not match:
        raise ValueError("Malformatted armor dex line!", line)
    armor_dex[int(match.group(2))] = int(match.group(1))

tundra_dex = {}
for line in tundra_dex_file:
    match = DEX_REGEX.match(line)
    if not match:
        raise ValueError("Malformatted armor dex line!", line)
    tundra_dex[int(match.group(2))] = int(match.group(1))

region = "Galar"
region_ident = make_identifier(region)
first_form_id = 901

print("BEGIN;")
print("INSERT INTO regions (id, identifier) VALUES (8, '%s') ON CONFLICT DO NOTHING;" % region_ident)
print("INSERT INTO region_names (region_id, local_language_id, name) SELECT id, 9, '%s' FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (region, region_ident))
print("INSERT INTO pokedexes (id, region_id, identifier, is_main_series) SELECT 26, id, '%s', true FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (region_ident, region_ident))
print("INSERT INTO pokedexes (id, region_id, identifier, is_main_series) SELECT 27, id, '%s', true FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % ('isle-of-armor', region_ident))
print("INSERT INTO pokedexes (id, region_id, identifier, is_main_series) SELECT 28, id, '%s', true FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % ('crown-tundra', region_ident))
print("INSERT INTO generations (id, main_region_id, identifier) SELECT 8, id, '%s' FROM regions WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % ('generation-viii', region_ident))
print("INSERT INTO version_groups (id, identifier, generation_id, \"order\") VALUES (19, 'lets-go', 7, 19) ON CONFLICT DO NOTHING;")
print("INSERT INTO version_groups (id, identifier, generation_id, \"order\") VALUES (20, 'sword-shield', 8, 20) ON CONFLICT DO NOTHING;")

evolution_map = {}
name_map = {}

for pokemon in data:
    species_id = None
    if pokemon['id'] < first_form_id:
        # Not a form
        name_map[pokemon['name']] = pokemon
        species_id = pokemon['id']
    else:
        species_id = name_map[pokemon['name'].rsplit(' ', 1)[0]]['id']
    if pokemon['evolutions']:
        for evolution in pokemon['evolutions']:
            if re.search(r'-\d+$', evolution['species']) is not None:
                evolution_map[evolution['species'].rsplit('-', 1)[0]] = species_id
            else:
                evolution_map[evolution['species']] = species_id

pokemon_order = 956

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
        if pokemon['name'] not in evolution_map and False:
            print("INSERT INTO evolution_chains (id) SELECT MAX(id) + 1 FROM evolution_chains;")
        print("INSERT INTO pokemon_species (id, identifier, generation_id, evolves_from_species_id, evolution_chain_id, color_id, shape_id, habitat_id, gender_rate, capture_rate, base_happiness, is_baby, hatch_counter, has_gender_differences, growth_rate_id, forms_switchable, is_legendary, is_mythical, \"order\") SELECT %s, '%s', %s, %s, %s, %s, 1, NULL, -1, %s, 70, false, %s, false, %s, false, %s, %s, %s ON CONFLICT (id) DO UPDATE SET capture_rate = excluded.capture_rate;" % (
            pokemon['id'],
            pokemon_ident,
            7 if pokemon_ident in ('meltan', 'melmetal') else 8,
            evolution_map[pokemon['name']] if pokemon['name'] in evolution_map else 'NULL',
            ('(SELECT evolution_chain_id FROM pokemon_species WHERE id = \'%s\')' % evolution_map[pokemon['name']]) if pokemon['name'] in evolution_map else '(SELECT MAX(evolution_chain_id) + 1 FROM pokemon_species)',
            '(SELECT id FROM pokemon_colors WHERE identifier = \'%s\')' % pokemon['color'].lower(),
            pokemon['catch_rate'],
            pokemon['hatch_cycles'],
            '(SELECT id FROM growth_rates WHERE identifier = \'%s\')' % GROWTH_RATES[pokemon['exp_group']],
            "true" if pokemon_ident in ('zacian', 'zamazenta', 'eternatus', 'kubfu', 'urshifu', 'regieleki', 'regidrago', 'glastrier', 'spectrier', 'calyrex') else "false",
            "true" if pokemon_ident in ('zarude',) else "false",
            pokemon['id']
        ))

        print("INSERT INTO pokemon_species_names (pokemon_species_id, local_language_id, name, genus) VALUES (%s, 9, E'%s', '') ON CONFLICT DO NOTHING;" % (
            pokemon['id'],
            pokemon['name'].encode('unicode-escape')
        ))

        print("INSERT INTO pokemon_dex_numbers (species_id, pokedex_id, pokedex_number) VALUES (%s, 1, %s) ON CONFLICT DO NOTHING;" % (pokemon['id'], pokemon['id']))
        if pokemon['galar_dex'] and pokemon['galar_dex'] != "foreign":
            print("INSERT INTO pokemon_dex_numbers (species_id, pokedex_id, pokedex_number) VALUES (%s, 26, %s) ON CONFLICT DO NOTHING;" % (pokemon['id'], pokemon['galar_dex']))
        if pokemon['id'] in armor_dex:
            print("INSERT INTO pokemon_dex_numbers (species_id, pokedex_id, pokedex_number) VALUES (%s, 27, %s) ON CONFLICT DO NOTHING;" % (pokemon['id'], armor_dex[pokemon['id']]))
        if pokemon['id'] in tundra_dex:
            print("INSERT INTO pokemon_dex_numbers (species_id, pokedex_id, pokedex_number) VALUES (%s, 28, %s) ON CONFLICT DO NOTHING;" % (pokemon['id'], tundra_dex[pokemon['id']]))

    else:
        name, form_num = pokemon['name'].rsplit(' ', 1)
        species = name_map[name]
        pokemon_ident = make_identifier(name)
        pokemon_form_ident = pokemon_ident

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

    pokemon_order += 1
    # print("SELECT '%s', '%s', '%s';" % (pokemon_ident, pokemon['id'], species['id']))
    print("INSERT INTO pokemon (id, identifier, species_id, height, weight, base_experience, \"order\", is_default) VALUES (%s, '%s', %s, %s, %s, 65, %s, %s) ON CONFLICT DO NOTHING;" % (
        pokemon['id'] if pokemon['id'] < first_form_id else ("COALESCE((SELECT id FROM pokemon WHERE identifier = '%s'), (SELECT MAX(id) + 1 FROM pokemon))" % (pokemon_ident if species['id'] in PSEUDOFORMS else pokemon_form_ident)),
        pokemon_ident if species['id'] in PSEUDOFORMS else pokemon_form_ident,
        species['id'],
        int(pokemon['height'] * 10),
        int(pokemon['weight'] * 10),
        pokemon_order,
        "true" if pokemon['id'] < first_form_id else "false"
    ))

    for i, t in enumerate(pokemon['types']):
        print("INSERT INTO pokemon_types (pokemon_id, type_id, slot) SELECT %s, id, %s FROM types WHERE identifier = '%s' ON CONFLICT DO NOTHING;" % (
            "(SELECT id FROM pokemon WHERE identifier = '%s')" % (pokemon_ident if species['id'] in PSEUDOFORMS else pokemon_form_ident),
            i + 1,
            make_identifier(t)
        ))

    for i, stat in enumerate(pokemon['base_stats']):
        print("INSERT INTO pokemon_stats (pokemon_id, stat_id, base_stat, effort) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;" % (
            "(SELECT id FROM pokemon WHERE identifier = '%s')" % (pokemon_ident if species['id'] in PSEUDOFORMS else pokemon_form_ident),
            i + 1,
            stat,
            pokemon['ev_yield'][i]
        ))

    print("INSERT INTO pokemon_forms (id, identifier, form_identifier, pokemon_id, introduced_in_version_group_id, is_default, is_battle_only, is_mega, form_order, \"order\") VALUES (%s, '%s', %s, %s, %s, true, false, false, 1, (SELECT MAX(\"order\") + 1 FROM pokemon_forms)) ON CONFLICT DO NOTHING;" % (
        pokemon['id'] if pokemon['id'] < first_form_id else ("(COALESCE((SELECT id FROM pokemon_forms WHERE identifier = '%s'), (SELECT MAX(id) + 1 FROM pokemon_forms)))" % pokemon_form_ident),
        pokemon_form_ident,
        form_ident and ("'%s'" % form_ident) or 'NULL',
        "(SELECT id FROM pokemon WHERE identifier = '%s')" % (pokemon_ident if species['id'] in PSEUDOFORMS else pokemon_form_ident),
        19 if pokemon_ident in ('meltan', 'melmetal') else 20
    ))

    if pokemon['id'] > 893:
        form_name = ("E'%s %s'" % (' '.join((word.capitalize() if word != 'galar' else 'Galarian') for word in form_ident.split('-')), species['name'])).encode('unicode-escape') if form_ident else 'NULL'

        print("INSERT INTO pokemon_form_names (pokemon_form_id, local_language_id, form_name, pokemon_name) VALUES (%s, 9, %s, %s) ON CONFLICT DO NOTHING;" % (
            pokemon['id'] if pokemon['id'] < first_form_id else ("(SELECT id FROM pokemon_forms WHERE identifier = '%s')" % pokemon_form_ident),
            form_name,
            form_name
        ))

print("COMMIT;")
