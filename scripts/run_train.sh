if [ $# -lt 4 ]; then
    echo "Missing arguments! Usage: <doc1> <doc2> ... <docN> <window> <dimension>"
    exit 1
fi


mkdir results
mkdir ./results/models
window=${@: -2:1}
dimension=${@: -1:1}

mat_pathes=""

document_commands=""
document_filepathes=""
for ((i = 1; i <= $# - 2; i++)); do
    document="${!i}"
    document_abspath=$(readlink -f "$document")
    document_filename=$(basename "$document")

    document_filepath="/data/${document_filename}"
    document_command="-v ${document_abspath}:${document_filepath}"

    docker run --name ws-slim_container_train \
        -w /app ${document_command} \
        -v ./results:/results \
        ws-slim \
        python sppmisvd/main.py \
            --file_path ${document_filepath} \
            --pickle_id2word /results/id2word.pkl \
            --window_size ${window} \
            --dim ${dimension} \
            --shift 1

    docker cp ws-slim_container_train:/app/model/C_w-${window} ./results/models/C_${i}_w-${window}
    mat_path="PPMI_${i}_w-${window}_s-1"
    mat_pathes="${mat_pathes} /results/models/${mat_path}"
    docker cp ws-slim_container_train:/app/model/SPPMI_w-${window}_s-1 ./results/models/PPMI_${i}_w-${window}_s-1
    docker cp ws-slim_container_train:/app/model/WV_d-${dimension}_w-${window}_s-1.npy ./results/models/WV_${i}_d-${dimension}_w-${window}_s-1.npy

    docker rm ws-slim_container_train

done

docker run --name ws-slim_container_train \
    -w /app \
    -v ./results:/results \
    ws-slim \
    python joint_decompose.py \
        --pickle_id2word /results/id2word.pkl \
        --mat_pathes ${mat_pathes} \
        --dim ${dimension}

docker cp ws-slim_container_train:/app/WV_d-${dimension}.npy ./results/models/WV_joint_d-${dimension}_w-${window}_s-1.npy

docker remove ws-slim_container_train

