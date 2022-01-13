REPLACEWORDS = ['incorporated', 'the', 'corporation']
ENDWORDS = ['inc', 'co']


def rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    else:
        return s


def clean_org(w):
    # lower case
    w = w.lower()

    #remove non alphanum
    w = ''.join([w_ for w_ in w  if (w_.isalnum() or w_==' ')])

    #treat common words that have no value (qualitative)
    for cw in ENDWORDS:
        w = rchop(w, cw)
    for cw in REPLACEWORDS:
        w = w.replace(cw, '')

    # remove whitespace at ends
    w = w.strip()

    return w

