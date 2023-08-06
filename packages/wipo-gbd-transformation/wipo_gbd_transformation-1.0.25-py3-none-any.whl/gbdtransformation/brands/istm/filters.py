# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def get_full_address(applicant):
    if applicant.postalCode:
        return "%s %s" % (applicant.address, applicant.postalCode)
    return  applicant.address

def translate_status(status, status_is):
    # office did not map to english -> we do it
    if not status:
        if status_is == 'Áfrýjun': return 'Pending' # Appeal
        if status_is == 'Afturkallað': return 'Ended' # Revoked
        if status_is == 'Birt': return 'Pending' # Published
        if status_is == 'Andmæli': return 'Opposition' # Published
        if status_is == 'Krafa um niðurfellingu': return 'Ended' # Request for cancellation
        if status_is == 'Tilbúið til birtingar': return 'Pending' # Ready for publishing
        if status_is == 'Í rannsókn': return 'Registered' # Investigating ..
        if status_is == 'Krafa um ógildingu': return 'Registered' # Claim for annulment ..

    if status == 'Filed': return 'Pending'
    if status == 'Expired': return 'Expired'
    if status == 'Ended': return 'Ended'
    if status == 'Registered': return 'Registered'

    raise Exception('Status "%s/%s" unmapped' % (status, status_is))


def translate_feature(feature, is3D):
    if not feature: return 'Undefined'

    if is3D: return "Three dimensional"
    if feature == 'orð- og myndmerki': return "Combined"
    if feature == 'myndmerki': return "Figurative"
    if feature == 'orðmerki': return "Word"
    if feature == 'orðmerki skannað': return "Stylized characters"
    if feature == 'hljóðmerki': return "Sound"
    if feature == 'þrívíddarmerki með orðhluta': return "Three dimensional"
    if feature == 'staðsetningarmerki': return "Position"
    if feature == 'annað': return "Other"
    if feature == 'hreyfimerki': return "Motion"
    if feature == 'mynsturmerki': return "Pattern"
    if feature == 'margmiðlunarmerki': return "Multimedia"


    raise Exception('feature "%s" unmapped' % feature)

