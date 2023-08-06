

def get_column_index(dataframe, columns):
    try:
        columns = list(columns)
    except:
        if isinstance(columns, (int, str)):
            columns = [columns]

    return [list(dataframe.columns).index(col) for col in columns]
