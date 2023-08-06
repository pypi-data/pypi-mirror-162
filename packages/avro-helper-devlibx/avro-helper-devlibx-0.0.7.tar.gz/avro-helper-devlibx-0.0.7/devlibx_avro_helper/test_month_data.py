import unittest
from datetime import datetime

from devlibx_avro_helper.month_data import MonthDataAvroHelper


class TestingMonthDataAvroHelper(unittest.TestCase):

    def test_parsing(self):
        base64Str = "BgY3LTMCBjYtNgIGNy01BAAAAAI="
        helper = MonthDataAvroHelper()
        result = helper.process(base64Str)
        print(result)
        self.assertEqual(2, result["days"]["7-5"], "It should be 2")

        base64Str = "Ogg3LTI1CAg3LTI0CAg3LTI3Bgg3LTI2CAg3LTI5Bgg3LTI4CAg3LTIxCAg3LTIwCAg3LTIzCAg3LTIyBgY4LTEGBjgtMgYGOC0zCAY4LTQICDctMTQIBjgtNQgINy0xMwgGOC02sA4INy0xNgYGNy05CAg3LTE1Bgg3LTE4CAg3LTE3Bgg3LTE5CAg3LTMwCAg3LTEwBgg3LTMxCAg3LTEyCAg3LTExBgAAAAI="
        result = helper.process(base64Str)
        print(result)
        self.assertEqual(4, result["days"]["7-25"], "It should be 4")
        self.assertEqual(29, len(result["days"]), "It should be 30")

        base64Str = "Ogg3LTI1Sgg3LTI0SAg3LTI3Rgg3LTI2Sgg3LTI5Rgg3LTI4Sgg3LTIxSgg3LTIwTAg3LTIzSgg3LTIyRgY4LTFIBjgtMkYGOC0zSgY4LTRMCDctMTRIBjgtNUoINy0xM0wGOC028A4INy0xNkYGNy05Sgg3LTE1SAg3LTE4Sgg3LTE3SAg3LTE5SAg3LTMwSAg3LTEwSAg3LTMxSgg3LTEySgg3LTExRgAAAAI="
        result = helper.process(base64Str)
        print(result)
        self.assertEqual(37, result["days"]["7-25"], "It should be 37")
        self.assertEqual(29, len(result["days"]), "It should be 30")

        base64Str = "PAg3LTI1zgIINy0yNNACCDctMjfKAgg3LTI20AIINy0yOcQCCDctMjjQAgg3LTIxwAIINy0yMNACCDctMjO4Agg3LTIyxAIGOC0xygIGOC0yzgIGOC0zsAIGOC00wAIINy0xNM4CBjgtNcACCDctMTO8AgY4LTa6Agg3LTE2xAIGOC03xgIGNy05yAIINy0xNcICCDctMTjGAgg3LTE3ugIINy0xOc4CCDctMzC0Agg3LTEwwAIINy0zMboCCDctMTLQAgg3LTExvgIAAAAC"
        result = helper.process(base64Str)
        print(result)
        self.assertEqual(30, len(result["days"]), "It should be 30")

    def test_parsing_from_base64(self):
        base64Str = "PAg3LTI1zgIINy0yNNACCDctMjfKAgg3LTI20AIINy0yOcQCCDctMjjQAgg3LTIxwAIINy0yMNACCDctMjO4Agg3LTIyxAIGOC0xygIGOC0yzgIGOC0zsAIGOC00wAIINy0xNM4CBjgtNcACCDctMTO8AgY4LTa6Agg3LTE2xAIGOC03xgIGNy05yAIINy0xNcICCDctMTjGAgg3LTE3ugIINy0xOc4CCDctMzC0Agg3LTEwwAIINy0zMboCCDctMTLQAgg3LTExvgIAAAAC"
        helper = MonthDataAvroHelper()
        result = helper.process(base64Str)
        print(result)
        self.assertEqual(162, result["days"]["7-29"], "It should be 157")

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


if __name__ == '__main__':
    unittest.main()
