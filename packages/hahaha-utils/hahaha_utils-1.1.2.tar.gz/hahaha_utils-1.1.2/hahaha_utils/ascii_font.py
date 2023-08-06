import sys

from colorama import init
init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
from termcolor import cprint 
from pyfiglet import figlet_format

def print_ascii_tetx(font_text):


       cprint(figlet_format(font_text, font='starwars'), 'green', 'on_red', attrs=['bold'])

if __name__ == '__main__':
       font_text = 'abcd'
       print_ascii_tetx(font_text)