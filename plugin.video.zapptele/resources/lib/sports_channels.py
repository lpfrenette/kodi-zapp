"""Personal sports preset, matched only within live TV provider categories."""
from resources.lib.local_channels import normalized, regroup_record

SPORTS_GROUP = 'Sports #tata'


def is_sports(record):
    if record['group'] not in ('FRENCH', 'ENGLISH', 'SPORTS', 'NHL', SPORTS_GROUP):
        return False
    name = normalized(record['name'])
    return (name in {'RDS', 'RDS 2', 'RDS2', 'TVA SPORTS', 'TVA SPORTS 2',
                     'NHL MONTREAL CANADIENS', 'NHL MONTREAL CANADIAN'}
            or name == 'TSN' or name.startswith('TSN ')
            or name.startswith('SPORTSNET ') or name == 'SPORTSNET'
            or name.startswith('SPORTS NET ') or name == 'SPORTS NET')


def with_sports_group(records):
    return [regroup_record(record, SPORTS_GROUP) if is_sports(record) else record
            for record in records]
