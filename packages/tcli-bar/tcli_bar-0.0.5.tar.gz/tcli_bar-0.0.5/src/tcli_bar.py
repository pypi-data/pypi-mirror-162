from time import sleep


def bar(progress, total, icon='█', begin='Downloading', show_percent=True):
    '''
    Be sure to print a ('\\n') after running the bar function!
    You can find out why ;)
    '''
    percent = 100 * (progress / float(total))
    bar = icon * int(percent) + '-' * (100 - int(percent))
    if show_percent == True:
        print(f"\r{begin} |{bar}| {percent:.2f}%", end="")
    else:
        print(f"\r{begin} |{bar}|", end="")

def rotate(begin = 'Downloading', sleep_value = 0.1):
    list = ['|', '/', '-', '\\']
    ting = '|'
    for i in list:
        sleep(sleep_value)
        ting = i
        print(f'\r{begin} {ting}', end='\r')
