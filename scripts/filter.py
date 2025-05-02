import argparse

group = ""

def extract(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        return "\n".join(f"{lines[i]}\n{lines[i+1]}" for i in range(len(lines)-1) if group in lines[i])
    except FileNotFoundError:
        return f"error: '{file_path}' not found."
    except UnicodeDecodeError as e:
        return f"error: couldn't decode '{file_path}': {e}"

def save(output_path, text):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text + "\n")
        print(f"saved to '{output_path}'")
    except Exception as e:
        print(f"error: couldn't save to '{output_path}': {e}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", required=True)
    p.add_argument("-o", "--output", required=True)
    args = p.parse_args()
    result = extract(args.input)
    if result.startswith("error:"):
        print(result)
    else:
        save(args.output, result)