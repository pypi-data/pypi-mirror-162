import io
import avro.schema
import avro.io
import base64

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
class MonthDataAvroHelper:
    def __int__(self):
        pass

    def process(self, avro_base64_str):
        bytes_reader = io.BytesIO(base64.b64decode(avro_base64_str))
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(month_data_schema_parsed)
        return reader.read(decoder)
