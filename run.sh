#!/bin/bash

# python get_data.py

for i in {1..300}
do
    filename1="split/${i}.jsonl"
    filename2="output/${i}.jsonl"

    python translate.py --filename1 "$filename1" --filename2 "$filename2"
done
