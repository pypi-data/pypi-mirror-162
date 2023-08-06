import re

def get_kind(info):
    if info.marart:
        nbs = info.marart.marartn

        if not isinstance(nbs, list):
            nbs = [nbs]

        for nb in nbs:
            if nb == '6':
                return ['Collective']

    return ['Individual']

def get_verbal(info):
    if info.markve:
        return info.markve

    # or get it from the picture remark
    if info.marpicrem:
        return info.marpicrem.replace('((fig.))', '')

def structure_gs(gsgr):
    if not gsgr: return {}

    nc = {} # nice classes and eventual goods services
    gs = [] # unclassified goods and services

    nice = gsgr.intregg
    if not isinstance(nice, list):
        nice = [nice]

    # get the nice classes
    for n in nice:
        nc[n.nicclai] = []

    # get the goods and services
    terms = gsgr.gstermt
    try:
        # terml means unclassified
        terms_lines = terms.gsterml
        if not isinstance(terms_lines, list):
            terms_lines = [terms_lines]

        l = []
        for t in terms_lines:
            if t:
                l += t.split('\n')

        terms_lines = l
    except:
        # classified (nice class indicated inline)
        terms_lines = terms.split('\n') if terms else []
        terms_lines = [line.strip() for line in terms_lines if line.strip()]

    nc_gs = gs
    for line in terms_lines:
        # get the numeric prefix if the line
        matches = re.findall(r'^0?(\d+):? (.*)', line)
        if len(matches):
            # split the class number and the rest of the line
            (cls, line) = matches[0]
            # try and find the nice class defined before
            # if not found, go to unclassified
            nc_gs = nc.get(cls, gs)
        nc_gs.append(line.strip())

    # join the lines then split on ';'
    for cls in nc:
        gslines = nc[cls]
        if len(gslines):
            nc[cls] = [term.strip().rstrip('.') for term in ' '.join(gslines).split(';')]

    return (nc, gs)

def get_roles(info):
    persons = info.regadr

    if not isinstance(persons, list):
        persons = [persons]

    matches = {
        'applicants': [],
        'representatives': [],
        'correspondence': None
    }

    def _get_person_info(p):
        info = {}
        nameadd = p.nameadd

        try:
            name = nameadd.namel.namell
            if isinstance(name, list):
                name = list(filter(None, name))
                name = ' '.join(name)
        except:
            name = nameadd.namel

        try:
            addr = nameadd.addrl.addrll
            if isinstance(addr, list):
                addr = list(filter(None, addr))
                addr = ', '.join(addr)
        except:
            addr = nameadd.addrl

        # complete the address with zipcode and city
        if nameadd.plainco:
            if addr: addr += ', '
            else: addr = ''
            addr += (nameadd.plainco)

        return {'name': name, 'addr': addr, 'nat': nameadd.nat}

    for p in persons:
        role = p.addrrole
        if role == '1':
            matches['applicants'].append(_get_person_info(p))
        elif role == '3':
            matches['representatives'].append(_get_person_info(p))
        elif role == '11':
            matches['correspondence'] = _get_person_info(p)
        # Licensee
        elif role == '6': continue
        # Bankruptcy office
        elif role == '7': continue
        # Usufructuary
        elif role == '8': continue
        # Pawnee
        elif role == '9': continue
        # Collection office
        elif role == '10': continue
        # Sub-Licensee
        elif role == '17': continue
        # Limited Licensee
        elif role == '19': continue
        # Exclusive Licensee
        elif role == '20': continue
        else:
            raise Exception('unindentified role [%s]' % role)

    return matches

def get_representatives(info):
    persons = info.regadr
    representatives = [p for p in persons if p.addrrole == '3']

    return representatives

def get_correspondence(info):
    persons = info.regadr
    correspondence = [p for p in persons if p.addrrole == '11']

    if len(correspondence): return correspondence[0]

def translate_status(status, deld):
    if deld: return 'Ended'
    if status == '0': return 'Pending'
    if status == '1': return 'Registered'

    raise Exception('Status "%s" unmapped' % status)

def translate_feature(feature, marart):
    if feature == '1': return 'Word'
    if feature == '2': return 'Figurative'
    if feature == '3': return 'Combined'
    if feature == '4':
        if not marart: return 'Undefined'
        # we do not support multi-value
        # for features. take the first one
        if isinstance(marart.marartn, list):
            marart.marartn = marart.marartn.pop()
        if marart.marartn == '10': return 'Sound'
        if marart.marartn == '11': return 'Three dimensional'
        if marart.marartn == '12': return 'Colour'
        if marart.marartn == '14': return 'Motion'
        if marart.marartn == '15': return 'Position'
        if marart.marartn == '16': return 'Hologram'

    raise Exception('Feature "%s" unmapped' % feature)

