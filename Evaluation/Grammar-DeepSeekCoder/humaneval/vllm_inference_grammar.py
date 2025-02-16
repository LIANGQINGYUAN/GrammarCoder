from argparse import ArgumentParser
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import os
import json
from tqdm import tqdm
import logging
from jinja2 import Template

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--model_path", type=str, default="/share/liangqingyuan/GrammarInfilling/src/saved_models/DeepSeekv2_Scratch_DeepSeek-12-2e-06/00test/checkpoints-700000"
    )
    parser.add_argument("--model_type", type=str, default="chat")
    parser.add_argument("--gpus", type=int, default=1)
    parser.add_argument("--max_num_seqs", type=int, default=8)
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.82)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--max_total_tokens", type=int, default=8192)
    parser.add_argument("--max_new_tokens", type=int, default=4096)
    parser.add_argument("--testset_path", type=str, default="humaneval-python-c2.jsonl")
    parser.add_argument("--output_path", type=str, default=None)
    return parser.parse_args()

def load_data(args):
    with open (args.testset_path, "r") as f:
        testsets = [json.loads(line) for line in f.readlines()]
    return testsets

def build_prompt_token_ids(testsets):
    input_prompt_token_ids = []
    for item in tqdm(testsets, desc="Building prompts"):
        input_prompt_token_ids.append(item['rulelist'][:-3])
    return input_prompt_token_ids


def main():
    args = parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    stop_sequences = [tokenizer.eos_token, "module_py -> End ", '<|EOT|>']
    # stop_sequences = ['<|EOT|>']

    testsets = load_data(args)

    input_prompt_token_ids = build_prompt_token_ids(testsets)

    llm = LLM(
        model=args.model_path,
        tensor_parallel_size=args.gpus,
        max_model_len=args.max_total_tokens,
        # max_num_seqs=args.max_num_seqs,
        gpu_memory_utilization=args.gpu_memory_utilization,
    )

    sampling_params = SamplingParams(
        temperature=args.temperature,
        max_tokens=args.max_new_tokens,
        stop=stop_sequences,
    )

    outputs = llm.generate(prompt_token_ids = input_prompt_token_ids, sampling_params = sampling_params)

    outputs = [[output.outputs[0].token_ids] for output in outputs]

    for i, output in enumerate(outputs):
        testsets[i]['outrulelist'] = list(output[0])

    with open(f"{args.output_path}", "w") as f:
        for item in testsets:
            f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    main()