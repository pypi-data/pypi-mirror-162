class InconsistentColumns(Exception):
    pass
class InconsistentRows(Exception):
    pass
def combine_rows(tables):
    for table in tables:
        if len(table[0]) != len(tables[0][0]):
            raise InconsistentColumns('Tables do not share the same total column numbers.')
    comb = []
    for table in tables:
        comb.extend(table)
    return comb
def combine_columns(tables):
    for table in tables:
        if len(table) != len(tables[0]):
            raise InconsistentRows('Tables do not share the same total row numbers.')
    comb = [[] for i in range(len(tables[0]))]
    for row in range(len(tables[0])):
        for table in tables:
            comb[row] += table[row]
    return comb
