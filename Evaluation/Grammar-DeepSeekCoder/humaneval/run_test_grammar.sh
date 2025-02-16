MBaseDir=../../../Models
ModelDir=GrammarCoder-1.3B-Base

# if [ ! -d "$ModelDir" ];then
# mkdir $ModelDir
# fi


# GPUID=6
# saveFolder=./${ModelDir}
# LOGFILE="${saveFolder}/output_log.txt"


# CUDA_VISIBLE_DEVICES=$GPUID python vllm_inference_grammar.py \
#     --model_path=${MBaseDir}/${ModelDir} \
#     --testset_path=./humaneval-python-c2.jsonl \
#     --output_path=${saveFolder}/res_c3.json \
#     | tee -a "$LOGFILE"

# python c3_tokens2mytree.py \
#     --rfile=${saveFolder}/res_c3.json \
#     --wfile=${saveFolder}/res_c4.json \
#     | tee -a "$LOGFILE"

# python c4_mytree2code.py \
#     --rfile=${saveFolder}/res_c4.json \
#     --wfile=${saveFolder}/res_c5.json \
#     | tee -a "$LOGFILE"

# python c5_testhumaneval.py \
#     --rfile=${saveFolder}/res_c5.json \
#     --wfile=${saveFolder}/res_c6.jsonl \
#     | tee -a "$LOGFILE"

# evalplus.evaluate --dataset humaneval --samples ${saveFolder}/res_c6.jsonl  | tee -a "$LOGFILE"



ModelDir=GrammarCoder-1.3B-Instruct

if [ ! -d "$ModelDir" ];then
mkdir $ModelDir
fi


GPUID=6
saveFolder=./${ModelDir}
LOGFILE="${saveFolder}/output_log.txt"


CUDA_VISIBLE_DEVICES=$GPUID python vllm_inference_grammar.py \
    --model_path=${MBaseDir}/${ModelDir} \
    --testset_path=./humaneval-python-c2.jsonl \
    --output_path=${saveFolder}/res_c3.json \
    | tee -a "$LOGFILE"

python c3_tokens2mytree.py \
    --rfile=${saveFolder}/res_c3.json \
    --wfile=${saveFolder}/res_c4.json \
    | tee -a "$LOGFILE"

python c4_mytree2code.py \
    --rfile=${saveFolder}/res_c4.json \
    --wfile=${saveFolder}/res_c5.json \
    | tee -a "$LOGFILE"

python c5_testhumaneval.py \
    --rfile=${saveFolder}/res_c5.json \
    --wfile=${saveFolder}/res_c6.jsonl \
    | tee -a "$LOGFILE"

evalplus.evaluate --dataset humaneval --samples ${saveFolder}/res_c6.jsonl  | tee -a "$LOGFILE"



