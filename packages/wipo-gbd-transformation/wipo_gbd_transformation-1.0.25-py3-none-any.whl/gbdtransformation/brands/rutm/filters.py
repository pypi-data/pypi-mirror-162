# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Individual': return ['Individual']
    if kind == 'Collective': return ['Collective']
    if kind == 'Certificate': return ['Certificate']

    raise Exception('kind "%s" is not mapped.' % kind)

def get_path(path, data):
    if not path:
        return data
    tmp_path = path.split('.')
    if '[' in tmp_path[0]:
        if isinstance(data, list):
            nb = tmp_path[0].split('[')[1][:-1]
            return get_path('.'.join(tmp_path[1:]), data[nb])
        else:
            return get_path('.'.join(tmp_path[1:]), data[tmp_path[0].split('[')[0]])
    if isinstance(data, dict):
        if tmp_path[0] in data.keys():
            return get_path('.'.join(tmp_path[1:]), data[tmp_path[0]])


def get_trademark(data):
    if data.TradeMarkDetails:
        if isinstance(data.TradeMarkDetails.TradeMark, list):
            trademark = data.TradeMarkDetails.TradeMark[0]
            for transaction in data.TradeMarkDetails.TradeMark[1:]:
                trademark.update(transaction)
        else:
            trademark = data.TradeMarkDetails.TradeMark
        status = 'Registered'
        if get_path('MarkRecordDetails.MarkRecord[-1].BasicRecord.BasicRecordKind', trademark) == 'Non Renewal':
            status = 'Expired'
        return trademark, status
    if data.TradeMarkApplication:
        status = 'Pending'
        return data.TradeMarkApplication.TradeMarkDetails.TradeMark, status

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

def translate_feature(feature):
    if not feature: return 'Undefined'

    if feature == '3-D': return 'Three dimensional'
    if feature == 'Hologram': return 'Hologram'
    if feature == 'Colour': return 'Colour'
    if feature == 'Sound': return 'Sound'
    if feature == 'Olfactory': return 'Olfactory'
    if feature == 'Motion': return 'Motion'

    # the office wild card. bof
    if feature == 'Other': return 'Other'

    # has_word = get_path('WordMarkSpecification.MarkSignificantVerbalElement', trademark)
    # has_figure = get_path('MarkImageDetails.MarkImage.MarkImageFilename', trademark)

    # if has_word and has_figure: return 'Combined'
    # elif has_word: return 'Word'
    # elif has_figure: return 'Figurative'

    raise Exception('Feature "%s" unmapped' % feature)
