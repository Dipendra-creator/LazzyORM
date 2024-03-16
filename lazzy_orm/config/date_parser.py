from datetime import datetime


def parse_date(input_date):
    input_date = str(input_date).strip()
    formats = [
        '%Y-%b-%d',  # 2023-Jan-15
        '%d-%b-%Y',  # 15-Jan-2023
        '%b-%d-%Y',  # Jan-15-2023
        '%Y-%B-%d',  # 2023-January-15
        '%d-%B-%Y',  # 15-January-2023
        '%B-%d-%Y',  # January-15-2023

        '%y-%b-%d',  # 23-Jan-15
        '%d-%b-%y',  # 15-Jan-23
        '%b-%d-%y',  # Jan-15-23
        '%y-%B-%d',  # 23-January-15
        '%d-%B-%y',  # 15-January-23
        '%B-%d-%y',  # January-15-23

        '%Y/%b/%d',  # 2023/Jan/15
        '%d/%b/%Y',  # 15/Jan/2023
        '%b/%d/%Y',  # Jan/15/2023
        '%Y/%B/%d',  # 2023/January/15
        '%d/%B/%Y',  # 15/January/2023
        '%B/%d/%Y',  # January/15/2023

        '%y/%b/%d',  # 23/Jan/15
        '%d/%b/%y',  # 15/Jan/23
        '%b/%d/%y',  # Jan/15/23
        '%y/%B/%d',  # 23/January/15
        '%d/%B/%y',  # 15/January/23
        '%B/%d/%y',  # January/15/23
        '%Y-%m-%d',  # 2023-01-15
        '%d-%m-%Y',  # 15-01-2023
        '%y-%m-%d',  # 20-01-15
        '%d-%m-%y',  # 15-01-20
        '%Y/%m/%d',  # 2023/01/15
        '%d/%m/%Y',  # 15/01/2023
        '%y/%m/%d',  # 20/01/15
        '%d/%m/%y',  # 15/01/20

        '%b %d, %Y',  # Jan 15, 2023

        '%d %b %Y',  # 15 Jan 2023
        '%d %B %Y',  # 15 January 2023
        '%d %b, %Y',  # 15 Jan, 2023
        '%d %B, %Y',  # 15 January, 2023
        '%b %d, %y',  # Jan 15, 20

        '%d %b %y',  # 15 Jan 2023
        '%d %B %y',  # 15 January 20
        '%d %b, %y',  # 15 Jan, 20
        '%d %B, %y',  # 15 January, 20

        '%Y%m%d',  # 20230115
    ]

    try:
        for date_format in formats:
            try:
                formatted_date = datetime.strptime(input_date, date_format).date()

                if formatted_date is not None:
                    return formatted_date
                else:
                    raise Exception(f"Unable to parse date format {input_date}")
            except ValueError:
                pass
    except ValueError:
        raise ValueError("Unable to parse date format")
