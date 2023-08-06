import io
import avro.schema
import avro.io
import base64
from datetime import datetime
from datetime import timedelta

month_data_schema = '''
{
  "namespace": "io.gitbub.devlibx.avro",
  "type": "record",
  "name": "MonthDataAvro",
  "fields": [
    {
      "name": "days",
      "type": {
        "type": "map",
        "values": "int"
      }
    },
    {
      "name": "entity_id",
      "type": "string"
    }
  ]
}
'''

month_data_schema_parsed = avro.schema.parse(month_data_schema)


# This class helps to read avro object from given Base64 string
# noinspection PyMethodMayBeStatic
class MonthDataAvroHelper:
    def __int__(self):
        pass

    def process(self, avro_base64_str):
        bytes_reader = io.BytesIO(base64.b64decode(avro_base64_str))
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(month_data_schema_parsed)
        return reader.read(decoder)

    def process_and_return_last_n_days_from_time(self, time, avro_base64_str, days):
        data = self.process(avro_base64_str)
        print(data)
        days_to_add = self.get_last_n_days_keys(time, days)
        result = []
        for day in days_to_add:
            try:
                result.append(data["days"][day])
            except KeyError as error:
                pass
        return result

    def process_and_return_last_n_days(self, avro_base64_str, days):
        return self.process_and_return_last_n_days_from_time(datetime.now(), avro_base64_str, days)

    def get_last_n_days_keys(self, time, days):
        result = []
        end = time
        start = time - timedelta(days=days)
        while start < end:
            start = start + timedelta(days=1)
            result.append("{}-{}".format(start.month, start.day))
        return result

    def get_last_n_days_keys_from_now(self, days):
        time = datetime.now()
        return self.get_last_n_days_keys(time, days)
