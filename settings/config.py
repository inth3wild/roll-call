from dotenv import dotenv_values
from termcolor import colored



'''Get all environment variables'''
env = dotenv_values()

'''Create blue and red color notification icons'''
blue_colored_icon = colored('[*]', 'magenta')
red_colored_icon = colored('[*]', 'red')
green_colored_icon = colored('[*]', 'green')