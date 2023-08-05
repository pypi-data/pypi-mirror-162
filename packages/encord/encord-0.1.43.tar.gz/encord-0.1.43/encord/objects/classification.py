from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Type, TypeVar

from encord.objects.common import (
    Attribute,
    _add_attribute,
    attribute_from_dict,
    attributes_to_list_dict,
)


@dataclass
class Classification:
    """
    This class is currently in BETA. Its API might change in future minor version releases.

    Represents a whole-image classification as part of Ontology structure. Wraps a single Attribute that describes
    the image in general rather then individual object.
    """

    uid: int
    feature_node_hash: str
    attributes: List[Attribute]

    @classmethod
    def from_dict(cls, d: dict) -> Classification:
        attributes_ret: List[Attribute] = list()
        for attribute_dict in d["attributes"]:
            attributes_ret.append(attribute_from_dict(attribute_dict))

        return Classification(
            uid=int(d["id"]),
            feature_node_hash=d["featureNodeHash"],
            attributes=attributes_ret,
        )

    def to_dict(self) -> dict:
        ret = dict()
        ret["id"] = str(self.uid)
        ret["featureNodeHash"] = self.feature_node_hash

        attributes_list = attributes_to_list_dict(self.attributes)
        if attributes_list:
            ret["attributes"] = attributes_list

        return ret

    T = TypeVar("T", bound=Attribute)

    def add_attribute(
        self,
        cls: Type[T],
        name: str,
        local_uid: Optional[int] = None,
        feature_node_hash: Optional[str] = None,
        required: bool = False,
    ) -> T:
        """
        Adds an attribute to the classification.

        Args:
            cls: attribute type, one of `RadioAttribute`, `ChecklistAttribute`, `TextAttribute`
            name: the user-visible name of the attribute
            local_uid: integer identifier of the attribute. Normally auto-generated;
                    omit this unless the aim is to create an exact clone of existing ontology
            feature_node_hash: global identifier of the attribute. Normally auto-generated;
                    omit this unless the aim is to create an exact clone of existing ontology
            required: whether the label editor would mark this attribute as 'required'

        Returns:
            the created attribute that can be further specified with Options, where appropriate

        Raises:
            ValueError: if the classification already has an attribute assigned
        """
        if self.attributes:
            raise ValueError("Classification should have exactly one root attribute")
        return _add_attribute(self.attributes, cls, name, [self.uid], local_uid, feature_node_hash, required)
