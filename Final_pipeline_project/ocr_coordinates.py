import glob
import json
import cv2
import pytesseract
from pytesseract import Output
from image_preprocessing import ImagePreprocessing


def get_from_d(d, i):
    return d[i]['left'], d[i]['top'], d[i]['width'], d[i]['height'], d[i]['conf'], d[i]['line_num'], d[i]['par_num'], \
           d[i]['block_num'], d[i]['text']


def transform_d(d):
    dd = []
    n_boxes = len(d['left'])
    for i in range(n_boxes):
        (x, y, w, h, c, l, q, b, t) = d['left'][i], d['top'][i], d['width'][i], d['height'][i], d['conf'][i], \
                                      d['line_num'][i], d['par_num'][i], d['block_num'][i], d['text'][i]
        # filter out all elements with width and height less than 5px
        if w <= 5 or h <= 5 or t == '':
            continue

        dd.append({'left': x, 'top': y, 'width': w, 'height': h, 'conf': c, 'line_num': l, 'par_num': q, 'block_num': b,
                   'text': t})

    # join all elements who are closer than 5 px
    i = 0
    while i < len(dd):
        found = True
        while found and i < len(dd):
            found = False
            try:
                (x1, y1, w1, h1, c1, l1, q1, b1, t1) = get_from_d(dd, i)
            except Exception as e:
                print(e)
                continue
            if t1.strip() == '':
                continue
            foundIdx = -1
            foundD = ''
            for j in range(len(dd)):
                (x2, y2, w2, h2, c2, l2, q2, b2, t2) = get_from_d(dd, j)
                if t2.strip() == '':
                    continue
                # if int(c2) <= 0:
                #     continue
                if x1 < x2:
                    d = abs(x2 - x1 - w1)
                    if d < 16:
                        if (y1 <= y2 and y1 + h1 >= y2) or (y2 <= y1 and y2 + h2 >= y1):
                            found = True
                            foundIdx = j
                            if d > 2:
                                foundD = ' '
                            break
            if found:
                (x2, y2, w2, h2, c2, l2, q2, b2, t2) = get_from_d(dd, foundIdx)
                x = min(x1, x2)
                y = min(y1, y2)
                t = t1 + foundD + t2
                mx = max(x1 + w2, x2 + w2)
                my = max(y1 + h1, y2 + h2)
                w = mx - x
                h = my - y
                c = c1
                l = l1
                q = q1
                b = b1
                dd[i] = {'left': x, 'top': y, 'width': w, 'height': h, 'conf': c, 'line_num': l, 'par_num': q,
                         'block_num': b, 'text': t}
                dd.remove(dd[foundIdx])
        i = i + 1
    return dd


def get_coords_one_file(filename, page, preprocess=False):
    coords = []
    config = ''

    # preprocess
    if preprocess:
        img = ImagePreprocessing.preprocess(filename)
    else:
        img = cv2.imread(filename)

    dd = pytesseract.image_to_data(img, output_type=Output.DICT, lang='deu', config=config)
    dd = transform_d(dd)
    for d in dd:
        coords.append({"x_0": d['left'], "y_0": d['top'], "x_1": d['left'] + d['width'], "y_1": d['top'] + d['height'],
                       "page": page, "text": d['text']})
    return coords


def get_coords_file(filename):
    page = 0
    coords = []
    for file in glob.glob(filename + '*.jpg'):
        page = page + 1
        onecoords = get_coords_one_file(file, page)
        for c in onecoords:
            coords.append(c)

    f = open(filename + "_coords.json", "w")
    json.dump(coords, f)
    f.close()
