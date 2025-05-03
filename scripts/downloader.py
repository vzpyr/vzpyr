import argparse
import os
import subprocess

def getwget():
    if not os.path.exists("wget"):
        print("wget not found. downloading...")
        try:
            if os.name == 'nt':
                subprocess.run(["powershell", "-Command", "(New-Object System.Net.WebClient).DownloadFile('https://eternallybored.org/misc/wget/1.21.4/64/wget.exe', 'wget.exe')"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"error: couldn't download wget: {e}")
            exit(1)
        except FileNotFoundError:
            print("error: curl or powershell not found.")
            exit(1)
    else:
        print("wget found in the current directory.")

def process(input_file):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if (i + 1) % 2 == 0:
                    link = line.strip()
                    print(f"downloading: {link}")
                    try:
                        subprocess.run(["./wget", link], check=True)
                        print(f"download completed.")
                    except subprocess.CalledProcessError as e:
                        print(f"error: couldn't download {link}: {e}")
    except FileNotFoundError:
        print(f"error: couldn't find '{input_file}'")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", required=True)
    args = p.parse_args()
    getwget()
    process(args.input)