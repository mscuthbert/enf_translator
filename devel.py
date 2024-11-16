from collections import defaultdict, Counter
import enf_read

enf = enf_read.ENFReader('/Users/cuthbert/Dropbox (MIT)/Documents/trecento/EMMSAP/Erin Returns/enf Files/GloriaAnon27.enf')

def vert_debug():
    # for t, d in enf.events_by_type.items():
    #     print(f'\n********\nTYPE: {t}\n')
    #     print(d)
    # print(list(enf.events_by_type))
    print(len(enf.events_by_type['note']))
    print(len(enf.events_by_type['rest']))
    print(len(enf.events_by_type['vert']))

    last_rare = False
    index = -1
    for t, n in enf.events:
        # print(t, end=' ')
        if t == 'vert':
            print(n.first_index, n.first_indexb, n.measure_index, n.second_index, n.third_index)
        elif t == 'note':
            index += 1
            # print(index, n.as_m21_pitch())

def stem_debug():
    counter_by_event_type('stem')
    index = -1
    last_is_relevant = False
    for t, n in enf.events:
        # print(t, end=' ')
        if t == 'stem':
            index += 1
            assert isinstance(n, enf_read.Stem)
            print(index, end=' ')
            print(n.d13, end=' ')
        elif t == 'note':
            print(n.as_m21_pitch())

def list_events():
    for t, n in enf.events:
        print(t, end=' ')

def counter_by_event_type(event_type):
    dd = defaultdict(Counter)
    for n in enf.events_by_type[event_type]:
        for i in range(len(n.data)):
            dd[i][n.data[i]] += 1
    for i in sorted(dd):
        print(i, dict(dd[i]))


if __name__ == '__main__':
    print(enf.filename)
    print(enf.enf_header)
    print(len(enf.data))

    list_events()
    stem_debug()

    print(enf_read.read_bytes_as_signed_number(b'\xFF\xFF\x00'))
