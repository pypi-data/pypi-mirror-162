# TODO: help doc / c++
import numpy as np
import chromox.protein_descriptors.table as Table


methods = [
    ('BLOSUM', 'BLOSUM'),
    ('CRUCIANI', 'PP'),
    ('FASGAI', 'F'),
    ('KIDERA', 'KF'),
    ('MSWHIM', 'MSWHIM'),
    ('PCP_DESCRIPTORS', 'E'),
    ('PROTFP', 'ProtFP'),
    ('SNEATH', 'SV'),
    ('ST_SCALES', 'ST'),
    ('T_SCALES', 'T'),
    ('VHSE', 'VHSE'),
    ('Z_SCALES', 'Z')
]


def descriptor(seq, verbose=False, return_dict=False):
    encoder = {aa: i for i, aa in enumerate(Table.AA)}
    seq_enc = np.zeros(len(seq), dtype=int)
    for i, aa in enumerate(seq):
        seq_enc[i] = encoder.get(aa, encoder["X"])

    if return_dict:
        descriptors = {}
    else:
        descriptors = []
    for method, sub_method in methods:
        method_dict = getattr(Table, method)
        for i in range(len(method_dict)):
            sub_method_ = '%s%d' % (sub_method, i + 1)
            table_method = [method_dict[sub_method_].get(aa, 0.0) for aa in Table.AA]
            descriptor = np.sum(np.take(table_method, seq_enc))/len(seq_enc)
            if verbose:
                print('%20s -%10s:   %10f' % (method, sub_method_, descriptor))
            if return_dict:
                descriptors[sub_method_] = descriptor
            else:
                descriptors.append(descriptor)
    return descriptors


if __name__ == '__main__':
    AA_seq = 'EXA'
    desc = descriptor(AA_seq, verbose=False, return_dict=False)
    print('done')