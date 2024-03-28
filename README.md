# writing-shift-slim
light-weight implementation of 'writing-shift' https://github.com/a1da4/writing-shift

## Setup
```
git clone https://github.com/a1da4/writing-shift-slim.git

git submodule update --init --recursive

docker build -t ws-slim .
```

## Preprocess
Check target word frequencies
```
cd scripts/

bash run_check_target_frequency.sh <doc1> <doc2> ... <docN> <target_word_list>
```

Obtain shared vocabulary across corpora
```
bash run_preprocess.sh <doc1> <doc2> ... <docN> <target_word_list> <threshold>
```

## Training
Compute Co-occur/PPMI/WV matrices for each doc
Also compute joint WV matrix

```
bash run_train.sh <doc1> <doc2> ... <docN> <window_size> <dimension>
```

Results are stored in `./results/models/`
 - `./results/models/C_<docId>_w-<window>`: co-occur matrix
 - `./results/models/PPMI_<docId>_w-<window>_s-1`: ppmi matrix
 - `./results/models/WV_<docId>_d-<dimension>_w-<window_size>_s-1.npy`: word vectors (each doc) 
 - `./results/models/WV_joint_d-<dimension>_w-<window_size>_s-1.npy`: joint word vector across docs

## Analyze
Calculate neighbors of target word vectors  

```
bash run_understand_neighbors.sh <joint_vector> <target_word_list> <topk>
```

## Visualize
(Optional) Visualize (and calculate distance) each group of target words  
group\_1 + group\_2 + ... + group\_L = all target words

```
ex) group_i.txt

word_i
word_j
word_k
```

```
bash run_visualize_each_group.sh <joint_vector> <topk> <word_list_1> <word_list_2> ... <word_list_L>
```

Results are stored in `./results/figures/`
Distances are stored in `./results/distances/`

