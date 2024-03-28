import argparse
import logging
import os
import pickle

import matplotlib.pyplot as plt
import japanize_matplotlib
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.decomposition import PCA
from typing import Dict, List, Tuple

from sppmisvd.util import load_pickle


def get_vectors_eachslice(id2word: Dict[int, str],
                          word2id: Dict[str, int],
                          target_words: List[str],
                          WV: List[List[float]],
                          get_neighbors: bool = False,
                          num_neighbors: int = 3,
                          suffix: str = None) -> Tuple[Dict[str, List[float]], Dict[str, List[str]]]:
    """ get target/neighbors vector
    :param id2word: Dict[int, str], id -> word dict
    :param word2id: Dict[str, int], word -> id dict
    :param target_words: List[str], target words
    :param WV: List[List[float]], vector matrix
    :param get_neighbors: bool, obtain neighbor words or not
    :param num_neighbors: int, number of neighbors
    :param suffix: str, add suffix (_i) or not (for multiple timeslices)

    :return:
     - word2vec: Dict[str, List[float]], word -> vec dict
     - word2neighbors: Dict[str, List[str]], word -> neighbors dict
    """
    word2vec = {}
    word2neighbors = {}

    for target_word in target_words:
        target_vec = WV[word2id[target_word]]
        target_word = target_word if suffix is None else f"{target_word}_{suffix}"
        word2vec[target_word] = target_vec
        word2neighbors[target_word] = []
        if get_neighbors:
            logging.debug(f"[get_neighbors] get neighbors of {target_word}")
            pair_dists = cdist(np.reshape(target_vec, [1, -1]), WV)[0]
            #for neighbor_id in np.argsort(pair_dists)[1:num_neighbors + 1]:
            for neighbor_id in np.argsort(pair_dists)[1:]:
                neighbor_word = id2word[neighbor_id]
                if neighbor_word in set(target_words):
                    continue
                neighbor_vec = WV[neighbor_id]
                neighbor_word = neighbor_word if suffix is None else f"{neighbor_word}_{suffix}"
                word2vec[neighbor_word] = neighbor_vec
                word2neighbors[target_word].append(neighbor_word)
                logging.debug(f"[get_neighbors]   - neighbor: {neighbor_word}, dist: {pair_dists[neighbor_id]}")
                if len(word2neighbors[target_word]) >= num_neighbors:
                    break
            logging.debug(f"[get_neighbors] - w2v: {len(word2vec)} items")
            logging.debug(f"[get_neighbors] - w2n: {word2neighbors}")

    return word2vec, word2neighbors


def get_vectors_allslices(id2word: Dict[int, str],
                          word2id: Dict[str, int],
                          target_words: List[str],
                          WV: List[List[float]],
                          T: int,
                          get_neighbors: bool = False,
                          num_neighbors: int = 3) -> Tuple[Dict[str, List[float]], Dict[str, List[str]]]:
    """ get target/neighbors vector allslices
    :param id2word: Dict[int, str], id -> word dict
    :param word2id: Dict[str, int], word -> id dict
    :param target_words: List[str], target words
    :param WV: List[List[float]], vector matrix
    :param T: int, timeslices
    :param get_neighbors: bool, obtain neighbor words or not
    :param num_neighbors: int, number of neighbors

    :return:
     - word2vec: Dict[str, List[float]], word -> vec dict
     - word2neighbors: Dict[str, List[str]], word -> neighbors dict
    """
    word2vec = {}
    word2neighbors = {}
    for curr_time in range(T):
        word2vec_curr, word2neighbors_curr = get_vectors_eachslice(id2word, word2id,
                                                                   target_words,
                                                                   WV[curr_time],
                                                                   get_neighbors=get_neighbors,
                                                                   num_neighbors=num_neighbors,
                                                                   suffix=curr_time)
        logging.debug(f" - curr_time: {curr_time}")
        logging.debug(f"   - w2v: {len(word2vec_curr)} items")
        logging.debug(f"   - w2n: {len(word2neighbors_curr)} items")
        word2vec.update(word2vec_curr)
        word2neighbors.update(word2neighbors_curr)
        logging.debug(f"   - w2v(updated): {len(word2vec)} items")
        logging.debug(f"   - w2n(updated): {len(word2neighbors)} items")

    return word2vec, word2neighbors


def plot_2d(target_words: List[str],
            word2vec: Dict[str, List[float]],
            word2neighbors: Dict[str, List[str]],
            output: str) -> None:
    """ plot into 2d graph
    :param target_words: List[str], target words
    :param T: int, timeslices
    :param word2vec: Dict[str, List[float]], word -> vec dict
    :param word2neighbors: Dict[str, List[str]], word -> neighbors dict
    :param output: str, output file name
    """
    vecid2vec = []
    word2vecid = {}
    vecid = 0
    for word, vec in word2vec.items():
        vecid2vec.append(vec)
        word2vecid[word] = vecid
        vecid += 1
    
    vecid2vec = np.array(vecid2vec)
    if len(vecid2vec) < 2:
        logging.info(f"[plot_2d] {target_words} has just 1 vector, cannot plot")
        return
    logging.debug(f"[plot_2d] vecid2vec: {vecid2vec.shape}")
    vecid2vec_2d = PCA(n_components=2).fit_transform(vecid2vec)
    logging.debug(f"[plot_2d] vecid2vec_2d: {vecid2vec_2d.shape}")

    vecs_target = []
    vecs_neighbor = []
    vocab = set(word2neighbors.keys())
    logging.debug(f"[plot_2d] vocab: {vocab}")
    for word, vecid in word2vecid.items():
        if word in vocab:
            vecs_target.append(vecid2vec_2d[vecid])
        else:
            vecs_neighbor.append(vecid2vec_2d[vecid])
    vecs_target = np.array(vecs_target)
    vecs_neighbor = np.array(vecs_neighbor)
    logging.debug(f"[plot_2d] vecs_target: {vecs_target.shape}")
    logging.debug(f"[plot_2d] vecs_neighbor: {vecs_neighbor.shape}")
    plt.scatter(vecs_target[:, 0], vecs_target[:, 1], marker="D")
    if len(vecs_neighbor) > 0:
        plt.scatter(vecs_neighbor[:, 0], vecs_neighbor[:, 1])

    for word, vecid in word2vecid.items():
        vec = vecid2vec_2d[vecid]
        plt.text(vec[0], vec[1], word)

    plt.savefig(f"/results/figures/{output}.png")
    plt.clf()


def visualize(id2word: Dict[int, str],
              word2id: Dict[str, int],
              target_words: List[str],
              WV: List[List[float]],
              num_neighbors: int,
              output: str = "test") -> None:

    os.makedirs("/results/figures", exist_ok=True)

    V = len(id2word)
    T = len(WV) // V
    WV_eachtimes = np.split(WV, T)

    # group, one-slice
    ## group words
    ## group vectors
    for curr_time in range(T):
        w2v, w2n = get_vectors_eachslice(id2word, word2id, target_words, WV_eachtimes[curr_time], False)
        logging.debug("[visualize] group, one-slice:")
        logging.debug(f"[visualize] - w2v: {len(w2v)} items")
        logging.debug(f"[visualize] - w2n: {w2n}")
        plot_2d(target_words, w2v, w2n, f"group_single-{curr_time}_{output}")

    # group, all-slices
    ## group words
    ## group vectors in each slice
    w2v, w2n = get_vectors_allslices(id2word, word2id, target_words, WV_eachtimes, T)
    logging.debug("[visualize] group, all-slices:")
    logging.debug(f"[visualize] - w2v: {len(w2v)} items")
    logging.debug(f"[visualize] - w2n: {w2n}")
    plot_2d(target_words, w2v, w2n, f"group_all_{output}")

    # group+neighbors, one-slice
    ## group words
    ## group vectors
    ## neighbor words for each group word
    ## neighbor vectors for each group word
    for curr_time in range(T):
        w2v, w2n = get_vectors_eachslice(id2word, word2id, target_words, WV_eachtimes[curr_time], True, num_neighbors)
        logging.debug("[visualize] group+neighbors, one-slice:")
        logging.debug(f"[visualize] - w2v: {len(w2v)} items")
        logging.debug(f"[visualize] - w2n: {w2n}")
        plot_2d(target_words, w2v, w2n, f"group-neighbor_single-{curr_time}_{output}")

    # group+neighbors, all-slices
    ## group words
    ## group vectors in each slice 
    ## neighbor words for each group word in each slice
    ## neighbor vectors for each group word in each slice
    w2v, w2n = get_vectors_allslices(id2word, word2id, target_words, WV_eachtimes, T, True, num_neighbors)
    logging.debug("[visualize] group+neighbors, all-slices:")
    logging.debug(f"[visualize] - w2v: {len(w2v)} items")
    logging.debug(f"[visualize] - w2n: {w2n}")
    plot_2d(target_words, w2v, w2n, f"group-neighbor_all_{output}")


def cli_main():
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle_id2word", help="path of dict[id]->word")
    parser.add_argument("--joint_vector", help="path of joint ppmi-svd vector matrix, (V*T, D) dim")
    parser.add_argument("--target_word_pathes", nargs="*", help="pathes of target words (\n separated, .txt style)")
    parser.add_argument("--num_neighbors", type=int, default=3, help="number of neighbors (default=3words)")
    parser.add_argument("--output_names", nargs="*", help="output names")

    args = parser.parse_args()
    logging.debug(f"[main] args: {args}")

    logging.debug("[main] load dict, word vectors")
    id2word, word2id = load_pickle(args.pickle_id2word)
    WV = np.load(args.joint_vector)

    logging.debug("[main] visualize each target group")
    for target_word_path, output_name in zip(args.target_word_pathes, args.output_names):
        target_words = []
        with open(target_word_path) as fp:
            for line in fp:
                target_word = line.strip()
                if target_word in word2id:
                    target_words.append(target_word)
        if len(target_words) == 0:
            continue
        
        logging.debug(f"[main] - target_words: {target_words}")
        visualize(id2word, word2id, target_words, WV, args.num_neighbors, output_name)

if __name__ == "__main__":
    cli_main()
