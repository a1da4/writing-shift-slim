if [ $# -lt 4 ]; then
    echo "Missing arguments! Usage: <window> <dimension> <word_list> <topk>"
    exit 1
fi


window=${@: -4:1}
dimension=${@: -3:1}
target_word_list=${@: -2:1}
target_word_list_abspath=$(readlink -f "$target_word_list")
target_word_list_filename=$(basename "$target_word_list")
topk=${@: -1:1}

docker run --name ws-slim_container_understand \
    -w /app \
    -v ./results:/results \
    -v "${target_word_list_abspath}":/data/"${target_word_list_filename}" \
    ws-slim \
    python calculate_neighbors.py \
        --pickle_id2word /results/id2word.pkl \
        --joint_vector /results/models/WV_joint_d-${dimension}_w-${window}_s-1.npy \
        --target_words /data/${target_word_list_filename} \
        --topk 20

docker remove ws-slim_container_understand

