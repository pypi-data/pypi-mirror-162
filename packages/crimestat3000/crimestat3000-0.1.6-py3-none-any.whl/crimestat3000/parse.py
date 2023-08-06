import pandas as pd
import re
import time
import random
from .helpers import (
    shorten_sheet_descr,
    districts_to_column,
    cumsum_to_monthly_values,
    rearrange_columns
)


def one_month(month, section,
              sheets='all', descr_row=4,
              columns='C',
              keep='all',
              shorten_descr=False,
              local_dir=None):

    month, year = month.split('-')[0], month.split('-')[1]

    if local_dir == None:
        path = f"http://crimestat.ru/loadStatisticFormXls/4-EGS_Razdel_{section}_{month}{year}"
        time.sleep(random.uniform(.01, 1))
    else:
        path = f"{local_dir}/{year}/{month}/4-EGS_Razdel_{section}_{month}{year}.xls"
    month_file = pd.ExcelFile(path)

    month_table = pd.DataFrame()
    sheets_range = month_file.sheet_names if sheets == 'all' else sheets

    sheet_filter = {
        'articles':  r'no articles mentioned|\bч\d|Г\d|[а-я]',
        'articles+': r'no articles mentioned',
        'all':       r'this will never match so every sheet will pass the filter'
    }

    for sheet in sheets_range:
        descr = month_file.parse(sheet, nrows=5).iloc[descr_row, 2]
        try:
            short_descr = shorten_sheet_descr(descr)
        except Exception as e:
            print(f"Parsing failed at sheet {sheet}.")
            print("Check if the sheet's description is in the 6th row (counting from 1).")
            print("If not -- add `descr_row` argument to your function call\nspecifying the needed row (defaul value is 4).")

        if re.search(sheet_filter[keep], short_descr):
            continue

        sheet_table = month_file.parse(
            sheet, usecols=f"B,{','.join(columns)}", index_col=0)
        sheet_table = sheet_table.loc[
            'Центральный федеральный округ':'Транспорт России'][:-1].reset_index()

        if shorten_descr == True:
            descr = short_descr

        if len(columns) > 1:
            clmns = ['region']
            clmns.extend([f"{descr}_[{col}]" for col in columns])
            sheet_table.columns = clmns
        else:
            sheet_table.columns = ['region', descr]

        try:
            sheet_table = districts_to_column(sheet_table)
        except:
            print(f"problem with:\nsheet {sheet}, {month}-{year}")
            raise Exception
        if len(month_table) == 0:
            month_table = sheet_table.copy()
        else:
            month_table = pd.merge(month_table, sheet_table)

    month_table['period_end'] = pd.to_datetime(f"{year}-{month}-01")
    month_table.sort_values(['region', 'period_end'], inplace=True)
    month_table = rearrange_columns(month_table)

    return month_table


def period(first_month, last_month, section,
           sheets='all', descr_row=4, columns='C',
           keep='all', shorten_descr=False,
           local_dir=None, cumsum=False):

    if (cumsum == False) and (first_month[:2] != '01'):
        first_month = pd.to_datetime(first_month) - pd.DateOffset(months=1)
    last_month = pd.to_datetime(last_month) + pd.DateOffset(months=1)

    months = pd.date_range(first_month, last_month, freq='M')
    months = [m.strftime('%m-%Y') for m in months]

    table = pd.DataFrame()

    for month in months:
        try:
            month_table = one_month(month, section, sheets, columns,
                                    keep=keep,
                                    shorten_descr=shorten_descr,
                                    local_dir=local_dir)
        except Exception as e:
            print(f"Problem period: {month}")  # just in case
            raise e

        table = pd.concat([table, month_table], ignore_index=True)

    if cumsum == False:
        cases_columns = [col for col in table.columns if col not in [
            'region', 'federal_district', 'period_end']]

        table_grouped = table.groupby(
            ['region', pd.Grouper(key='period_end', freq='Y')])
        table = pd.DataFrame()
        for _, subframe in table_grouped:
            subframe.reset_index(drop=True, inplace=True)
            subframe[cases_columns] = subframe[cases_columns].apply(
                cumsum_to_monthly_values)
            table = pd.concat([table, subframe], ignore_index=True)

    table = rearrange_columns(table)
    table.sort_values(['region', 'period_end'], inplace=True)

    if (cumsum == False) and (first_month[:2] != '01'):
        table = table[table['period_end'] > first_month]

    return table
