### How to use

```python
from devlibx_avro_helper.month_data import MonthDataAvroHelper

input = "PAg4LTE23AEIOC0xN94BCDgtMTTYAQg4LTE12gEIOC0xOOABCDgtMTniAQg4LTMw"
"+AEIOC0zMfoBCDgtMTLUAQg4LTEz1gEIOC0xMNABCDgtMTHSAQY5LTH8AQY5LTL"
"+AQY5LTOAAgg4LTI38gEGOS00ggIGOC02yAEIOC0yOPQBBjgtN8oBCDgtMjXuAQY4LTjMAQg4LTI28AEGOC05zgEIOC0yOfYBCDgtMjDkAQg4LTIz6gEIOC0yNOwBCDgtMjHmAQg4LTIy6AEAEGhhcmlzaF8x "
helper = MonthDataAvroHelper()
result = helper.process(input)
print(result)

# Result
# {'days': {'8-16': 110, '8-17': 111, '8-14': 108, '8-15': 109, '8-18': 112, '8-19': 113, '8-30': 124, '8-31': 125, '8-12': 106, '8-13': 107, '8-10': 104, '8-11': 105, '9-1': 126, '9-2': 127, '9-3': 128, '8-27': 121, '9-4': 129, '8-6': 100, '8-28': 122, '8-7': 101, '8-25': 119, '8-8': 102, '8-26': 120, '8-9': 103, '8-29': 123, '8-20': 114, '8-23': 117, '8-24': 118, '8-21': 115, '8-22': 116}, 'entity_id': 'harish_1'}
```

### Get last N days data

In this example we would have data in base 64 encoding. We will get last 29 nad 7
days data from.

```python
# How to use - the full example is given below
from devlibx_avro_helper.month_data import MonthDataAvroHelper

helper = MonthDataAvroHelper()
result = helper.process_and_return_last_n_days_from_time(date_time_obj, base64Str, 30)
```

```python
from devlibx_avro_helper.month_data import MonthDataAvroHelper
from datetime import datetime


def test_collect_data_for_n_days(self):
    base64Str = "PAg3LTI1zgIINy0yNNACCDctMjfKAgg3LTI20AIINy0yOcQCCDctMjjQAgg3LTIxwAIINy0yMNACCDctMjO4Agg3LTIyxAIGOC0xygIGOC0yzgIGOC0zsAIGOC00wAIINy0xNM4CBjgtNcACCDctMTO8AgY4LTa6Agg3LTE2xAIGOC03xgIGNy05yAIINy0xNcICCDctMTjGAgg3LTE3ugIINy0xOc4CCDctMzC0Agg3LTEwwAIINy0zMboCCDctMTLQAgg3LTExvgIAAAAC"

    date_time_str = '07/08/22 01:55:19'
    date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
    
    helper = MonthDataAvroHelper()
    result = helper.process_and_return_last_n_days_from_time(date_time_obj, base64Str, 30)
    self.assertEqual(30, len(result))
    print("result of test_collect_data_for_n_days 30 days", result)
    
    result = helper.process_and_return_last_n_days_from_time(date_time_obj, base64Str, 7)
    self.assertEqual(7, len(result))
    print("result of test_collect_data_for_n_days 7 days", result)
```