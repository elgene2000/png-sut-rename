from typing import Any, Dict, Optional


class Model:
    def __init__(self, model_attrs: Dict[str, Any] = None, from_db: bool = False):
        self.id: Optional[str] = None
        self.date_create: Optional[str] = None
        self.model_attrs = model_attrs or {}
        self.snapshot = {}
        self.from_db = from_db

    def to_dict(self, include_nested=False, only_modified=False):
        if only_modified is True and self.from_db is False:
            # we probably created this object ourselves, consider all fields modified
            only_modified = False
        model_dict = {}
        for key in self.__dict__.keys():
            value = getattr(self, key)
            if key in self.model_attrs:
                if only_modified is True:
                    # do not check modification status of nested objects
                    continue
                if include_nested is True:
                    if isinstance(value, list):
                        if len(value) == 0 or not isinstance(value[0], Model):
                            continue
                        model_dict[key] = [
                            x.to_dict(include_nested=include_nested) for x in value
                        ]
                    else:
                        if not isinstance(value, Model):
                            continue
                        model_dict[key] = value.to_dict(include_nested=include_nested)
            elif key == "model_attrs" or key == "snapshot" or key == "from_db":
                if include_nested is False:
                    continue
            else:
                if only_modified is True:
                    if value != self.snapshot.get(key, None):
                        model_dict[key] = value
                else:
                    model_dict[key] = value
        return model_dict

    def from_dict(self, data, snapshot: bool = True):
        if not data:
            return None
        for key in self.__dict__.keys():
            if key not in data:
                continue
            # should be turned into an object
            if key in self.model_attrs:
                # list of objects
                if isinstance(data[key], list):
                    objects = []
                    for obj in data[key]:
                        model_attr = self.model_attrs[key](from_db=self.from_db)
                        model_attr.from_dict(obj, snapshot=snapshot)
                        objects.append(model_attr)
                    setattr(self, key, objects)
                # single object
                elif data.get(key):
                    model_attr = self.model_attrs[key](from_db=self.from_db)
                    model_attr.from_dict(data[key], snapshot=snapshot)
                    setattr(self, key, model_attr)
                else:
                    setattr(self, key, None)
            # normal attribute, as it would be uploaded to DB
            else:
                setattr(self, key, data[key])
                if snapshot is True:
                    self.snapshot[key] = data[key]
