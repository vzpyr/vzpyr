import argparse
import google.generativeai as genai
import re
import time

def parse_ass(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().splitlines()
    
    header = []
    dialogues = []
    in_events = False
    
    for line in content:
        line = line.strip()
        if not line: continue
        
        lower_line = line.lower()
        
        if lower_line == '[events]':
            in_events = True
            header.append(line)
            continue
        
        if not in_events:
            header.append(line)
        elif lower_line.startswith('dialogue:'):
            # split on the 9th comma to separate fields from text (ass format has 9 fields before text)
            parts = line.split(',', 9)
            if len(parts) == 10:
                dialogues.append({
                    # everything up to the last comma (dialogue: layer, start, end, style, actor, margins, effect)
                    'prefix': ','.join(parts[:9]) + ',',
                    'text': parts[9]
                })
        else:
            header.append(line)
            
    return header, dialogues

def write_ass(header, dialogues, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(header) + '\n')
        for dialogue in dialogues:
            f.write(f"{dialogue['prefix']}{dialogue['text']}\n")

def translate_texts_gemini(dialogues, api_key, target_lang, model_name, batch_size=50, requests_per_minute=15):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    def get_tag_and_text(line):
        tags, text = '', line
        # extract ass-style inline tags {}
        match = re.match(r'^((?:\{.*?\})+)\s*(.*)', line)
        if match:
            tags, text = match.group(1), match.group(2)
        return tags, text

    tag_text_pairs = [get_tag_and_text(d['text']) for d in dialogues]
    only_texts = [t[1] for t in tag_text_pairs]
    original_tags = [t[0] for t in tag_text_pairs]
    total = len(only_texts)
    translated_texts = []
    request_count = 0
    start_time = time.time()
    
    for i in range(0, total, batch_size):
        batch_texts = only_texts[i:i+batch_size]
        print(f"translating batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total)}) of {((total-1)//batch_size)+1}...")
        
        numbered_batch = [f"{idx+1}. {line}" for idx, line in enumerate(batch_texts)]
        joined_text = "\n".join(numbered_batch)
        
        prompt = (
            f"translate the following numbered subtitles to {target_lang} naturally and colloquially. preserve honorifics (e.g., -san, -kun) if applicable. only return the translated lines, line by line, in the same numbered order, with no extra output."
            f"{joined_text}"
        )
        
        try:
            response = model.generate_content(prompt)
            lines = response.text.strip().split('\n')
            
            batch_translated = [re.sub(r'^\d+\.\s*', '', line).strip() for line in lines if line.strip()]
            
            if len(batch_translated) != len(batch_texts):
                print("warning: mismatch in batch size and translation lines. using original texts for this batch.")
                batch_translated = batch_texts
            
            for j, translated_text in enumerate(batch_translated):
                translated_texts.append(f"{original_tags[i + j]}{translated_text}")

        except Exception as e:
            print(f"error: {e}")
            for j in range(len(batch_texts)):
                translated_texts.append(f"{original_tags[i + j]}{batch_texts[j]}")
        
        request_count += 1
        
        if request_count >= requests_per_minute:
            elapsed = time.time() - start_time
            if elapsed < 60:
                wait_time = 60 - elapsed
                print(f"waiting {int(wait_time)+1}s to avoid rate limit...")
                time.sleep(wait_time + 1)
            request_count = 0
            start_time = time.time()
        else:
            time.sleep(4)
            
    return translated_texts

def main():
    parser = argparse.ArgumentParser(description="translate ass file using google gemini")
    parser.add_argument("input", help="input .ass file")
    parser.add_argument("output", help="output .ass file")
    parser.add_argument("language", help="target language")
    parser.add_argument("apikey", help="gemini api key")
    parser.add_argument("--model", default="gemini-2.5-flash", help="gemini model (default: gemini-2.5-flash)")
    args = parser.parse_args()

    header, dialogues = parse_ass(args.input)
    
    translated_texts = translate_texts_gemini(dialogues, args.apikey, args.language, args.model)
    
    for dialogue, translated in zip(dialogues, translated_texts):
        dialogue['text'] = translated
        
    write_ass(header, dialogues, args.output)
    print(f"saved translated ass: {args.output}")

if __name__ == "__main__":
    main()
