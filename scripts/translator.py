import argparse
import google.generativeai as genai
import re
import time

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = re.compile(r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\s+(.+?)(?=\n\n|\Z)', re.DOTALL)
    entries = pattern.findall(content)
    return [
        {
            'index': idx,
            'time': time,
            'text': text.replace('\n', ' ')
        }
        for idx, time, text in entries
    ]

def write_srt(entries, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(f"{entry['index']}\n{entry['time']}\n{entry['text']}\n\n")

def split_tags_and_text(line):
    tags = ''
    text = line
    match = re.match(r'^((?:\{.*?\})+)\s*(.*)', line)
    if match:
        tags = match.group(1)
        text = match.group(2)
    return tags, text

def translate_texts_gemini(texts, api_key, target_lang, model_name, batch_size=25, max_requests_per_minute=15):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    translated = []
    tags_and_texts = [split_tags_and_text(line) for line in texts]
    only_texts = [t[1] for t in tags_and_texts]
    total = len(only_texts)
    request_count = 0
    start_time = time.time()
    for i in range(0, total, batch_size):
        batch_texts = only_texts[i:i+batch_size]
        print(f"translating batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total)}) of {((total-1)//batch_size)+1}...")
        numbered_batch = [f"{idx+1}. {line}" for idx, line in enumerate(batch_texts)]
        joined_text = "\n".join(numbered_batch)
        prompt = (
            f"Translate the following numbered subtitles to {target_lang}. "
            "Only return the translated lines, line by line, in the same order, without any explanations or extra output. "
            "Keep the numbering in your output.\n\n"
            f"{joined_text}"
        )
        try:
            response = model.generate_content(prompt)
            lines = response.text.strip().split('\n')
            batch_translated = [re.sub(r'^\d+\.\s*', '', line).strip() for line in lines if line.strip()]
            if len(batch_translated) != len(batch_texts):
                print("warning: returning original texts for this batch because of a mismatch in batch size and translation lines")
                batch_translated = batch_texts
            for j, translated_text in enumerate(batch_translated):
                tags = tags_and_texts[i + j][0]
                translated.append(f"{tags}{translated_text}")
        except Exception as e:
            print(f"error: {e}")
            for j, orig_text in enumerate(batch_texts):
                tags = tags_and_texts[i + j][0]
                translated.append(f"{tags}{orig_text}")
        request_count += 1
        if request_count >= max_requests_per_minute:
            elapsed = time.time() - start_time
            if elapsed < 60:
                wait_time = 60 - elapsed
                print(f"waiting {int(wait_time)+1}s to avoid rate limit...")
                time.sleep(wait_time + 1)
            request_count = 0
            start_time = time.time()
        else:
            time.sleep(4)
    return translated

def main():
    parser = argparse.ArgumentParser(description="translate srt file using google gemini")
    parser.add_argument("input", help="input .srt file")
    parser.add_argument("output", help="output .srt file")
    parser.add_argument("language", help="target language")
    parser.add_argument("apikey", help="gemini api key")
    parser.add_argument("--model", default="gemini-1.5-flash-latest", help="gemini model (default: gemini-1.5-flash-latest)")
    args = parser.parse_args()

    entries = parse_srt(args.input)
    texts = [entry['text'] for entry in entries]
    translated_texts = translate_texts_gemini(texts, args.apikey, args.language, args.model)
    for entry, translated in zip(entries, translated_texts):
        entry['text'] = translated
    write_srt(entries, args.output)
    print(f"saved translated srt: {args.output}")

if __name__ == "__main__":
    main()
