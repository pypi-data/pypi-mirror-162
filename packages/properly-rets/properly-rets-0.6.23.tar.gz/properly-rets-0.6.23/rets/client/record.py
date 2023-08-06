from typing import Sequence

from rets.http import Object


class Record:

    def __init__(self, resource_class, data: dict):
        # Check if the reported primary key is in the data
        if resource_class.resource.key_field in data:
            self.resource_key = str(data[resource_class.resource.key_field])
        else:
            # If it is not, use the capitalized version. This is probably a hack.
            self.resource_key = str(data[resource_class.resource.key_field.capitalize()])

        self.resource = resource_class.resource
        self.resource_class = resource_class
        self.data = data

    def get_objects(self, name: str, **kwargs) -> Sequence[Object]:
        resource_object = self.resource.get_object_type(name)
        return resource_object.get(self.resource_key, **kwargs)

    def __repr__(self) -> str:
        return '<Record: %s:%s:%s>' % (
            self.resource_class.resource.name,
            self.resource_class.name,
            self.resource_key,
        )
