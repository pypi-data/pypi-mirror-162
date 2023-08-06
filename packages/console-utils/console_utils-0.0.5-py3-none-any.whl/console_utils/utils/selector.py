import sys
import keyboard as kb


def select(array: list):
    row = 0
    accept = True
    a_len = 7
    for x in array:
        if len(x) > a_len: a_len = len(x)
    a_len+=2
    row_len = len(array)
    
    heat = ['┌'+'─'*a_len+'┐']
    free = a_len - 7
    left = free//2
    right = free - left
    heat.append('│'+' '*left+'Select:'+' '*right+'│')
    heat.append('│'+'─'*a_len+'│')

    while True:
        if accept:
            field = heat.copy()
            for row_, row_data in enumerate(array):
                free = a_len - len(row_data)
                if row_ == row: 
                    row_data = f'[{row_data}]'
                    free -= 2

                left = free//2
                right = free - left

                field.append('│'+' '*left+row_data+' '*right+'│')
            field.append('└'+'─'*a_len+'┘')

            for row_data in field:
                print(row_data)

        key = kb.read_key()

        if accept: accept = False
        else:
            accept = True
            continue

        if key == 'up': row -= 1
        elif key == 'down': row += 1
        elif key == 'enter':
            return row

        for _ in range(row_len+4):
            sys.stdout.write("\033[F")

        if row < 0: row = row_len - 1
        elif row > row_len - 1: row = 0
