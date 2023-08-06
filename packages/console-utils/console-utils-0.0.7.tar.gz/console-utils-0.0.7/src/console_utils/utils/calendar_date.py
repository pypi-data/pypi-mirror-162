from datetime import datetime, timedelta
import sys
import keyboard as kb
import calendar as cal


def _fill_calendar(date: datetime, sel_row=0, sel_col=0):
    month_cal = ['┌'+'─'*34+'┐']
    month_name = f'{cal.month_name[date.month]} {date.year}'
    space = (28 - len(month_name))//2
    free = 0 if len(month_name)%2 == 0 else 1
    pice = space//2
    prevp = ' < '
    nextp = ' > '
    if sel_row < 0:
        if sel_col == 1: prevp = '[<]'
        else: nextp = '[>]'

    month_cal.append('│'+' '*pice+prevp+' '*(space-pice)+month_name+' '*(space-pice+free)+nextp+' '*pice+'│')
    month_cal.append('│ '+'   '.join(["Mo","Tu","We","Th","Fr","Sa","Su"])+' │')
    for row, week in enumerate(cal.monthcalendar(date.year, date.month)):
        out = ['    ' if x == 0 else f' {x} ' if x>9 else f'  {x} ' for x in week]
        if row == sel_row:
            out[sel_col] = f'[{out[sel_col][1:-1]}]'
        month_cal.append('│'+' '.join(out)+'│')

    month_cal.append('└'+'─'*34+'┘')

    for week in month_cal:
        print(week)
    if len(month_cal) < 10:
        sys.stdout.write("\033[K")
        sys.stdout.write("\033[F")
        print()

    return month_cal


def get_date(current_date = datetime.now()):
    row = 0
    col = 0
    date = current_date.replace(day=1)
    month_cal = _fill_calendar(date, row, col)

    while True:
        key = kb.read_key()
        kb.read_key()
        row_len = len(month_cal)
        if key == 'up': row -= 1
        elif key == 'down': row += 1
        elif key == 'left': col -= 1
        elif key == 'right': col += 1
        elif key == 'enter':
            input('skipping real key input')
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            if row < 0:
                if col == 1: date -= timedelta(1)
                else: date += timedelta(31)
                date = date.replace(day=1)
            else:
                for row_, week in enumerate(cal.monthcalendar(date.year, date.month)):
                    if row_ == row and week[col]:
                        for _ in range(row_len):
                            sys.stdout.write("\033[F")
                            sys.stdout.write("\033[K")
                        return date.replace(day=week[col])

        for _ in range(row_len):
            sys.stdout.write("\033[F")

        if row == -10:
            if col == 2 or col == 6: col = 5
            elif col == 4 or col == 0: col = 1
        elif row == -9: row = 0
        elif row == -1:
            row = -10
            if col < 3: col = 1
            else: col = 5

        if col > 6:
            if row < row_len-5:
                col = 0
                row += 1
            else: col = 6

        elif col < 0:
            if row > 0:
                col = 6
                row -= 1
            else: col = 0
        if row > row_len-5: row = row_len-5
        elif row < 0: row = -10

        month_cal = _fill_calendar(date, row, col)
