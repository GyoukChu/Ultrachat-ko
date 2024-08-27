from openai import OpenAI
client = OpenAI(
    api_key= "YOUR_SOLAR_API_KEY",
    base_url="https://api.upstage.ai/v1/solar"
)
from tqdm import tqdm
tqdm.pandas()
import pandas as pd
import time
import argparse

def solar_translate_apicall(source_input, previous_translate_results):
    trial_count = 0
    while True:
        try:
            stream = client.chat.completions.create(
                model="solar-1-mini-translate-enko",
                messages= previous_translate_results + 
                    [
                        {
                            "role": "user",
                            "content": source_input
                        },
                    ]
                ,
                stream=False,
            )
        except Exception as e:
            if e.status_code == 401: # Unauthorized
                raise Exception(e.response)
            elif e.status_code == 429: # Rate Limit
                raise Exception(e.response)
            elif e.status_code in [500, 502, 503, 504] : # Internal Server Error
                trial_count += 1
                if trial_count <= 10:
                    print("Internal Server Error. Retrying...")
                    time.sleep(5)
                    continue
                else:
                    print("Retried 10 times, but still failed. Please check the server status.")
                    raise Exception(e.response)   
        else:
            break
    return stream.choices[0].message.content

def translate_conversations(input_file, output_file):
    df = pd.read_json(input_file, lines=True)
    # df = df.head(2)

    def translate(conversations):
        output = []
        # 번역 어투 고정을 위한 예시 하나, 처음 번역에 사용
        TRANSLATE_EXAMPLE = [
            {
                "role": "user",
                "content": "Hello. How can I help you?"
            },
            {
                "role": "assistant",
                "content": "안녕하세요. 어떻게 도와드릴까요?"
            },
        ]
        previous_translate_results = TRANSLATE_EXAMPLE 
        for speech in conversations:
            # speech: "content", "role"로 구성된 dictionary
            # 1. output 갱신
            temp = dict()
            temp['role'] = speech['role']
            translate_result = solar_translate_apicall(source_input=speech['content'], previous_translate_results=previous_translate_results)
            temp['content'] = translate_result
            output.append(temp)
            # 2. 이전 번역결과에 추가
            previous_translate_results = previous_translate_results[2:]
            previous_translate_results.append({'role':'user', 'content':speech['content']})
            previous_translate_results.append({'role':'assistant', 'content':translate_result})
        return output

    df['conversations'] = df['messages'].progress_apply(translate)

    df = df[['prompt_id', 'messages', 'conversations']]
    # Save to jsonl
    df.to_json(output_file, orient='records', lines=True, force_ascii=False)
    print("*****************************")
    print(f"!!!!!!!!!번역 완료!!!!!!!!!!!")
    print("*****************************")

    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process two filenames.")
    parser.add_argument('--filename1', type=str, required=True, help='The first filename.')
    parser.add_argument('--filename2', type=str, required=True, help='The second filename.')
    
    args = parser.parse_args()
    print(f"번역 파일: {args.filename1}")
    translate_conversations(args.filename1, args.filename2)
    # translate_conversations(f"split/1.jsonl", f"output/1.jsonl")
