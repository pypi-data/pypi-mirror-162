from datetime import datetime

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def convertdate2(date, input_formats, output_format="%Y-%m-%d"):
    if not date: return None

    for input_format in input_formats.split(';'):
        try:
            return datetime.strptime(date, input_format).strftime(output_format)
        except:
            continue
    raise Exception('Cannot translate state_date "%s"' % date)

def translate_status(record):
    status = record.STATUS_CATEGORY or record.STATUS_NAME
    if not status: return 'Unknown'

    status_map = { 'abandoned with finality': 'Ended',
                   'cancelled': 'Ended',
                   'refused for non-use': 'Ended',
                   'in verification of publication conditions': 'Pending',
                   'awaiting for bla notification about result of opposition process': 'Pending',
                   'refused with finality': 'Ended',
                   'removed from register for non-use': 'Ended',
                   'voluntarily abandoned': 'Ended',
                   'withdrawn': 'Ended',
                   'appeal pending': 'Pending',
                   'in examination': 'Pending',
                   'pending': 'Pending',
                   'for validation': 'Pending',
                   'registered': 'Registered',
                   '(migration) pending': 'Pending',
                   'abandoned with finality in examination': 'Ended',
                   'abandoned with finality in publication': 'Ended',
                   'awaiting due date to file payment of publication fee': 'Pending',
                   'awaiting for bla notification about possible oppositions': 'Pending',
                   'awaiting processing of appeal': 'Pending',
                   'awaiting processing of revival': 'Pending',
                   'finally refused': 'Ended',
                   'in assignment of responsible examiner for examination': 'Pending',
                   'in data capture of paper applications': 'Pending',
                   'inactive (dead number)': 'Expired',
                   'refused for non-filing of dau': 'Ended',
                   'refused for non-filing of dau / dnu': 'Ended',
                   'removed from register for non-filing of dau': 'Ended',
                   'removed from register for non-filing of dau / dnu': 'Ended',
                   'renewed': 'Registered',
                   'to abandon with finality for non-filing of revival': 'Ended',
                   'to check for renewal': 'Registered',
                   'to proceed after due date to file appeal against refusal': 'Pending',
                   'to proceed after due date to file request for revival': 'Pending',
                   'to produce notice of allowance': 'Pending',
                   'expired': 'Expired' }

    if status.lower() in status_map:
        return status_map[status.lower()]

    raise Exception('Status "%s" unmapped' % status)


def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == 'B': return 'Combined'
    if feature == 'L': return 'Figurative'
    if feature == 'N': return 'Word'

    raise Exception('Feature "%s" unmapped' % feature)

def get_address(record):
    if not record: return None

    addr = [ record.ADDR_STREET, record.CITY_NAME,
             record.STATE_NAME, record.PROVINCE_NAME ]
    addr = [x for x in addr if x]

    return ', '.join(addr)
