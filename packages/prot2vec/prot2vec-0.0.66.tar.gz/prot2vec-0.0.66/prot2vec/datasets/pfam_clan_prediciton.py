from prot2vec.datasets.amino_acid import line_to_seqtok
import numpy as np
import pandas as pd
from pathlib import Path


def vect_batch(batch_x, batch_y):
    x = np.concatenate(batch_x, axis=0)
    y = np.array(batch_y, dtype='int32')

    return x, y


def ds_iter_clan(src_file, all_clans_file, seq_len, batch_size):
    all_clans = pd.read_csv(all_clans_file, delimiter='\t')['clan_id'].tolist()
    all_clans.sort()
    clans_map = {all_clans[i]: i for i in range(len(all_clans))}

    batch_x = []
    batch_y = []
    while True:
        with open(src_file, "r", encoding="utf-8") as fr:
            fr.readline()
            for line in fr:
                _, clan_id, seq = line[:-1].split('\t')

                if clan_id not in clans_map or len(seq) < 1:
                    continue

                clan_id = clans_map[clan_id]
                seq_in = line_to_seqtok(seq, seq_len)

                batch_x.append(seq_in)
                batch_y.append(clan_id)

                if len(batch_x) >= batch_size:
                    assert len(batch_x) == len(batch_y)
                    v_batch = vect_batch(batch_x, batch_y)
                    yield v_batch
                    del batch_x[:], batch_y[:]


if __name__ == '__main__':
    ROOT = Path(r'C:\DATA\ML-Data\BioML\datasets\Prot2Vec_dataset_2022-06')

    gen = ds_iter_clan(ROOT /'clan_prediction_shuffled.tsv', ROOT / 'all_clans.tsv', 60, 4096)

    while True:
        a = next(gen)
        print()
