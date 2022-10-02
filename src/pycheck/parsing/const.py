"Constants related to parsing."
from enum import Enum


class TypeType(Enum):
    "Type of type."
    BaseType = "base_type"
    ListType = "list_type"
    RefinementType = "ref_type"
    ProductType = "prod_type"
    FuncType = "func_type"
