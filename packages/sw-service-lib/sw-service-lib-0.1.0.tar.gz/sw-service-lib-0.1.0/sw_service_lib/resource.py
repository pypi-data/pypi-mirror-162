from __future__ import annotations
from enum import Enum
from typing import List


class ResourceConfigurationValueType(Enum):
    BOOL = "BOOL"
    STRING = "STRING"
    SECURE = "SECURE"
    INT = "INT"
    JSON = "JSON"
    DATE = "DATE"
    FLOAT = "FLOAT"


class ResourceConfiguration:
    def __init__(
        self,
        key: str = None,
        config_type: str = None,
        is_editable: bool = None,
        value=None,
    ) -> None:
        self.key = key
        self.config_type = config_type
        self.is_editable = is_editable
        self.value = value

    @classmethod
    def from_dict(cls, d: dict) -> ResourceConfiguration:
        r = ResourceConfiguration()
        r.key = d["key"]
        r.config_type = d["type"]
        r.is_editable = d["isEditable"]
        if r.config_type == ResourceConfigurationValueType.BOOL:
            r.value = d["valueBool"]
        elif r.config_type == ResourceConfigurationValueType.STRING:
            r.value = d["valueString"]
        elif r.config_type == ResourceConfigurationValueType.SECURE:
            r.value = d["valueSecure"]
        elif r.config_type == ResourceConfigurationValueType.INT:
            r.value = d["valueInt"]
        elif r.config_type == ResourceConfigurationValueType.JSON:
            r.value = d["valueJson"]
        elif r.config_type == ResourceConfigurationValueType.DATE:
            r.value = d["valueDate"]
        elif r.config_type == ResourceConfigurationValueType.FLOAT:
            r.value = d["valueFloat"]            
        return r


class Resource:
    def __init__(
        self,
        resource_configurations: List[ResourceConfiguration]=[],
        id: str = None,
        slug: str = None,
        name: str = None,
    ) -> None:
        self.resource_configurations = resource_configurations
        self.id = id
        self.slug = slug
        self.name = name

    @classmethod
    def from_dict(cls, res: dict) -> Resource:
        r = Resource()
        r.id = res["resource"]["id"]
        r.slug = res["resource"]["slug"]
        r.name = res["resource"]["name"] 
        if "configuration" in res:
            for c in res["configuration"]:
                r.resource_configurations.append(ResourceConfiguration.from_dict(c))
        return r
