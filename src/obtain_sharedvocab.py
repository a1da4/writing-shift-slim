import argparse
import pickle
import logging

from collections import defaultdict

from typing import Dict, List


def count_doc(file_pathes) -> List[str]:
    logging.basicConfig(level=logging.INFO)

    word2freq_pathes: List[str] = []

    for path_id, file_path in enumerate(file_pathes):
        logging.info(f"[count_doc] count file: {file_path}")
        word2freq = defaultdict(int)
        with open(file_path) as fp:
            for line in fp:
                words = line.strip().split()
                for word in words:
                    word2freq[word] += 1
        word2freq_path = f"/results/word2freq_{path_id}.pkl"
        pickle.dump(word2freq, open(word2freq_path, "wb"))
        word2freq_pathes.append(word2freq_path)
        logging.info(f"[count_doc] saved to {word2freq_path}")

    return word2freq_pathes


def obtain_frequent_words(word2freq: Dict[str, int], threshold: int) -> List[str]:
    word_list = []
    for word, freq in word2freq.items():
        if freq >= threshold:
            word_list.append(word)
    return word_list


def save_target_list(target_list: List[str], model_name=None) -> str:
    id2word: Dict[int, str] = {word_id: target_list[word_id] for word_id in range(len(target_list))}
    if model_name is None:
        model_name = "id2word"
    id2word_path = f"/results/{model_name}.pkl"
    pickle.dump(id2word, open(id2word_path, "wb"))
    with open(f"/results/{model_name}.txt", "w") as fp:
        for word_id, word in id2word.items():
            fp.write(f"{word_id}\t{word}\n")

    return id2word_path


def get_id2word(word2freq_pathes: List[str], threshold: int) -> str:
    logging.basicConfig(level=logging.INFO)

    target_list = None
    for word2freq_path in word2freq_pathes:
        word2freq_other: Dict[str, int] = pickle.load(open(word2freq_path, "rb"))
        logging.info(f"[get_id2word] {word2freq_path}: {len(word2freq_other)} words")
        word_list: List[str] = obtain_frequent_words(word2freq_other, threshold)
        logging.info(f"[get_id2word]  - processed! more than {threshold}: {len(word_list)} words")
        if target_list == None:
            target_list = list(set(word_list))
        else:
            target_list = list(set(target_list) & set(word_list))
        logging.info(f"[get_id2word]  - intersection of target words: {len(target_list)} words")

    id2word_path = save_target_list(target_list)

    return id2word_path


def main(args) -> None:
    logging.basicConfig(level=logging.INFO)

    logging.info("[main] count word frequency")
    word2freq_pathes = count_doc(args.file_pathes)

    logging.info("[main] get id2word dictionary")
    id2word_path = get_id2word(word2freq_pathes, args.threshold)


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_pathes", nargs="*", help="path of a target file")
    parser.add_argument("--threshold", type=int, default=100, help="threshold of frequency")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()
