# Copyright (C) 2023 Warren Usui, MIT License
"""
Collect draft results, reformat
"""
import os
import pandas as pd

def dotrim_rows(plyr_row):
    """
    Return False if we do not want to save this row because the value of the
    first column is not a player position.
    """
    if isinstance(plyr_row[1][0], float):
        return False
    if plyr_row[1][0] == 'x':
        return False
    if plyr_row[1][0].startswith("Max") or plyr_row[1][0].startswith("Slots"):
        return False
    return True

def reformat_rows(league):
    """
    Filter out rows that are invalid.
    """
    return list(map(lambda a: a[1], list(filter(dotrim_rows,
                                                league.iterrows()))))

def read_start_of_season():
    """
    Get the original draft page.
    """
    return pd.read_excel(os.sep.join(["data", "draft.xlsx"]), header=1)

def make_table():
    """
    Return DataFrame with invalid rows filtered and Position column named.
    """
    return pd.DataFrame(reformat_rows(read_start_of_season())).rename(
                    columns={'Unnamed: 0': 'Position'}).reset_index()

def fix_columns(old_df):
    """
    Columns for the new DataFrame are Position and Manager names.
    """
    return old_df[['Position'] + list(map(lambda a: old_df.columns[2:][a],
                                  range(0, 3 * 10 - 1, 3)))]

def get_cleaner_xlsx(xlsx_file):
    """
    Write new excel file with data reformatted
    """
    fix_columns(make_table()).to_excel(os.sep.join(['data', xlsx_file]),
                                       index=False)

if __name__ == "__main__":
    get_cleaner_xlsx("formatted_draft.xlsx")
