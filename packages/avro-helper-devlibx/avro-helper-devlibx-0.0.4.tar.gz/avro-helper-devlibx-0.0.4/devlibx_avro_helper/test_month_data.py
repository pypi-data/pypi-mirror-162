import unittest
from datetime import datetime

from devlibx_avro_helper.month_data import MonthDataAvroHelper


class TestingMonthDataAvroHelper(unittest.TestCase):

    def test_parsing_from_base64(self):
        base64Str = "PAg4LTE23AEIOC0xN94BCDgtMTTYAQg4LTE12gEIOC0xOOABCDgtMTniAQg4LTMw" \
                    "+AEIOC0zMfoBCDgtMTLUAQg4LTEz1gEIOC0xMNABCDgtMTHSAQY5LTH8AQY5LTL" \
                    "+AQY5LTOAAgg4LTI38gEGOS00ggIGOC02yAEIOC0yOPQBBjgtN8oBCDgtMjXuAQY4LTjMAQg4LTI28AEGOC05zgEIOC0yOfYBCDgtMjDkAQg4LTIz6gEIOC0yNOwBCDgtMjHmAQg4LTIy6AEAEGhhcmlzaF8x "
        helper = MonthDataAvroHelper()
        result = helper.process(base64Str)
        print(result)
        self.assertEqual(110, result["days"]["8-16"], "It should be 110")

    def test_get_last_n_days_keys(self):
        date_time_str = '05/08/22 01:55:19'
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
        helper = MonthDataAvroHelper()
        results = helper.get_last_n_days_keys(date_time_obj, 30)
        print(results)
        self.assertEqual(30, len(results))
        self.assertEqual("7-7", results[0])
        self.assertEqual("8-5", results[29])

    def test_collect_data_for_n_days(self):
        base64Str = "PAg4LTE23AEIOC0xN94BCDgtMTTYAQg4LTE12gEIOC0xOOABCDgtMTniAQg4LTMw" \
                    "+AEIOC0zMfoBCDgtMTLUAQg4LTEz1gEIOC0xMNABCDgtMTHSAQY5LTH8AQY5LTL" \
                    "+AQY5LTOAAgg4LTI38gEGOS00ggIGOC02yAEIOC0yOPQBBjgtN8oBCDgtMjXuAQY4LTjMAQg4LTI28AEGOC05zgEIOC0yOfYBCDgtMjDkAQg4LTIz6gEIOC0yNOwBCDgtMjHmAQg4LTIy6AEAEGhhcmlzaF8x "

        date_time_str = '03/09/22 01:55:19'
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')

        helper = MonthDataAvroHelper()
        result = helper.process_and_return_last_n_days_from_time(date_time_obj, base64Str, 30)
        self.assertEqual(29, len(result))
        print("result of test_collect_data_for_n_days 30 days", result)

        result = helper.process_and_return_last_n_days_from_time(date_time_obj, base64Str, 7)
        self.assertEqual(7, len(result))
        print("result of test_collect_data_for_n_days 7 days", result)


if __name__ == '__main__':
    unittest.main()
