from datasets import load_dataset
import json
import pandas as pd
# Load data
data = load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft")
# data = data.select(range(80))

# 300 Splits
num_splits = 300
split_size = len(data) // num_splits

# Save into jsonl
for i in range(num_splits):
    start_idx = i * split_size
    # Last part: include until the end
    end_idx = (i + 1) * split_size if i < num_splits - 1 else len(data)

    items = data.select(range(start_idx, end_idx))

    # Save into jsonl
    items.to_json(f"split/{i + 1}.jsonl", index=False, lines=True, orient='records', force_ascii=False)
