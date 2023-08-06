from time import sleep


def bar(progress, total, icon='█', begin='Downloading', show_percent=True):
    '''
    Be sure to print a ('\\n') after running the bar function!
    You can find out why ;)
    '''
    percent = 100 * (progress / total)
    bar = icon * int(percent) + '-' * (100 - int(percent))
    if show_percent == True:
        print(f'{begin} |{bar}| {percent:.2f}%', end='\r')
    else:
        print(f'{begin} |{bar}|', end='\r')

def rotate(begin = 'Downloading', sleep_value = 0.1):
    list = ['|', '/', '-', '\\']
    ting = '|'
    for i in list:
        sleep(sleep_value)
        ting = i
        print(f'\r{begin} {ting}', end='\r')
