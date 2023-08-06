import pandas as pd
import re


def shorten_sheet_descr(descr):
    spec_cases = {
        r"105–107|105–107": "105|106|107",
        r"чч. 3–6 ст. 264": "264_ч3|4|5|6",
        r"побои, нанесенные по мотивам политической": "116_ч2_б",
        r"Строка 1:": 'total'
    }
    for k, v in spec_cases.items():
        if re.search(k, descr):
            return v

    article_group = re.search(
        r'(п\.\s*[«"]|ч\.\s*\d|ст\.\s*\d|\bглава\s+).*', descr)
    if article_group == None:
        return re.search(r'строка\s*\d+\s*:', descr, re.IGNORECASE).group(0) + " no articles mentioned"
    else:
        article = re.search(
            r"ст\.\s*(\d+(?:\s*[–,и\.]\s*\d+)*)\s*УП?К", article_group.group(0))

        if article:
            article = re.sub(r"\s*30\s*[,и]", "", article.group(1))
            article = re.sub(r"(,\s+|\s+и\s+)", r"|", article)
            article = re.sub(r"\s+", "", article)
            short_descr = article

            part = re.search(
                r"ч\.\s*(\d+(?:\s*[–,и]\s*\d+)*)\s*ст", article_group.group(0))
            if part:
                part = re.sub(r"(,\s+|\s+и\s+)", r"|", part.group(1))
                short_descr = short_descr + "_ч" + part

                paragraph = re.search(
                    r'п\.\s*[«"](\w+)[»"]', article_group.group(0))
                if paragraph:
                    paragraph = re.sub(r"(,\s+|\s+и\s+)",
                                       r"|", paragraph.group(1))
                    short_descr = short_descr + "_" + paragraph
        else:
            section = re.search(r"глава\s*(\d+)", article_group.group(0))
            if section:
                return f"Г{section.group(1)}"
            else:
                return "no articles mentioned"

        return short_descr.strip()


def districts_to_column(table):

    # table1620['region'] = table1620['region'].apply(lambda reg:
    #   re.sub(r"г\.\s+|(\s+)?(-|–|—)(?!Манси|Петербург|Западный|Кавказ).*", "", reg))

    table['region'].replace(
        {"г. Москва": "Москва",
         "г. Санкт-Петербург": "Санкт-Петербург",
         "г. Севастополь": "Севастополь",
         "Кемеровская область - Кузбасс": "Кемеровская область",
         "Кемеровская область – Кузбасс": "Кемеровская область",
         "Республика Северная Осетия-Алания": "Республика Северная Осетия – Алания",
         "Республика Северная Осетия - Алания": "Республика Северная Осетия – Алания",
         "Республика Северная Осетия — Алания": "Республика Северная Осетия – Алания",
         "Ханты-Мансийский автономный округ - Югра": "Ханты-Мансийский автономный округ",
         "Ханты-Мансийский автономный округ –  Югра": "Ханты-Мансийский автономный округ"},
        inplace=True)

    districts_dict = {}

    for row in table.itertuples():
        if re.search(r"федераль", row.region, re.IGNORECASE):
            d = row.region
        else:
            districts_dict[row.region] = d

    table.insert(loc=1, column='federal_district',
                 value=table['region'].map(districts_dict))
    table = table[-table['federal_district'].isna()]

    return table


def cumsum_to_monthly_values(column_values):

    if column_values.notna().any():
        first_valid_idx = column_values.first_valid_index()
        first_valid_value = column_values[first_valid_idx]
        column_values = column_values.diff()
        column_values[first_valid_idx] = first_valid_value

    return column_values


def rearrange_columns(table):
    articles_columns = [col for col in table.columns if not re.search(
        r'region|federal_district|period_end|total|Строка\s+1\s*:', col)]
    # articles_columns = table.select_dtypes(include=['float64', 'int64']).columns
    table = pd.concat(
        [table[sorted([col for col in table.columns if not col in articles_columns])], table[sorted(articles_columns)]], axis=1)
    return table
