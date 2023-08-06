### How to use

```python
from devlibx_avro_helper.month_data import MonthDataAvroHelper

input = "PAg4LTE23AEIOC0xN94BCDgtMTTYAQg4LTE12gEIOC0xOOABCDgtMTniAQg4LTMw"
        "+AEIOC0zMfoBCDgtMTLUAQg4LTEz1gEIOC0xMNABCDgtMTHSAQY5LTH8AQY5LTL"
        "+AQY5LTOAAgg4LTI38gEGOS00ggIGOC02yAEIOC0yOPQBBjgtN8oBCDgtMjXuAQY4LTjMAQg4LTI28AEGOC05zgEIOC0yOfYBCDgtMjDkAQg4LTIz6gEIOC0yNOwBCDgtMjHmAQg4LTIy6AEAEGhhcmlzaF8x "
helper = MonthDataAvroHelper()
result = helper.process(input)
print(result)

```