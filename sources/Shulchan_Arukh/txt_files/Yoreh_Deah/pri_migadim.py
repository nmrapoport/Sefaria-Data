# encoding=utf-8

import re
import os
import codecs
from data_utilities.util import ja_to_xml
from data_utilities.util import getGematria, PlaceHolder, convert_dict_to_array, clean_whitespace

import django
django.setup()
from sefaria.model import *

print "\nParsing Mishbezot Zahav"

with codecs.open(u'./part_1/שולחן ערוך יורה דעה חלק א משבצות זהב.txt', 'r', 'utf-8') as fp:
    my_lines = fp.readlines()

siman, seif = None, 0
holder = PlaceHolder()
for line in my_lines:
    if holder(re.search(u'@22([\u05d0-\u05ea]{1,2})', line)):
        siman, seif = getGematria(holder.group(1)), 0
    elif holder(re.search(u'@44\(([\u05d0-\u05ea]{1,2})\)', line)):
        new_seif = getGematria(holder.group(1))
        if new_seif - seif != 1:
            print "Siman {}: Jump from seif {} to {}".format(siman, seif, new_seif)
        seif = new_seif

del seif

mishbetzot = []
chapter, seif = None, None
chap_num, seif_num = -1, -1

holder = PlaceHolder()
for line in my_lines:
    if holder(re.search(u'@22([\u05d0-\u05ea]{1,2})', line)):
        if chapter is not None:
            if seif is not None:
                chapter[seif_num - 1] = seif
            mishbetzot.append(convert_dict_to_array(chapter, default_value=list))
        chapter, chap_num = {}, getGematria(holder.group(1))
        seif, seif_num = None, -1

    elif holder(re.search(u'@44\(([\u05d0-\u05ea]{1,2})\)', line)):
        if seif is not None:
            chapter[seif_num - 1] = seif
        seif, seif_num = [], getGematria(holder.group(1))

    else:
        assert re.match(u'^@11', line) is not None
        fixed_line = re.sub(u'@11([^@]+)@33', u'<b>\g<1></b>', line)
        fixed_line = re.sub(u'\s?@66[\[(]#[\])]\s?', u'\u270d', fixed_line)
        fixed_line = re.sub(u'@\d{2}', u'', fixed_line)
        fixed_line = re.sub(u' {2,}', u' ', fixed_line)
        fixed_line = re.sub(u'^ +| +$', u'', fixed_line)
        seif.append(fixed_line)
chapter[seif_num - 1] = seif
mishbetzot.append(convert_dict_to_array(chapter, default_value=list))

with codecs.open(u'./part_2/משבצות זהב  יורה דעה חלק ב.txt', 'r', 'utf-8') as fp:
    my_lines = fp.readlines()

siman, seif = None, 0
holder = PlaceHolder()
for line in my_lines:
    if holder(re.search(u'@22([\u05d0-\u05ea]{1,3})', line)):
        siman, seif = getGematria(holder.group(1)), 0

    elif holder(re.search(u'@11\(([\u05d0-\u05ea]{1,2})\)', line)):
        new_seif = getGematria(holder.group(1))
        if new_seif - seif != 1:
            print "Siman {}: Jump from seif {} to {}".format(siman, seif, new_seif)
        seif = new_seif
del chapter, chap_num, seif_num, seif

chapter, seif = None, None
chap_num, seif_num = -1, -1

for line in my_lines:
    if holder(re.search(u'@22([\u05d0-\u05ea]{1,3})', line)):
        if chapter is not None:
            if seif is not None:
                chapter[seif_num - 1] = seif
            mishbetzot.append(convert_dict_to_array(chapter, default_value=list))
        chapter, chap_num = {}, getGematria(holder.group(1))
        seif, seif_num = None, -1

    elif holder(re.search(u'@11\(([\u05d0-\u05ea]{1,2})\)', line)):
        if seif is not None:
            chapter[seif_num - 1] = seif
        seif, seif_num = [], getGematria(holder.group(1))

    if re.match(u'^@11', line):
        fixed_line = re.sub(u'@11\(([\u05d0-\u05ea]{1,2})\)', u'@11', line)
        fixed_line = re.sub(u'@11\s?([^@]+)@33', u'<b>\g<1></b>', fixed_line)
        fixed_line = re.sub(u'\s?\(#\)\s?', u' \u270d', fixed_line)
        fixed_line = re.sub(u'@\d{2}', u'', fixed_line)
        fixed_line = re.sub(u' {2,}', u' ', fixed_line)
        fixed_line = re.sub(u'^ +| +$', u'', fixed_line)
        seif.append(fixed_line)
chapter[seif_num - 1] = seif
mishbetzot.append(convert_dict_to_array(chapter, default_value=list))

with codecs.open(u'./part_3/‏‏פרי מגדים משבצות זהב שולחן ערוך יורה דעה חלק ג.txt', 'r', 'utf-8') as fp:
    my_lines = fp.readlines()

for line in my_lines:
    if holder(re.search(u'@22([\u05d0-\u05ea]{3})', line)):
        chapter, chap_num = [], getGematria(holder.group(1))

    elif re.match(u'^@11', line):
        fixed_line = re.sub(u'^@11[^@]+@33\s*', u'', line)
        fixed_line = re.sub(u'^[^\s]+', u'<b>\g<0></b>', fixed_line)
        fixed_line = re.sub(u' {2,}', u' ', fixed_line)
        fixed_line = re.sub(u'^ +| +$', u'', fixed_line)
        chapter.append([fixed_line])
mishbetzot.append(chapter)

links = []
tur_chapters = Ref("Turei Zahav on Shulchan Arukh, Yoreh De'ah").all_subrefs()
for c_num, (t_chap, pri_chap) in enumerate(zip(tur_chapters, mishbetzot), 1):
    yd_ref = Ref(u"Shulchan Arukh, Yoreh De'ah {}".format(c_num))
    yd_linkset = yd_ref.linkset()
    t_seifim = t_chap.all_segment_refs()

    if not 0 <= len(t_seifim) - len(pri_chap) <= 1:
        print "Seif mismatch at chapter {}: {} in Tur, {} in Mishbetzot".format(c_num, len(t_seifim), len(pri_chap))
        continue

    for s_num, (t_seif, pri_seif) in enumerate(zip(t_seifim, pri_chap), 1):
        m_ref = u"Pri Megadim, Mishbezot Zahav on Yoreh De'ah {}:{}".format(c_num, s_num)
        links.append((t_seif.normal(), m_ref))
        refs_from = list(set([i.normal() for i in yd_linkset.refs_from(t_seif)]))  # clear duplicates
        if len(refs_from) > 1:
            print u'Multiple refs at {}'.format(t_seif.normal())
        links.append((refs_from[0], m_ref))

print "\n\nParsing Siftei Da'at"


def itag_repl(match):
    return u'<i data-commentator="Maharsha" data-order="{}"></i> '.format(getGematria(match.group(1)))


siftei = []
with codecs.open(u'./part_1/שולחן ערוך יורה דעה חלק א פרי מגדים שפתי דעת.txt', 'r', 'utf-8') as fp:
    my_lines = fp.readlines()

siman, seif = 0, 0
for line in my_lines:
    if holder(re.search(u'@00([\u05d0-\u05ea]{1,2})', line)):
        new_siman, seif = getGematria(holder.group(1)), 0
        if new_siman - siman != 1:
            print "Missing Siman! Jump from Siman {} to {}".format(siman, new_siman)
        siman = new_siman

    elif holder(re.search(u'@22([\u05d0-\u05ea]{1,2})', line)):
        new_seif = getGematria(holder.group(1))
        if new_seif - seif != 1:
            print "Siman {}: Jump from seif {} to {}".format(siman, seif, new_seif)
        seif = new_seif

is_opening, current_opening, opening_title, opening_list = False, None, None, []
del chapter, chap_num, seif_num, seif
chapter, seif = None, None
chap_num, seif_num = -1, -1

for line in my_lines:
    if is_opening:
        if re.search(u'^@55', line):
            opening_list.append({
                'title': opening_title,
                'text': current_opening,
                'type': 'opening'
            })
            is_opening, current_opening = False, None
        elif holder(re.search(u'^@77(.*)', line)):
            opening_title = holder.group(1)
        else:
            assert re.match(u'^@11', line) is not None
            fixed_line = re.sub(u'@11([^@]+)@33', u'<b>\g<1></b>', line)
            fixed_line = re.sub(u'@\d{2}', u'', fixed_line)
            fixed_line = clean_whitespace(fixed_line)
            current_opening.append(fixed_line)

    elif re.search(u'^@44', line):
        is_opening = True
        current_opening = []

    elif holder(re.search(u'@00([\u05d0-\u05ea]{1,2})', line)):
        if chapter is not None:
            if seif is not None:
                chapter[seif_num - 1] = seif
            siftei.append(convert_dict_to_array(chapter))
        chapter, chap_num = {}, getGematria(holder.group(1))
        seif, seif_num = None, -1

    elif holder(re.search(u'@22([\u05d0-\u05ea]{1,2})', line)):
        if seif is not None:
            chapter[seif_num - 1] = seif
        seif, seif_num = [], getGematria(holder.group(1))

    else:
        assert re.match(u'^@11', line) is not None
        fixed_line = re.sub(u'@11([^@]+)@33', u'<b>\g<1></b>', line)
        fixed_line = re.sub(u'\s?@66\[([\u05d0-\u05ea]{1,2})\]\s?', itag_repl, fixed_line)
        fixed_line = re.sub(u'\s?\(#\)\s?', u' \u270d', fixed_line)
        fixed_line = re.sub(u'@\d{2}', u'', fixed_line)
        fixed_line = clean_whitespace(fixed_line)
        seif.append(fixed_line)
chapter[seif_num - 1] = seif
siftei.append(convert_dict_to_array(chapter))

with codecs.open(u'./part_2/שפתי דעת פרי מגדים יורה דעה חלק ב מוכן.txt', 'r', 'utf-8') as fp:
    my_lines = fp.readlines()

seif_num = 0
is_opening = False
for line in my_lines:
    if is_opening:
        if re.search(u'@55', line):
            is_opening = False
    else:
        continue
    if holder(re.search(u'@00([\u05d0-\u05ea]{1,3})', line)):
        new_chap_num, seif_num = getGematria(holder.group(1)), 0
        if new_chap_num - chap_num != 1:
            print "Missing Siman! Jump from Siman {} to {}".format(chap_num, new_chap_num)
        chap_num = new_chap_num

    elif holder(re.search(u'@22([\u05d0-\u05ea]{1,2})', line)):
        new_seif_num = getGematria(holder.group(1))
        if new_seif_num - seif_num != 1:
            print "Siman {}: Jump from seif {} to {}".format(chap_num, seif_num, new_seif_num)
        seif_num = new_seif_num

    elif re.search(u'@44', line):
        is_opening = True
del seif_num

is_opening, current_opening, opening_title, opening_type = False, None, None, None
chapter, seif = None, None
chap_num, seif_num = -1, -1
sfek_sfeka, segment = False, None

for line in my_lines:
    if is_opening:
        if re.search(u'@55', line):
            opening_list.append({
                'title': opening_title,
                'text': current_opening,
                'type': opening_type
            })
            is_opening, current_opening = False, None
        elif holder(re.search(u'^@77(.*)', line)):
            opening_title = holder.group(1)

        else:
            assert re.match(u'^@(11|00)', line) is not None
            fixed_line = re.sub(u'@11([^@]+)@33', u'<b>\g<1></b>', line)
            fixed_line = re.sub(u'@\d{2}', u'', fixed_line)
            fixed_line = clean_whitespace(fixed_line)
            current_opening.append(fixed_line)

    elif holder(re.search(u'@4([45])', line)):
        is_opening, current_opening = True, []
        if holder.group(1) == '4':
            opening_type = 'opening'
        else:
            opening_type = 'appendix'
        current_opening = []

    elif re.search(u'@41', line):
        sfek_sfeka = True
        segment = []

    elif holder(re.search(u'@00([\u05d0-\u05ea]{1,3})', line)):
        if sfek_sfeka:
            if seif and segment:
                seif.append(u'<br>'.join(segment))
            sfek_sfeka = False
        if chapter is not None:
            if seif is not None:
                chapter[seif_num - 1] = seif
            siftei.append(convert_dict_to_array(chapter))
        chapter, chap_num = {}, getGematria(holder.group(1))
        seif, seif_num = None, -1

    elif holder(re.search(u'@22([\u05d0-\u05ea]{1,2})', line)):
        if sfek_sfeka and segment:
            seif.append(u'<br>'.join(segment))
            segment = []
        if seif is not None:
            chapter[seif_num - 1] = seif
        seif, seif_num = [], getGematria(holder.group(1))

    else:
        if sfek_sfeka:
            if holder(re.search(u'^@12(.*)', line)):
                if segment:
                    seif.append(u'<br>'.join(segment))
                    segment = []
                segment.append(u'{})'.format(holder.group(1)))
            else:
                assert re.match(u'^@11', line) is not None
                fixed_line = re.sub(u'@11([^@]+)@33', u'<b>\g<1></b>', line)
                fixed_line = re.sub(u'\s?\(#\)\s?', u' \u270d', fixed_line)
                fixed_line = re.sub(u'@\d{2}', u'', fixed_line)
                fixed_line = clean_whitespace(fixed_line)
                segment.append(fixed_line)

        else:
            assert re.match(u'^@11', line) is not None
            fixed_line = re.sub(u'@11([^@]+)@33', u'<b>\g<1></b>', line)
            fixed_line = re.sub(u'@77([^@]+)@88', u'<big>\g<1></big>', fixed_line)
            fixed_line = re.sub(u'\s?\(#\)\s?', u' \u270d', fixed_line)
            fixed_line = re.sub(u'@\d{2}', u'', fixed_line)
            fixed_line = clean_whitespace(fixed_line)
            seif.append(fixed_line)
chapter[seif_num - 1] = seif
siftei.append(convert_dict_to_array(chapter))

# ja_to_xml(siftei, ['Siman', 'Seif', 'Paragraph'])
for o in opening_list:
    print o['title'], o['type']
