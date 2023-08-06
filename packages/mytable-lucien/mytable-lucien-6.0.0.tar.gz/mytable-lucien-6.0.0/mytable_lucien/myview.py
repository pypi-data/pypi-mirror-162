from mytable_lucien import mycsv

def select_range(table, columns=[], rows=[]):
    if len(rows) == 0:
        rows = [row for row in range(len(table))]
    if len(columns) == 0:
        columns = [column for column in range(len(table[0]))]
    table_select = []
    for row in rows:
        myrow = []
        for column in columns:
            myrow.append(table[row][column])
        table_select.append(myrow)
    return table_select
