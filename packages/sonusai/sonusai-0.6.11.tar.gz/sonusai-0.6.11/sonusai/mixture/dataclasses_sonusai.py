from dataclasses_json import DataClassJsonMixin


class DataClassSonusAIMixin(DataClassJsonMixin):
    from typing import Dict
    from typing import Union

    # Json type defined to maintain compatibility with DataClassJsonMixin
    Json = Union[dict, list, str, int, float, bool, None]

    def __str__(self):
        return f'{self.to_dict()}'

    # Override DataClassJsonMixin to remove dictionary keys with values of None
    def to_dict(self, encode_json=False) -> Dict[str, Json]:
        def del_none(d):
            if isinstance(d, dict):
                for key, value in list(d.items()):
                    if value is None:
                        del d[key]
                    elif isinstance(value, dict):
                        del_none(value)
                    elif isinstance(value, list):
                        for item in value:
                            del_none(item)
            elif isinstance(d, list):
                for item in d:
                    del_none(item)
            return d

        return del_none(super().to_dict(encode_json))
