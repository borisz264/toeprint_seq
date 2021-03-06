import matplotlib.pyplot as plt
from rna import rna

newcolors6 = [ "#A67D33", "#B15DCA", "#498B78", "#ED9121"]
celtics = '#00611C'
colors4 = ['#E79E34', '#831A0A', '#2800F5', '#447E23']
colors5 = ['#E79E34', '#831A0A', '#2800F5', '#447E23', '#000000']
colors6 = ["#A67D33", "#B15DCA", "#498B78", "#6E7AAE", "#66A140", "#B4527C"]
colors7 = ["#A67D33", "#498B78", "#6E7AAE", "#66A140", "#B4527C", "#C14D3B", "#B15DCA"]
colors8 = ["#A67D33", "#498B78", "#6E7AAE", "yellow", "#B4527C", "#C14D3B", "#B15DCA", "black"]
green8 = [ "#99FF99", "#66FF66", "#33FF33", "#00FF00", "#00CC00", "#009900", "#006600", "#003300"] 
colors_def = ['b','g','r','c','m','k']
colors_red_to_black_5 = ['#F80000', '#C80000', '#980000', '#680000', '#380000']
colors_red_to_black_6 = ['#F80000', '#C80000', '#980000', '#680000', '#380000', '#080000']
spearmint = '#19B271'
Little_green = '#00B164'
Little_pink = '#FF1493'
khaki = '#F0E68C'
cyan = '#00FFFF'
steel_blue = '#63B8FF'
blue_steel = steel_blue
bacon = '#C65D57'
crimson = '#DC143C'
deepskyblue = '#00B2EE'
mint = '#00CD66'
olive = '#8E8E38'
coco_grey = '#C0C0C0'
dodo_grey = '#D0D0D0'
eo_grey = '#E0E0E0'
fofo_grey = '#F0F0F0'
gunmetal = '#2C3539'
black='#000000'
#generate jet
cm = plt.cm
jet4 = [cm.jet(i/3.) for i in range(4)]
jet5 = [cm.jet(i/4.) for i in range(5)]
jet6 = [cm.jet(i/5.) for i in range(6)]
jet7 = [cm.jet(i/6.) for i in range(7)]
jet8 = [cm.jet(i/7.) for i in range(8)]
jet9 = [cm.jet(i/8.) for i in range(9)]

primary_motif = '#FF0000'
secondary_motif = '#FF9912'
tertiary_motif = '#009E0B'
quaternary_motif = '#C979A7'
motif5 = '#000000'

other_significant = '#6600FF'
background_motif = coco_grey

two_ugus = primary_motif
one_ugu = secondary_motif

ygcu_motif = primary_motif
ygcc_motif = secondary_motif

true_positive = spearmint
false_positive = 'magenta'
true_negative = background_motif


ordered_colors = [primary_motif, secondary_motif, tertiary_motif, quaternary_motif, other_significant, background_motif]

def protein_colors(sequence_mapping, protein, significant):
    if 'ITIVE' in protein.upper():
        if 'FALSEPOSITIVE' in protein.upper():
            return false_positive
        if 'TRUEPOSITIVE' in protein.upper():
            return true_positive
        if 'TRUENEGATIVE' in protein.upper():
            return true_negative
        raise ValueError
    if 'EIF4G' in protein.upper():
        return eIF4G_colors(sequence_mapping.full_sequence, significant)
    return spearmint

def eIF4G_colors(sequence, significant):
    if 'TTTTTTT' in sequence:
        return primary_motif
    elif 'TTTTTT' in sequence:
        return secondary_motif
    elif 'GGGGG' in sequence:
        return tertiary_motif
    elif significant:
        return other_significant
    return background_motif

def eIF4G2_colors(kmer, significant):
    if 'GGAGTC' in kmer:
        return primary_motif
    elif 'TTTTTT' in kmer:
        return secondary_motif
    elif 'GGCACCC' in kmer:
        return tertiary_motif
    elif 'GGGGG' in kmer:
        return quaternary_motif
    elif 'GGGATCG' in kmer:
        return motif5
    elif significant:
        return other_significant
    return background_motif


def test_colors(kmer, significant):
    if kmer[0] == 'A':
        return primary_motif
    if kmer[0] == 'C':
        return secondary_motif
    if kmer[0] == 'G':
        return other_significant
    if kmer[0] == 'T':
        return background_motif


def ERSP_colors(kmer, significant):
    kmer = rna(kmer)
    if 'GGUG' in kmer:
        return primary_motif
    elif 'GGU' in kmer:
        return secondary_motif
    elif significant:
        return other_significant
    return background_motif


def YGCY(seq):
    assert isinstance(seq, str)
    assert seq.upper() == seq
    if len(seq) < 4:
        return 
    seq = rna(seq)
    for starti in range(0, len(seq) - 3):
        if seq[starti] in 'CU': # Y
            if seq[starti+1:starti+3] == 'GC':
                if seq[starti+3] in 'CU':
                    return True
    return False


def YGCC(seq):
    assert isinstance(seq, str)
    assert seq.upper() == seq
    if len(seq) < 4:
        return 
    seq = rna(seq)
    for starti in range(0, len(seq) - 3):
        if seq[starti] in 'CU': # Y
            if seq[starti + 1:starti + 3] == 'GC':
                if seq[starti + 3] == 'C':
                    return True
    return False


def YGCU(seq):
    assert isinstance(seq, str)
    assert seq.upper() == seq
    if len(seq) < 4:
        return 
    seq = rna(seq)
    for starti in range(0, len(seq) - 3):
        if seq[starti] in 'CU': # Y
            if seq[starti+1:starti+3] == 'GC':
                if seq[starti+3] == 'U':
                    return True
    return False


def mbnl_colors(kmer, significant):
    if YGCU(kmer):
        return ygcu_motif
    if YGCC(kmer):
        return ygcc_motif
    if significant:
        return other_significant
    return background_motif
    

def fox_colors(kmer, significant):
    if kmer.count('GCATG') or kmer.count('GCAUG'):
        return primary_motif
    if kmer.count('GCACG'):
        return secondary_motif
    if significant:
        return other_significant
    return background_motif
