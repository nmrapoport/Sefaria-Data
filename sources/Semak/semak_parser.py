# encoding=utf-8

import codecs
import re
from data_utilities.util import ja_to_xml, multiple_replace, traverse_ja, file_to_ja_g
from data_utilities.util import getGematria

from collections import OrderedDict
from sources.functions import post_text, post_index, post_link
from sefaria.model import *
from sefaria.datatype.jagged_array import JaggedArray


def map_semak_day(filename): # alt struct according to days. (not sure how alt struct works
    pass


def parse_semak(filename):

    def cleaner(my_text):
        replace_dict = {u'@11(.*?)@12': ur'<b>\1</b>', u'@33(.*?)@34': ur'<b>\1</b>', u'@33(.*?)@34': ur'<b>\1</b>', u'@66(.*?)@67': ur'\1'}#, u'@55[\u05d0-\u05ea]{1,3}' : u'<i-tags = >'}
        new = []
        for line in my_text:
            line = multiple_replace(line,replace_dict,using_regex=True)
            new.append(line)
        return new


    regs = [ur'@22(?P<gim>[\u05d0-\u05ea]{1,3})'] #, u'@(11|23|33)(?P<gim>)']
    with codecs.open(filename, 'r', 'utf-8') as fp:
        lines = fp.readlines()
    starting = None
    # check if we got to the end of the legend and change to started
    # clean all lines of days start with @00
    cleaned = []
    letter_section = []
    for line_num, line in enumerate(lines):
        if line == u'\n':
            starting = line_num + 1
            break
    for line_num, line in enumerate(lines[starting:]):
        if not re.search(u'@00', line) and not line.isspace():
            if re.search(u'@22', line):
                line = re.split(u'(@22[\u05d0-\u05ea]{1,3})', line)
                if isinstance(line, basestring):
                    cleaned.append(line)
                else:
                    [cleaned.append(st) for st in line if st]
            else:
                cleaned.append(line)
    try:
        smk_ja = file_to_ja_g(2, cleaned, regs, cleaner, gimatria=True,  grab_all=[False, True, True], group_name = 'gim').array() #group_name = 'gim',
    except AttributeError:
        print 'there are more regs then levels...'

    ja_to_xml(smk_ja, ['letter', 'segments'], 'smk.xml')

    return smk_ja

#todo:
# i would want to devide the Raph according to simanim as well and not according to pages,
# once one has the mapping of simanim to dapim this is possible
def parse_Raph(filename):
    def cleaner(my_text):
        replace_dict = {u'@(?:11|77)[\u05d0-\u05ea]{0,3}': u'', u'@(33|22)': u''}#{u'@11(.*?)@12': ur'<b>\1</b>', u'@33(.*?)@34': ur'<b>\1</b>', u'@33(.*?)@34': ur'<b>\1</b>', u'@66(.*?)@67': ur'\1'}
        new = []
        for line in my_text:
            line = multiple_replace(line,replace_dict,using_regex=True)
            new.append(line)
        return new

    regs = [ur'@77(?P<gim>[\u05d0-\u05ea]{0,3})', ur'@11(?P<gim>[\u05d0-\u05ea]{1,3})']  # (?P<gim>[\u05d0-\u05ea]{1,3})
    with codecs.open(filename, 'r', 'utf-8') as fp:
        lines = fp.readlines()
    starting = None
    # check if we got to the end of the legend and change to started
    # clean all lines of days start with @00
    cleaned = []
    letter_section = []
    for line_num, line in enumerate(lines):
        if line == u'\n':
            starting = line_num + 1
            break
    for line_num, line in enumerate(lines[starting:]):
        if not re.search(u'@00', line) and not line.isspace():
            # if re.search(u'@(77|11)', line):
            line = re.split(u'(@(?:77|11)[\u05d0-\u05ea]{0,3})', line)
            if isinstance(line, basestring):
                cleaned.append(line)
            else:
                [cleaned.append(st.strip()) for st in line if st]#(st and not re.search(u'@(77)', st))]
            # else:
            #     cleaned.append(line)
    try:
        ja = file_to_ja_g(3, cleaned, regs, cleaner, gimatria=True,  grab_all=[False, False, True], group_name='gim').array()
    except AttributeError:
        print 'there are more regs then levels...'

    ja_to_xml(ja, ['page', 'letter', 'segments'], 'raph.xml')

    return ja

def map_semak_page_siman(smk_ja):
    '''

    :param smk_ja: smk ja parsed according to simanim @22
    :return: simanim to pages (each siman on whitch page in the semak is it presented)
    '''
    siman_page = OrderedDict()
    for seg in traverse_ja(smk_ja):
        for i, page in enumerate(re.finditer(u'@77', seg['data'])):
            print i, page.span(), seg['indices']

def link_semak_raph(smk_ja, raph_ja):
    #if segment in smak_ja has a @55[\u05d0-\u05ea]{0,3} extract the letter and match it to the segment in the ja_raph
    #by running on the ja_raph segments
    smk_raph = []
    raph_letter = []
    for seg in traverse_ja(smk_ja):
        if re.search(u'@55[\u05d0-\u05ea]{0,3}', seg['data']):
            for letter in re.findall(u'@55([\u05d0-\u05ea]{0,3})', seg['data']):
                # smk_raph.append([seg['indices'][:], letter])
                smk_raph.append([letter, seg['indices']])
    last = [-1, -1]
    for seg in traverse_ja(raph_ja):
        if seg['indices'][0:2] == last[0:2]:
            continue
        else:
            raph_letter.append(seg)
        last = seg['indices']

    problem_count = 0
    for smk, raph in zip(smk_raph, raph_letter):
        if getGematria(smk[0]) == (raph['indices'][1]+1):
            print getGematria(smk[0]), raph['indices'][1]+1, \
                [item+1 for item in smk[1]], [item +1 for item in raph['indices']]
        else:
            problem_count +=1
            print 'problem:' , getGematria(smk[0]), raph['indices'][1]+1,\
                [item+1 for item in smk[1]], [item +1 for item in raph['indices']]
    print problem_count

if __name__ == "__main__":
    ja_smk = parse_semak('Semak.txt')
    map_semak_page_siman(ja_smk)
    # ja_raph = parse_Raph('Raph_on_Semak.txt')
    # link_semak_raph(ja_smk, ja_raph)
