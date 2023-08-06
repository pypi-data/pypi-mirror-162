from dataclasses import dataclass


@dataclass
class ButtonEntity:
    url: str
    label: str
    classname: str
    title: str

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if "__" not in k}
