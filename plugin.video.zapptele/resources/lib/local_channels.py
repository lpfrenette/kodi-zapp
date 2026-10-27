"""Explicit regional presets matched against provider labels, never VOD titles."""
import re
import unicodedata

CITIES = ['Granby', 'Montréal', 'Québec', 'Ottawa–Gatineau', 'Sherbrooke', 'Saguenay', 'Trois-Rivières']
BASE = {'ICI TELE', 'ICI TELEVISION', 'TVA', 'NOOVO', 'TELE QUEBEC'}
REGIONS = {
    'Granby': {'ESTRIE', 'SHERBROOKE', 'MONTREAL'},
    'Montréal': {'MONTREAL'}, 'Québec': {'QUEBEC'},
    'Ottawa–Gatineau': {'OTTAWA', 'GATINEAU'},
    'Sherbrooke': {'SHERBROOKE', 'ESTRIE'},
    'Saguenay': {'SAGUENAY'}, 'Trois-Rivières': {'TROIS RIVIERES', 'MAURICIE'},
}


def normalized(name):
    name = ''.join(c for c in unicodedata.normalize('NFD', name.upper()) if not unicodedata.combining(c))
    name = re.sub(r'\((?:FR|EN)\)|\b(?:FHD|UHD|HD|SD|4K)\b', '', name)
    return re.sub(r'[^A-Z0-9]+', ' ', name).strip()


def is_local(record, city):
    if record['group'] not in ('FRENCH', 'ENGLISH', 'Locale'):
        return False
    name = normalized(record['name'])
    if name in BASE:
        return city in REGIONS
    for prefix in ('ICI TELE ', 'TVA ', 'CBC ', 'CTV ', 'CTV TWO ', 'CITY ', 'GLOBAL '):
        if name.startswith(prefix) and name[len(prefix):] in REGIONS.get(city, set()):
            return True
    return False


def with_local_group(records, city):
    if city not in REGIONS:
        return records
    result = []
    for record in records:
        if not is_local(record, city):
            result.append(record)
            continue
        result.append(regroup_record(record, 'Locale'))
    return result


def regroup_record(record, group):
    item = dict(record, group=group)
    lines = list(record['lines'])
    if re.search(r'group-title\s*=', lines[0], re.I):
        lines[0] = re.sub(r'group-title\s*=\s*([\"\']).*?\1', 'group-title="{}"'.format(group), lines[0], flags=re.I)
    else:
        # Insert before the first comma outside quoted attributes.
        quote = None
        for i, char in enumerate(lines[0]):
            if char in ('"', "'"):
                quote = None if quote == char else (char if quote is None else quote)
            elif char == ',' and quote is None:
                lines[0] = lines[0][:i] + ' group-title="{}"'.format(group) + lines[0][i:]
                break
    lines = ['#EXTGRP:' + group if line.startswith('#EXTGRP:') else line for line in lines]
    item['lines'] = lines
    return item
