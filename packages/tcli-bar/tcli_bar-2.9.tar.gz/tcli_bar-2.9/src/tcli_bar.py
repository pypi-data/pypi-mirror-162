from time import sleep
from colorama import Fore


def bar(progress, total, icon='█', description='Downloading', show_percent=True, colour=Fore.WHITE):
    '''
    Be sure to print a ('\\n') after running the bar function!
    You can find out why ;)
    '''
    percent = 50 * (progress / float(total))
    some = percent - 50
    bar = icon * int(percent) + '-' * (50 - int(percent))
    if show_percent == True:
        print(colour + f"\r{description} |{bar}| {50 + percent:.2f}%", end="" + Fore.RESET)
    else:
        print(colour + f"\r{description} |{bar}|", end="" + Fore.RESET)

def free_bar(set, icon='█', description='Downloading', show_percent=True, colour=Fore.WHITE):
    for i in range(set * 100):
        f = set * 100 // 50
        bar = icon * (int(i / f)) + '-' * (49 - int(i / f))
        print(colour + f"\r{description} |{bar}|", end="" + Fore.RESET)

            

def rotate(begin = 'Downloading', sleep_value = 0.1, colour=Fore.WHITE):
    list = ['|', '/', '-', '\\']
    ting = '|'
    for i in list:
        sleep(sleep_value)
        ting = i
        print(colour + f'\r{begin} {ting}', end='\r' + Fore.RESET)

free_bar(set=100, icon= '+', colour=Fore.RED, description='Scanning...')