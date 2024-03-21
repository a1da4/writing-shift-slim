# writing-shift-slim
light-weight implementation of 'writing-shift' https://github.com/a1da4/writing-shift

## Setup
```
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

Results are stored in `./results/models/`
```
bash run_train.sh <doc1> <doc2> ... <docN> <window_size> <dimension>
```

## Analyze
Calculate neighbors of target word vectors  

```
bash run_understand_neighbors.sh <joint_vector> <target_word_list> <topk>
```
