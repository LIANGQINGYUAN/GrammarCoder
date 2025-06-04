#!/bin/bash
export CUDA_VISIBLE_DEVICES=0,1

# folders
tag=grammarcoder7b-base-submission
log_dir="./${tag}_logs"
save_dir="./${tag}_results"
workspace="$(pwd)"
mkdir -p ${log_dir} ${save_dir}

# models
model_dir="../../Models/GrammarCoder-7B"
base_prefix="pygrammar"

model_type="base"
file_tag="ckp"


prefix='```'"${base_prefix}"


model_tag=GrammarCode7B
model_path="../../Models/GrammarCoder-7B"

save_tag="${model_tag}_${base_prefix}"
log_path=$log_dir/${save_tag}.log
save_path=$save_dir/${save_tag}.jsonl

echo "$model_path"
echo "$save_path"

# inference
python $workspace/vllm_inference.py \
    --model_path $model_path   \
    --model_type $model_type \
    --testset_path ./humaneval-python-grammar.json \
    --gpus 2 \
    --max_total_tokens 2000 \
    --max_new_tokens 1024 \
    --gpu_memory_utilization 0.9 \
    --temperature 0.0 \
    --prefix ${prefix} \
    --output_path $save_path | 
    tee $log_path 2>&1
sleep 3

# extract
python extract.py --input ${save_path} --output $save_dir/${save_tag}_solutions.jsonl 

# evaluate
evalplus.evaluate --dataset humaneval --samples $save_dir/${save_tag}_solutions.jsonl | 
    tee -a $log_path 2>&1
