"""
Extended codewriters.
"""

from typing import Optional

from pyavro_gen.codewriters.core import ClassWriter, Decorator, Extension, Method, Docstring, \
    Attribute, SimpleTypeClassWriter
from pyavro_gen.codewriters.utils import j

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class UndictifiableClassWriter(ClassWriter):
    """
    Codewriter to produce classes that can be "undictified".
    https://github.com/Dobiasd/undictify
    """

    def __init__(self,
                 fully_qualified_name: str,
                 doc: Optional[str] = None,
                 prefix: Optional[str] = None):
        super().__init__(fully_qualified_name, doc, prefix)

        self.decorators = [
            Decorator('@type_checked_constructor()',
                      ClassWriter('undictify.type_checked_constructor')),
            Decorator('@dataclass', ClassWriter('dataclasses.dataclass'))
        ]

        self.methods.append(Method(
            name='to_dict',
            parameters=[Attribute('self')],
            return_type=ClassWriter('typing.Dict'),
            doc=Docstring('Returns a dictionary version of this instance.'),
            body="return asdict(self)",
            additional_dependencies=[ClassWriter('dataclasses.asdict')]
        ))

        self.methods.append(Method(
            name='from_dict',
            parameters=[
                Attribute('cls'),
                Attribute(
                    name='the_dict',
                    type=ClassWriter('typing.Dict'),
                    doc=Docstring('The dictionary from which to create an instance of this class.')
                )
            ],
            return_type=SimpleTypeClassWriter(j("'", self.name, "'")),  # simple: no dep added
            doc=Docstring('Returns an instance of this class from a dictionary.'),
            body="return cls(**the_dict)",
            decorators=[Decorator('@classmethod')],
        ))


class DataClassWriter(ClassWriter):
    """
    Codewriter to write dataclasses.
    """

    def __init__(self,
                 fully_qualified_name: str,
                 doc: Optional[str] = None,
                 prefix: Optional[str] = None):
        super().__init__(fully_qualified_name, doc, prefix)

        self.decorators = [
            Decorator('@dataclass', ClassWriter('dataclasses.dataclass'))
        ]


class RpcWriter(ClassWriter):
    """
    Codewriter to write RPC protocols.
    """

    def __init__(self,
                 fully_qualified_name: str,
                 doc: Optional[str] = None,
                 prefix: Optional[str] = None):
        super().__init__(fully_qualified_name, doc, prefix)

        self.extensions = [
            Extension('abc.ABC')
        ]
