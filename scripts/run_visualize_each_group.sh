if [ $# -lt 3 ]; then
    echo "Missing arguments! Usage: <joint_vector> <topk> <word_list_1> <word_list_2> ... <word_list_L>"
    echo " <joint_vector>: please check ./results/models/ directory"
    exit 1
fi


joint_vector=$1
joint_vector_filename=$(basename "$joint_vector")
topk=$2

wordgroup_filepathes=""
wordgroup_commands=""
output_names=""
for ((i = 3; i <= $#; i++)); do
    wordgroup_path="${!i}"
    wordgroup_abspath=$(readlink -f "$wordgroup_path")
    wordgroup_filename=$(basename "$wordgroup_abspath")
    
    wordgroup_filepath="/data/${wordgroup_filename}"
    wordgroup_filepathes="${wordgroup_filepathes} ${wordgroup_filepath}"
    wordgroup_command="-v ${wordgroup_abspath}:${wordgroup_filepath}"
    wordgroup_commands="${wordgroup_commands} ${wordgroup_command}"

    output_names="${output_names} ${wordgroup_filename}"

done

docker run --name ws-slim_container_visualize \
    -w /app \
    -v ./results:/results \
    ${wordgroup_commands} \
    ws-slim \
    python visualize.py \
        --pickle_id2word /results/id2word.pkl \
        --joint_vector /results/models/${joint_vector_filename} \
        --target_word_pathes ${wordgroup_filepathes} \
        --num_neighbors ${topk} \
        --output_names ${output_names}

docker remove ws-slim_container_visualize

