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
        "--model_path", type=str, default=""
    )
    parser.add_argument("--model_type", type=str, default="chat")
    parser.add_argument("--gpus", type=int, default=1)
    parser.add_argument("--max_num_seqs", type=int, default=8)
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.82)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--max_total_tokens", type=int, default=4096)
    parser.add_argument("--max_new_tokens", type=int, default=2048)
    parser.add_argument("--testset_path", type=str, default="")
    parser.add_argument("--output_path", type=str, default=None)
    parser.add_argument("--isInstruct", type=bool, default=False)
    return parser.parse_args()

def load_data(args):
    with open (args.testset_path, "r") as f:
        testsets = [json.loads(line) for line in f.readlines()]
    return testsets


# prefix = [151667, 152526, 151750]
prefix = [151667, 152526, 151750]

examples = []
import pandas as pd
def build_prompt_token_ids(testsets, tokenizer, args):
    input_prompt_token_ids = []
    data = pd.read_parquet('../../../mbppplus/data/test-00000-of-00001-d5781c9c51e02795.parquet')
    index=0
    for _, item in tqdm(data.iterrows(), desc="Building prompts"):
        if args.isInstruct:
            input_prompt_token_ids.append(tokenizer.encode("Please generate a python function for my problem.\n\nHere is my problem:\n>>> Problem:\n" + item['prompt'] + "\n>>> Test Cases:\n" + "\n".join(item['test_list']) + "\n\n>> Your Response:\n```python\n") + prefix) 
        else:
            input_prompt_token_ids.append(examples + tokenizer.encode('"""\n' + item['prompt'] + "\n>>> Test Cases:\n" + "\n".join(item['test_list']) +"\n>>> Code: \n\"\"\"\n```python\n" )+prefix) # v1
        if index==0:
            print(input_prompt_token_ids[0])
            print(tokenizer.decode(input_prompt_token_ids[0]))
        index+=1
    return input_prompt_token_ids

def main():
    args = parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    stop_sequences = [tokenizer.eos_token, "module_py -> End "]
    # stop_sequences = ['<|EOT|>']

    testsets = load_data(args)

    input_prompt_token_ids = build_prompt_token_ids(testsets, tokenizer, args)

    llm = LLM(
        model=args.model_path,
        tensor_parallel_size=args.gpus,
        max_model_len=args.max_total_tokens,
        # max_num_seqs=args.max_num_seqs,
        gpu_memory_utilization=args.gpu_memory_utilization,
        trust_remote_code=True
    )

    sampling_params = SamplingParams(
        temperature=args.temperature,
        max_tokens=args.max_new_tokens,
        stop=stop_sequences,
    )

    outputs = llm.generate(prompt_token_ids = input_prompt_token_ids, sampling_params = sampling_params)

    # outputs = [[output.outputs[0].token_ids] if 10252 not in output.outputs[0].token_ids else [output.outputs[0].token_ids[:output.outputs[0].token_ids.index(10252)]] for output in outputs]
    outputs = [[output.outputs[0].token_ids] for output in outputs]

    for i, output in enumerate(outputs):
        testsets[i]['outrulelist'] = prefix + list(output[0])

    with open(f"{args.output_path}", "w") as f:
        for item in testsets:
            f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    main()