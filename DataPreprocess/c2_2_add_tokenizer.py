import pickle
newruleset = set()
for i in range(0, 100):
    with open(f"./c2_addrules/output_{i}.pkl", "rb") as f:
        ruleset = pickle.load(f)
        newruleset.update(ruleset)

from transformers import AutoTokenizer, AutoModel
base_dir = 'xxx'

tokenizer = AutoTokenizer.from_pretrained(base_dir)

tokenizer.add_tokens(["comment_py -> End", "string_literal_py -> End", "start -> python", 'line_continuation_py -> End'])
tokenizer.add_tokens(list(newruleset))
tokenizer.save_pretrained('./new_tokenizer')