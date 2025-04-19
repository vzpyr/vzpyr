import argparse
import random
import string
import requests
from colorama import Fore, Style, init

init()

def generate_name(length, numbers, underscores):
    """Generates a random name following Minecraft's rules"""
    chars = string.ascii_lowercase
    if numbers:
        chars += string.digits
    if underscores:
        chars += "_"
    first_char = random.choice(string.ascii_lowercase)
    return first_char + ''.join(random.choices(chars, k=length-1))

def check_name(name):
    """Checks name availability using Mojang's API"""
    try:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{name}")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def main():
    parser = argparse.ArgumentParser(description="Minecraft Name Checker")
    parser.add_argument("-a", "--amount", type=int, default=1000, help="Number of names to generate")
    parser.add_argument("-l", "--length", type=int, default=4, help="Length of the names")
    parser.add_argument("-n", "--numbers", action="store_true", help="Allow numbers in names")
    parser.add_argument("-u", "--underscores", action="store_true", help="Allow underscores in names")
    args = parser.parse_args()
    if not 3 <= args.length <= 16:
        print(f"{Fore.RED}Error: Length must be between 3 and 16{Style.RESET_ALL}")
        return
    available_names = []
    for _ in range(args.amount):
        name = generate_name(args.length, args.numbers, args.underscores)
        if check_name(name):
            print(f"{Fore.RED}{name} is claimed!{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}{name} is claimable!{Style.RESET_ALL}")
            available_names.append(name)
    with open("names.txt", "w") as f:
        f.write("\n".join(available_names))

if __name__ == "__main__":
    main()
