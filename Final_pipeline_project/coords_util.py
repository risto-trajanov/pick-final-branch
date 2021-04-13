

def get_height(coords):
    minx = 10000
    miny = 10000
    maxx = 0
    maxy = 0
    for c in coords:
        minx = min(minx, int(c['x_0']))
        maxx = max(maxx, int(c['x_1']))
        miny = min(miny, int(c['y_0']))
        maxy = max(maxy, int(c['y_1']))

    height = maxy + miny
    return height


def clean_feature(feature):
    feature = feature.strip()
    if len(feature) == 0:
        return feature
    if feature[-1] == '.' or feature[-1] == ':' or feature[-1] == '.':
        feature = feature[:-1]
    if len(feature) == 0:
        return feature
    if feature[-1] == '.' or feature[-1] == ':' or feature[-1] == '.':
        feature = feature[:-1]
    return feature


def split_words(coords):
    n = []
    for c in coords:
        words = str(c['text']).strip().split(' ')
        if len(str(c['text'])) == 0:
            continue
        char_len = int((int(c['x_1']) - int(c['x_0'])) / len(str(c['text'])))
        chars = 0
        for word in words:
            word = word.strip()
            if len(word) == 0:
                continue
            cc = dict()
            cc['text'] = word
            cc['y_1'] = int(c['y_1'])
            cc['y_0'] = int(c['y_0'])
            cc['x_0'] = int(c['x_0']) + chars * char_len
            cc['x_1'] = int(c['x_0']) + (chars + len(word)) * char_len
            if 'page' not in c:
                c['page'] = 1
            cc['page'] = int(c['page'])
            chars = chars + len(word) + 1
            if len(word.strip()) > 0:
                n.append(cc)
    return n


def get_right_coords(d, coords):
    y = int(d['y_0']) + int((int(d['y_1']) - int(d['y_0'])) / 2)
    i = 0
    min = 10000
    imin = -1
    for d2 in coords:
        if d['page'] != d2['page']:
            i += 1
            continue
        if int(d2['y_0']) <= y <= int(d2['y_1']):
            if min > int(d2['x_0']) >= int(d['x_1']):
                if int(d2['x_0']) < int(d['x_1']) + int(int(d['y_1']) - int(d['y_0'])) * 20:
                    min = int(d2['x_0'])
                    imin = i
        i += 1
    if imin >= 0:
        return coords[imin]
    return None


def get_left_coords(d, coords):
    y = int(d['y_0']) + int((int(d['y_1']) - int(d['y_0'])) / 2)
    i = 0
    max = 0
    imax = -1
    for d2 in coords:
        if d['page'] != d2['page']:
            i += 1
            continue
        if int(d2['y_0']) <= y <= int(d2['y_1']):
            if int(d2['x_0']) > max and int(d2['x_1']) <= int(d['x_0']):
                if int(d2['x_0']) >= int(d['x_0']) - int(int(d['y_1']) - int(d['y_0'])) * 20:
                    max = int(d2['x_0'])
                    imax = i
        i += 1
    if imax >= 0:
        return coords[imax]
    return None


def get_top_coords(d, coords):
    i = 0
    max = 0
    imax = -1
    for d2 in coords:
        if d['page'] != d2['page']:
            i += 1
            continue
        if int(d2['x_0']) <= int(d['x_0']) <= int(d2['x_1']) or int(d['x_0']) <= int(d2['x_0']) <= int(d['x_1']):
            if int(d2['y_1']) <= int(d['y_0']) and int(d2['y_0']) >= int(d['y_0']) - int(int(d['y_1']) - int(d['y_0'])) * 3:
                if imax > -1:
                    dd = coords[imax]
                if imax > -1 and (d2['y_0'] <= dd['y_0'] <= d2['y_1'] or dd['y_0'] <= d2['y_0'] <= dd['y_1']):
                        if d2['x_0'] < dd['x_0']:
                            max = int(d2['y_0'])
                            imax = i
                elif int(d2['y_0']) > max:
                    max = int(d2['y_0'])
                    imax = i
        i += 1
    if imax >= 0:
        return coords[imax]
    return None

def get_top_coords_any(d, coords):
    i = 0
    max = 0
    imax = -1
    for d2 in coords:
        if d['page'] != d2['page']:
            i += 1
            continue
        if int(d2['x_0']) <= int(d['x_0']) <= int(d2['x_1']) or int(d['x_0']) <= int(d2['x_0']) <= int(d['x_1']):
            if int(d2['y_1']) <= int(d['y_0']):
                if imax > -1:
                    dd = coords[imax]
                if imax > -1 and (d2['y_0'] <= dd['y_0'] <= d2['y_1'] or dd['y_0'] <= d2['y_0'] <= dd['y_1']):
                    if d2['x_0'] < dd['x_0']:
                        max = int(d2['y_0'])
                        imax = i
                elif int(d2['y_0']) > max:
                    max = int(d2['y_0'])
                    imax = i
        i += 1
    if imax >= 0:
        return coords[imax]
    return None


def get_bottom_coords(d, coords):
    i = 0
    min = 10000
    imin = -1
    for d2 in coords:
        if d['page'] != d2['page']:
            i += 1
            continue
        if int(d2['x_0']) <= int(d['x_0']) <= int(d2['x_1']) or int(d['x_0']) <= int(d2['x_0']) <= int(d['x_1']):
            if int(d2['y_0']) >= int(d['y_1']) and int(d2['y_0']) <= int(d['y_0']) + int(int(d['y_1']) - int(d['y_0'])) * 3:
                if imin > -1:
                    dd = coords[imin]
                if imin > -1 and (d2['y_0'] <= dd['y_0'] <= d2['y_1'] or dd['y_0'] <= d2['y_0'] <= dd['y_1']):
                    if d2['x_0'] < dd['x_0']:
                        min = int(d2['y_0'])
                        imin = i
                elif int(d2['y_0']) < min:
                    min = int(d2['y_0'])
                    imin = i

        i += 1
    if imin >= 0:
        return coords[imin]
    return None

def get_bottom_coords_any(d, coords):
    i = 0
    min = 10000
    imin = -1
    for d2 in coords:
        if d['page'] != d2['page']:
            i += 1
            continue
        if int(d2['x_0']) <= int(d['x_0']) <= int(d2['x_1']) or int(d['x_0']) <= int(d2['x_0']) <= int(d['x_1']):
            if int(d2['y_0']) >= int(d['y_1']):
                if imin > -1:
                    dd = coords[imin]
                if imin > -1 and (d2['y_0'] <= dd['y_0'] <= d2['y_1'] or dd['y_0'] <= d2['y_0'] <= dd['y_1']):
                    if d2['x_0'] < dd['x_0']:
                        min = int(d2['y_0'])
                        imin = i
                elif int(d2['y_0']) < min:
                    min = int(d2['y_0'])
                    imin = i

        i += 1
    if imin >= 0:
        return coords[imin]
    return None

