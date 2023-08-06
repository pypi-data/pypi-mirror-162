class InvalidCSVFormat(Exception):
    def __init__(self, error_info):
        super(InvalidCSVFormat, self).__init__(error_info)
        self.error_info = error_info
    def __str__(self):
        return self.error_info
class InvalidDataFormat(Exception):
    def __init__(self, error_info):
        super(InvalidDataFormat, self).__init__(error_info)
        self.error_info = error_info
    def __str__(self):
        return self.error_info        
def read(filename, delimiter=','):
    res = [[]]
    with open(filename, 'r', encoding = 'utf-8') as f:
        table = f.read().strip() + '\n'
    cur_row = 0
    cur_col = 0
    quote_cnt = 0
    last_col_cnt = 0
    cur_col_cnt = 0
    for i in range(len(table)):
        if table[i] == '\n' or table[i] == delimiter:
            if quote_cnt == 0:
                res[cur_row].append(table[cur_col:i])
                cur_col_cnt += 1
                if cur_row == 0:
                    last_col_cnt += 1
                cur_col = i + 1
                if table[i] == '\n':
                    cur_row += 1
                    if i != len(table) - 1:
                        res.append([])
                    if cur_col_cnt != last_col_cnt:
                        raise InvalidCSVFormat('Number of columns in each row should be equal')
                    else:
                        cur_col_cnt = 0
            elif quote_cnt % 2 == 0:
                if table[i-1] != '"' or table[cur_col] != '"':
                    raise InvalidCSVFormat('Quotation marks cannot appear in cells that are not surrounded by quotation marks')
                else:
                    cell = table[cur_col+1:i-1]
                    cell_revised = ''
                    j = 0
                    while j<len(cell):
                        cell_revised += cell[j]
                        if cell[j] == '"':
                            if j+1 < len(cell) and cell[j+1] != '"':
                                raise InvalidCSVFormat('Original quotation marks in a cell should be doubled')
                            else:
                                j += 2
                        else:
                            j += 1
                    res[cur_row].append(cell_revised)
                    cur_col_cnt += 1
                    if cur_row == 0:
                        last_col_cnt += 1
                    cur_col = i + 1
                    if table[i] == '\n':
                        cur_row += 1
                        if i != len(table) - 1:
                            res.append([])
                        if cur_col_cnt != last_col_cnt:
                            raise InvalidCSVFormat('Number of columns in each row should be equal')
                        else:
                            cur_col_cnt = 0
                    quote_cnt = 0
            else:
                if table[cur_col] != '"':
                    raise InvalidCSVFormat('Quotation marks cannot appear in cells that are not surrounded by quotation marks')
        elif table[i] == '"': 
            quote_cnt += 1
    return res
def write(filename, table, delimiter=','):
    rows = len(table)
    columns = len(table[0])
    res = ''
    last_col_cnt = 0
    cur_col_cnt = 0
    for row in range(rows):
        cur_col_cnt = len(table[row])
        if row == 0:
            last_col_cnt = len(table[row])
        if last_col_cnt != cur_col_cnt:
            raise InvalidDataFormat('Number of columns in each row should be equal')
        for column in range(columns):
            cell = table[row][column]
            if ('"' in cell) or (delimiter in cell) or ('\n' in cell):
                cell_revised = '"'
                for char in cell:
                    cell_revised += char
                    if char == '"':
                        cell_revised += '"'
                cell_revised += '"'
            else:
                cell_revised = cell[:]
            res += cell_revised
            if column != columns - 1:
                res += ','
            else:
                res += '\n'
    with open(filename, 'w', encoding = 'utf-8') as f:
        f.write(res)
