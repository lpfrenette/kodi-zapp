"""Quebec / francophone Canadian specialty TV labels present in the provider list."""
from urllib.parse import urlsplit
from resources.lib.local_channels import normalized, regroup_record

QUEBEC_GROUP = 'Québec — Chaînes spécialisées'
SPECIALTY = {
    'ADDIK TV', 'AMI TELE', 'ARTV', 'ASSEMBLEE NATIONALE', 'CANAL D',
    'CANAL SAVOIR', 'CASA', 'CINEPOP', 'CPAC', 'ELLE FICTIONS', 'EVASION',
    'FRISSONS TV', 'HISTORIA', 'ICI EXPLORA', 'ICI RDI', 'INVESTIGATION',
    'LCN', 'MATV', 'MAX', 'METEO MEDIA', 'NATYF TV', 'PLANETE CANADA',
    'PRISE 2', 'RDS INFO', 'SAISONS', 'SERIES PLUS',
    'STINGRAY FRANCO COUNTRY', 'STINGRAY FRANCO RETRO', 'STINGRAY PALMARES ADISQ',
    'SUPER ECRAN 1', 'SUPER ECRAN 2', 'SUPER ECRAN 3', 'SUPER ECRAN 4',
    'TELETOON', 'TEMOIN', 'TFO', 'TV5', 'UNIS TV', 'VIE', 'Z TELE', 'ZESTE',
}


def with_quebec_group(records):
    result = []
    for record in records:
        stream_path = urlsplit(record['url']).path.lower()
        match = (record['group'] in ('FRENCH', QUEBEC_GROUP)
                 and '/movie/' not in stream_path and '/series/' not in stream_path
                 and normalized(record['name']) in SPECIALTY)
        result.append(regroup_record(record, QUEBEC_GROUP) if match else record)
    return result
