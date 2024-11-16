'''
enf_read: read a SmartScore 64 ENF notation file
'''
from collections import defaultdict
from enum import Enum

import music21


class Accidental(Enum):
    NONE = 0
    NATURAL = 8
    SHARP = 128
    FLAT = 32
    # DOUBLE_SHARP = 256
    # DOUBLE_FLAT = 4
    # TRIPLE_SHARP = 5
    # TRIPLE_FLAT = 6

def read_bytes_as_number(b_in: bytes) -> int:
    out = 0
    for b in b_in:
        out = (out << 8) + b
    return out

def read_bytes_as_signed_number(b_in: bytes) -> int:
    unsigned = read_bytes_as_number(b_in)
    max_val = 1 << (len(b_in) * 8)
    if unsigned > max_val // 2:
        signed = max_val - unsigned
        signed *= -1
    else:
        signed = unsigned
    return signed

class ENFReader:
    def __init__(self, filename='Sample_ENF_Hack.enf'):
        self.filename = filename
        self.f = open(filename, 'rb')
        self.enf_header = self.f.read(4)
        if self.enf_header != b'ENF ':
            raise ValueError('Not an ENF file')
        self.dummy_length_maybe = self.f.read(2)
        self.data = self.f.read()
        self.f.close()
        self.events = self.split_events()
        self.events_by_type = self.split_events_by_type()

    def split_events(self):
        events = []
        i = 0
        while i < len(self.data):
            e_type = self.data[i:i+4].decode('ascii')
            e_len = read_bytes_as_number(self.data[i+4:i+6])
            # print(f'{i=}, {e_type=}, {e_len=}')
            if e_type not in types_to_object:
                raise ValueError(f'Unknown event type: {e_type}')
            e_obj = types_to_object[e_type](self.data[i+6:i+e_len])
            events.append((e_type, e_obj))
            i += e_len
        return events

    def split_events_by_type(self):
        events_by_type = defaultdict(list)
        for e_type, e_data in self.events:
            events_by_type[e_type].append(e_data)
        return events_by_type

class ENFObject:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

class Score(ENFObject):
    pass

class Part(ENFObject):
    pass

class Measure(ENFObject):
    pass

class Staff(ENFObject):
    pass

class Barline(ENFObject):
    pass

class System(ENFObject):
    pass

class TimeSignature(ENFObject):
    r'''
    0 <TimeSignature> b'\x00\x00\x01.\x00\x00\x00\x06\x00\x00\x00\x08\x01\x00'
    1 <TimeSignature> b'\x00\x00\x01\xc5\x00\x00\x00\x06\x00\x00\x00\x08\x01\x00'
    2 <TimeSignature> b'\x00\x00\x19\x85\x00\x00\x00\t\x00\x00\x00\x08\x01\x00'
    3 <TimeSignature> b'\x00\x00\x1b \x00\x00\x00\t\x00\x00\x00\x08\x01\x00'
    4 <TimeSignature> b'\x00\x00\x1dz\x00\x00\x00\x02\x00\x00\x00\x04\x01\x00'
    5 <TimeSignature> b'\x00\x00\x1e\xd4\x00\x00\x00\x06\x00\x00\x00\x08\x01\x00'
    6 <TimeSignature> b'\x00\x00 \xd6\x00\x00\x00\x03\x00\x00\x00\x04\x01\x00'
    7 <TimeSignature> b'\x00\x00"\xd2\x00\x00\x00\x06\x00\x00\x00\x08\x01\x00'
    '''
    def __init__(self, data):
        super().__init__(data)
        self.index1 = read_bytes_as_number(data[0:4])
        self.numerator = read_bytes_as_number(data[4:8])
        self.denominator = read_bytes_as_number(data[8:12])
        self.data1 = data[12]  # always 1 so far
        self.data2 = data[13]

    def as_m21(self) -> music21.meter.TimeSignature:
        return music21.meter.TimeSignature(f'{self.numerator}/{self.denominator}')

class KeySignature(ENFObject):
    pass

class Clef(ENFObject):
    pass

class Metadata(ENFObject):
    pass

class Vert(ENFObject):
    '''
    Something about duration?
    '''
    def __init__(self, data):
        super().__init__(data)
        self.first_index = read_bytes_as_number(data[0:2])  # position?
        self.first_indexb = read_bytes_as_number(data[2:4])  # position?
        # self.data4 = data[4]  # always 0 so far adding to measure index
        # self.data5 = data[5]  # always 0 so far adding to measure index
        self.measure_index = read_bytes_as_number(data[4:8])  # measure index?
        self.second_index = read_bytes_as_number(data[8:12])  # another index? 8,9 always 0
        self.data12 = data[12]  # always 0 so far
        self.third_index = read_bytes_as_number(data[13:17])
        self.data17 = data[17]  # always 0 so far
        self.data18 = data[18]  # always 0 so far
        self.position_of_something_rare = read_bytes_as_number(data[19:21])  # usually 0
        self.data21 = data[21]  # always 0 so far
        self.data22 = data[22]  # always 0 so far
        self.data23 = data[23]  # always 0 so far
        self.data24 = data[24]  # always 0 so far
        self.data25 = data[25]  # always 0 so far
        self.data26 = data[26]  # always 0 so far
        self.data27 = data[27]  # always 0 so far
        self.data28 = data[28]  # always 0 so far
        self.data29 = data[29]  # always 0 so far
        self.data30 = data[30]  # always 0 so far
        self.data31 = data[31]  # always 0 so far
        self.data32 = data[32]  # always 0 so far
        self.last_val = data[33]  # usually 0; values 1,2,3,4,5 also seen, logarithmically declining.


class Stem(ENFObject):
    '''
    Stem encompasses not just the stem but duration information.
    '''
    def __init__(self, data):
        super().__init__(data)
        self.index1 = read_bytes_as_number(data[0:4])
        self.index2 = read_bytes_as_number(data[4:8])
        self.d8 = data[8]  # ? always 0 so far
        self.d9 = data[9]  # ? always 255 so far
        self.d10 = data[10]  # ? always 0 so far
        self.type_num = data[11]  # 4=quarter, 3=half, 2=whole, 1=breve?
        self.num_dots = data[12]
        self.d13 = data[13]
        self.d14 = data[14]
        self.d15 = data[15]  # ? always 50 so far
        self.d16 = data[16]  # ? always 0 so far
        self.d17 = data[17]  # ? always 255 so far
        self.d18 = data[18]  # ? always 255 so far
        self.d19_28 = data[19:29]  # ? always 0 so far
        self.d29 = data[29]  # ? always 15 so far
        self.d30 = data[30]  # ? always 50 so far
        self.d31 = data[31]  # ? always 30 so far
        self.d32_33 = data[32:34]  # ? always 0 so far
        self.stem_direction1 = data[34]  # 0 = up or none, 255 = down
        self.stem_direction2 = data[35]  # 0 = up or none, 255 = down
        # signed stem length
        self.stem_length = read_bytes_as_signed_number(data[36:38])
        self.d38 = data[38]  # ? always 1 so far
        self.d39 = data[39]  # ? always 0 so far
        self.d40 = data[40]  # ? always 1 so far
        self.n_index1 = read_bytes_as_number(data[41:45])
        self.d45 = data[45]  # ? always 0 so far
        self.d46 = data[46]  # ? always 0 so far


class Beam(ENFObject):
    pass

class Tie(ENFObject):
    pass

class Slur(ENFObject):
    pass

class Pedal(ENFObject):
    pass

class Text(ENFObject):
    pass

class Control(ENFObject):
    pass

class Rest(ENFObject):
    pass

class Dynamic(ENFObject):
    pass

class Repeat(ENFObject):
    pass

class Note(ENFObject):
    def __init__(self, data):
        super().__init__(data)
        self.index1 = read_bytes_as_number(data[0:4])
        self.index2 = read_bytes_as_number(data[4:8])
        self.d8 = data[8]  # ? always 0 so far
        self.d9 = data[9]  # ? always 8 so far
        self.lowest_line_offset = read_bytes_as_number(data[10:12]) - 0x8000
        self.accidental = Accidental(data[12])
        self.diatonic_note_num = data[13] - 6  # subtract 6 to keep consistent with music21
        self.ks_alter = read_bytes_as_signed_number(data[14:15])
        self.midi_number = data[15]
        self.data5 = read_bytes_as_number(data[16:18])  # always 4 so far
        self.data6a = read_bytes_as_number(data[18:20])  # maybe part of tie_stop_index? always 0
        self.tie_stop_index = read_bytes_as_number(data[20:22])
        self.data6c = read_bytes_as_number(data[22:24])  # maybe part of tie_start_index? always 0
        self.tie_start_index = read_bytes_as_number(data[24:26])
        self.data6e = read_bytes_as_number(data[26:28])  # always 0
        self.data6f = read_bytes_as_number(data[28:30])  # always 0
        self.data6g = read_bytes_as_number(data[30:32])  # always 0
        self.data6h = read_bytes_as_number(data[32:34])  # always 0
        self.data7 = data[34] # always 85 (velocity?)
        self.data7a = data[35] # always 0
        # self.data7 = read_bytes_as_number(data[34:36])
        self.data8 = read_bytes_as_number(data[36:38])  # always 0
        self.left = read_bytes_as_number(data[38:42])
        self.right = read_bytes_as_number(data[42:46])
        self.top = read_bytes_as_number(data[46:50])
        self.bottom = read_bytes_as_number(data[50:54])

    def as_m21_pitch(self) -> music21.pitch.Pitch:
        p = music21.pitch.Pitch()
        p.diatonicNoteNum = self.diatonic_note_num
        acc_alter = self.midi_number - p.midi
        p.accidental = music21.pitch.Accidental(acc_alter)
        return p

types_to_object = {
    'scor': Score,
    'part': Part,
    'staf': Staff,
    'syst': System,
    'meas': Measure,
    'brln': Barline,
    'clef': Clef,
    'meta': Metadata,
    'tmsg': TimeSignature,
    'kysg': KeySignature,
    'note': Note,
    'rest': Rest,
    'vert': Vert,
    'stem': Stem,
    'bea-': Beam,
    'tie-': Tie,
    'slu-': Slur,
    'slu[': Slur,
    'slu]': Slur,
    'ped-': Pedal,
    'ped^': Pedal,
    'text': Text,
    'ctrl': Control,
    'dyns': Dynamic,
    'repe': Repeat,
    'guch': ENFObject,  # unknown
}

