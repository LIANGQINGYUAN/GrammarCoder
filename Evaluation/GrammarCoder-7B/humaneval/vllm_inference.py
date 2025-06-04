from argparse import ArgumentParser
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import os
import json
from tqdm import tqdm
import logging
from jinja2 import Template

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s'
)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--model_path", type=str, default="."
    )
    parser.add_argument("--model_type", type=str, default="chat")
    parser.add_argument("--gpus", type=int, default=8)
    parser.add_argument("--max_num_seqs", type=int, default=8)
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.82)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--max_total_tokens", type=int, default=8192)
    parser.add_argument("--max_new_tokens", type=int, default=512)
    parser.add_argument("--testset_path", type=str)
    parser.add_argument("--output_path", type=str, default=None)
    parser.add_argument("--prefix", type=str, default=None)
    return parser.parse_args()


def build_prompt(data, tokenizer, args):
    input_prompts = []
    index=0
    for item in tqdm(data, desc="Building prompts"):
        if args.prefix != 'None':
            prefix=f"{args.prefix}\n"
        else:
            prefix = ''
        # prompt = "Please generate a python function for my problem.\n\nHere is my problem:\n>>> Problem:\n" + item['prompt'] + "\n>>> Test Cases:\n" + "\n".join(item['test_list']) + f"\n\n>> Your Response:\n{prefix}"
        if 'python' in prefix:
            prompt = f"{prefix}{item['prompt']}"
        else:
            prompt = f"{prefix}{item['grammar_str']}"
        if 'chat' == args.model_type:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            prompt = prompt
        
        if index==0:
            print("PROMPTS:\n", prompt)
            index+=1

        input_prompts.append(prompt)

    return input_prompts


import json
import pandas as pd
from tqdm import tqdm
def read_data(file_name):
    items = []
    for i in open(file_name,'r').readlines():
        items.append(json.loads(i))
    return items

def load_data(args):
    return read_data(args.testset_path)


def generate_batch(examples, prompts, tokenizer, llm, model: str, temperature: float=0.0):
    # stop_sequences = [tokenizer.eos_token]
    # stop_sequences = [tokenizer.eos_token, "<|module_py -> End |>"]
    stop_sequences = []
    OUTPUT_NUM = 1
    # Create a sampling params object.
    # seed = random.randint(0, 2**32 - 1)
    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=0.95,
        max_tokens=10000, # 1500--10num
        stop=stop_sequences,
        seed=42,
        n=OUTPUT_NUM,
        logprobs=1
    )

    print("Sample prompt: {}".format(prompts[0]))
    outputs = llm.generate(prompts, sampling_params)
    print("Generate over!")
    print(len(examples), len(outputs))
    # outputs = list(range(len(examples)))

    for i in tqdm(range(len(examples))):
        # res = [outputs[i] for j in range(OUTPUT_NUM)]
        # examples[i]['output'] =0
        if i==0:
            print("outputs: ", outputs[i])

        # single output
        res = outputs[i].outputs[0]  # CompletionOutput(index, text, token_ids)
        examples[i]['output'] = outputs[i].prompt + res.text
        examples[i]['cumulative_logprob'] = res.cumulative_logprob
        examples[i]['logprobs'] = [{list(r.items())[0][0]: [list(r.items())[0][1].logprob, list(r.items())[0][1].decoded_token]} for r in res.logprobs]
        # multi outputs
        # res = [outputs[i].outputs[j] for j in range(len(outputs[i].outputs))] # [CompletionOutput(index, text, token_ids), CompletionOutput()]
        # res = sorted(res, key=lambda x: x.index)
        # print(res)
        # examples[i]['output'] = [r.text for r in res]

    return examples

import pandas as pd
def main():
    args = parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    stop_sequences = [tokenizer.eos_token]

    # data = pd.read_parquet(args.testset_path)
    # testsets = [item.to_dict() for _, item in data.iterrows()]
    # testsets = testsets[:2]
    testsets = read_data(args.testset_path)

    input_prompts = build_prompt(testsets, tokenizer=tokenizer, args=args)

    llm = LLM(
        model=args.model_path,
        tensor_parallel_size=args.gpus,
        max_model_len=args.max_total_tokens,
        max_num_seqs=20,
        gpu_memory_utilization=args.gpu_memory_utilization,
        trust_remote_code=True
    )

    generated_examples = generate_batch(testsets, input_prompts, tokenizer, llm, args.model_type, args.temperature) 
    print("Generate all over!!!")
    if args.output_path is not None:
        with open(args.output_path, 'w', encoding='utf-8') as fw:
            for ex in generated_examples:
                # print(ex)
                # fw.write(json.dumps({'task_id': "HumanEval/" + ex['task_id'].split('/')[-1], 'output': ex['output']})+'\n')
                fw.write(json.dumps({'task_id': "HumanEval/" + ex['task_id'].split('/')[-1], 'output': ex['output'], "cumulative_logprob": ex['cumulative_logprob'], 'logprobs':ex['logprobs']})+'\n')
        print("Save {} processed examples into {} over!".format(len(generated_examples), args.output_path))


if __name__ == "__main__":
    main()
