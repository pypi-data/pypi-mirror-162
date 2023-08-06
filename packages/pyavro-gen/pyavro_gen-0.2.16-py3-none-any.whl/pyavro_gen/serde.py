"""
This module is added as __init__.py of the main packages of generated classes.

It patches fastavro enum reader and writer to take enums as input (and return as output)
instead of strings.

Since it cannot know which enum class to return, we keep a dictionary of enum classes
found in the package and match them with the fully qualified domain of the avro schema,
during deserialization.
"""
import glob
import inspect
import struct
from importlib import import_module
from pathlib import Path
from typing import Dict, Optional, Union, Any, cast, Callable

import confluent_kafka.avro.serializer
import fastavro._read_py as fastavro_read  # pylint: disable=W0212
import fastavro._validation_py as fastavro_validation  # pylint: disable=W0212
import fastavro._write_py as fastavro_write  # pylint: disable=W0212
from avro.schema import Schema
from confluent_kafka.avro import CachedSchemaRegistryClient, loads  # pylint: disable=no-name-in-module
# pylint: disable=C0412
try:
    from confluent_kafka.avro.serializer import AvroSerializer, TopicNameStrategy, \
        AvroDeserializer, SerializerError, ContextStringIO, MAGIC_BYTE  # pylint: disable=no-name-in-module
except:
    from confluent_kafka.schema_registry import topic_subject_name_strategy as TopicNameStrategy  # pylint: disable=no-name-in-module
    from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer  # pylint: disable=no-name-in-module
    from confluent_kafka.avro.serializer import SerializerError  # pylint: disable=no-name-in-module
    from confluent_kafka.avro.serializer.message_serializer import ContextStringIO, MAGIC_BYTE  # pylint: disable=no-name-in-module
from fastavro._read_common import SchemaResolutionError  # pylint: disable=W0212
from fastavro._read_py import read_long  # pylint: disable=W0212
from fastavro._write_py import write_int  # pylint: disable=W0212

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

BASE_PACKAGE = '%%%base_package%%%'  # will be replaced

CLASSES: Dict[str, type] = {}

RESOLVED_NAMESPACE = Path(__file__).parent.resolve()
PACKAGE = RESOLVED_NAMESPACE.name.replace('/', '')
ROOT_DIR = str(RESOLVED_NAMESPACE.parent)
if not ROOT_DIR.endswith('/'):
    ROOT_DIR += '/'

for file in glob.iglob(str(RESOLVED_NAMESPACE) + '/**/__init__.py', recursive=True):
    module_name = str(Path(file).parent).replace(ROOT_DIR, '').replace('/', '.')
    module = import_module(module_name, PACKAGE)
    for _, class_type in inspect.getmembers(module, inspect.isclass):
        # Here we remove the base package.
        # Also, class module name is snake case, but classes are imported
        # in their packages' __init__.py so classes' module names have to be removed.
        # e.g.
        # from   'avroclasses.com.jaumo.schema.domain.user.gender.Gender'
        # to     'com.jaumo.schema.domain.user.Gender'
        class_module = class_type.__module__
        class_module_no_package = class_module[class_module.find('.') + 1:]
        if not class_module_no_package.startswith(BASE_PACKAGE):
            continue
        parent_class_module_no_package = \
            class_module_no_package[:class_module_no_package.rfind('.') + 1]
        fully_qualified_name = parent_class_module_no_package + class_type.__name__

        CLASSES[fully_qualified_name] = class_type
# for k, v in CLASSES.items():
#    print('loading class', k, v)


# pylint: disable=W0613
def my_validate_enum(datum, schema, **kwargs):  # type: ignore
    """
    Check that the data value matches one of the enum symbols.

    i.e "blue" in ["red", green", "blue"]

    Parameters
    ----------
    datum: Any
        Data being validated
    schema: dict
        Schema
    kwargs: Any
        Unused kwargs
    """
    return datum.value in schema['symbols']


# pylint: disable=C0103
def my_write_enum(fo, datum, schema):  # type: ignore
    """An enum is encoded by a int, representing the zero-based position of
    the symbol in the schema."""
    index = schema['symbols'].index(datum.value)
    write_int(fo, index)


# pylint: disable=C0103
def my_read_enum(fo, writer_schema, reader_schema=None):  # type: ignore
    """An enum is encoded by a int, representing the zero-based position of the
    symbol in the schema.
    """
    index = read_long(fo)
    symbol = writer_schema['symbols'][index]
    if reader_schema and symbol not in reader_schema['symbols']:
        default = reader_schema.get("default")
        if default:
            return default

        symlist = reader_schema['symbols']
        msg = '%s not found in reader symbol list %s' % (symbol, symlist)
        raise SchemaResolutionError(msg)

    klass_fully_qualified_name = writer_schema['name']
    klass = CLASSES[klass_fully_qualified_name]
    return klass(symbol)


fastavro_validation.VALIDATORS['enum'] = my_validate_enum
fastavro_write.WRITERS['enum'] = my_write_enum
fastavro_write.validate = fastavro_validation.validate
fastavro_read.READERS['enum'] = my_read_enum

confluent_kafka.avro.serializer.schemaless_writer = fastavro_write.schemaless_writer
confluent_kafka.avro.serializer.schemaless_reader = fastavro_read.schemaless_reader


# pylint: disable=R0903
class TypedAvroSerializer(AvroSerializer):  # type: ignore
    """
    Encodes kafka messages as Avro; registering the schema with the Confluent Schema Registry.

    :param registry_client CachedSchemaRegistryClient: Instance of CachedSchemaRegistryClient.
    :param bool is_key: True if configured as a key_serializer.
    :param func(str, bool, schema): Returns the subject name used when registering schemas.
    """

    def __init__(
            self,
            registry_client: CachedSchemaRegistryClient,
            is_key: bool = False,
            subject_strategy: Callable[[str, bool, Schema], str] = TopicNameStrategy
    ) -> None:
        super().__init__(registry_client, is_key, subject_strategy)

        self.class_name_to_schema: Dict[str, Schema] = {}

    def _get_parsed_schema(self, record: Any) -> Schema:
        klass = record.__class__
        class_name = klass.__module__ + '.' + klass.__name__
        if class_name in self.class_name_to_schema:
            return self.class_name_to_schema[class_name]

        parsed_schema = loads(record._schema)  # pylint: disable=W0212
        self.class_name_to_schema[class_name] = parsed_schema
        return parsed_schema

    def __call__(self, topic: str, record: Any) -> Optional[bytes]:
        """
        Given a parsed avro schema, encode a record for the given topic.

        The schema is registered with the subject of 'topic-value'.
        :param str topic: Topic name.
        :param Any record: An object to serialize.
        :returns: Encoded record with schema ID as bytes.
        :rtype: bytes
        """
        if record is None:
            return None

        schema = self._get_parsed_schema(record)

        subject = self.subject_strategy(topic, self.is_key, schema)

        schema_id = self.registry_client.register(subject, schema)
        if not schema_id:
            message = "Failed to register schema with subject {}.".format(subject)
            raise SerializerError(message, is_key=self.is_key)  # pylint: disable=unexpected-keyword-arg

        if schema_id not in self.codec_cache:
            self.codec_cache[schema_id] = self._get_encoder_func(schema)

        return cast(bytes, self._encode(schema_id, record.to_dict()))


# pylint: disable=R0903
class TypedAvroDeserializer(AvroDeserializer):  # type: ignore
    """
    Decodes Kafka messages encoded by Confluent Schema Registry compliant Avro Serializers.

    :param registry_client CachedSchemaRegistryClient: Instance of CachedSchemaRegistryClient.
    :param bool is_key: True if configured as a key_serializer.
    :param schema reader_schema: Optional reader schema to be used during deserialization.
    """

    def __init__(
            self,
            registry_client: CachedSchemaRegistryClient,
            is_key: bool = False,
            reader_schema: Optional[Schema] = None
    ) -> None:
        super().__init__(registry_client, is_key, reader_schema)

        self.schema_id_to_class: Dict[int, type] = {}

    def _get_class(self, schema_id: int) -> type:
        if schema_id in self.schema_id_to_class:
            return self.schema_id_to_class[schema_id]

        writer_schema: Schema = self.registry_client.get_by_id(schema_id)
        name = writer_schema.fullname
        self.schema_id_to_class[name] = CLASSES[name]
        return self.schema_id_to_class[name]

    def __call__(self, topic: str, datum: Union[str, bytes, None]) -> Any:
        """
        Decode a datum from kafka that has been encoded for use with the Confluent Schema Registry.
        :param str|bytes or None datum: message key or value to be decoded.
        :returns: Typed version of the decoded message key or value contents.
        """

        if datum is None:
            return None

        if len(datum) <= 5:
            raise SerializerError("message is too small to decode")

        with ContextStringIO(datum) as payload:
            magic, schema_id = struct.unpack('>bI', payload.read(5))
            if magic != MAGIC_BYTE:
                raise SerializerError("message does not start with magic byte", self.is_key)  # pylint: disable=too-many-function-args

            decoder_func = self._get_decoder_func(schema_id, payload)
            return self._get_class(schema_id).from_dict(decoder_func(payload))  # type: ignore
