from typing import Optional, Union, List, Iterable

from discord import PartialEmoji, Emoji, InvalidArgument

from uuid import uuid1
from enum import IntEnum

__all__ = (
    "Component",
    "ButtonStyle",
    "Button",
    "Select",
    "SelectOption",
    "InputText",
    "InputOption",
    "ActionRow",
    "_get_component_type",
)


def _get_partial_emoji(emoji: Union[Emoji, PartialEmoji, str]) -> PartialEmoji:
    if isinstance(emoji, Emoji):
        return PartialEmoji(name=emoji.name, animated=emoji.animated, id=emoji.id)
    elif isinstance(emoji, PartialEmoji):
        return emoji
    elif isinstance(emoji, str):
        return PartialEmoji(name=emoji)


class Component:
    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_json(cls, data: dict):
        pass


class SelectOption(Component):
    __slots__ = ("_label", "_value", "_emoji", "_description", "_default")

    def __init__(
        self,
        *,
        label: str,
        value: str,
        emoji: Union[Emoji, PartialEmoji, str] = None,
        description: str = None,
        default: bool = False,
    ):
        self._label = label
        self._value = value
        self._description = description
        self._default = default

        if emoji is not None:
            self.emoji = _get_partial_emoji(emoji)
        else:
            self._emoji = None

    def to_dict(self) -> dict:
        data = {
            "label": self.label,
            "value": self.value,
            "description": self.description,
            "default": self.default,
        }
        if self.emoji is not None:
            data["emoji"] = self.emoji.to_dict()
        return data

    @property
    def label(self) -> str:
        return self._label

    @property
    def value(self) -> str:
        return self._value

    @property
    def emoji(self) -> Optional[PartialEmoji]:
        return self._emoji

    @property
    def description(self) -> str:
        return self._description

    @property
    def default(self) -> bool:
        return self._default

    @label.setter
    def label(self, value: str):
        if not len(value):
            raise InvalidArgument("Label must not be empty.")

        self._label = value

    @value.setter
    def value(self, value: str):
        self._value = value

    @emoji.setter
    def emoji(self, emoji: Union[Emoji, PartialEmoji, str]):
        self._emoji = _get_partial_emoji(emoji)

    @description.setter
    def description(self, value: str):
        self._description = value

    @default.setter
    def default(self, value: bool):
        self._default = value

    def set_label(self, value: str):
        self.label = value

    def set_value(self, value: str):
        self.value = value

    def set_emoji(self, emoji: Union[Emoji, PartialEmoji, str]):
        self.emoji = emoji

    def set_description(self, value: str):
        self.description = value

    def set_default(self, value: bool):
        self.default = value

    @classmethod
    def from_json(cls, data: dict):
        emoji = data.get("emoji")
        return cls(
            label=data.get("label"),
            value=data.get("value"),
            emoji=PartialEmoji(
                name=emoji["name"],
                animated=emoji.get("animated", False),
                id=emoji.get("id"),
            )
            if emoji
            else None,
            description=data.get("description"),
            default=data.get("default", False),
        )


class Select(Component):
    __slots__ = (
        "_id",
        "_options",
        "_placeholder",
        "_min_values",
        "_max_values",
        "_disabled",
    )

    def __init__(
        self,
        *,
        options: List[SelectOption],
        id: str = None,
        custom_id: str = None,
        placeholder: str = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
    ):
        if (not len(options)) or (len(options) > 25):
            raise InvalidArgument("Options length should be between 1 and 25.")

        self._id = id or custom_id or str(uuid1())
        self._options = options
        self._placeholder = placeholder
        self._min_values = min_values
        self._max_values = max_values
        self._disabled = disabled

    def to_dict(self) -> dict:
        return {
            "type": 3,
            "options": list(map(lambda option: option.to_dict(), self.options)),
            "custom_id": self.id,
            "placeholder": self.placeholder,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled,
        }

    @property
    def id(self) -> str:
        return self._id

    @property
    def custom_id(self) -> str:
        return self._id

    @property
    def options(self) -> List[SelectOption]:
        return self._options

    @property
    def placeholder(self) -> str:
        return self._placeholder

    @property
    def min_values(self) -> int:
        return self._min_values

    @property
    def max_values(self) -> int:
        return self._max_values

    @property
    def disabled(self) -> bool:
        return self._disabled

    @id.setter
    def id(self, value: str):
        self._id = value

    @custom_id.setter
    def custom_id(self, value: str):
        self._id = value

    @options.setter
    def options(self, value: List[SelectOption]):
        if (not len(value)) or (len(value) > 25):
            raise InvalidArgument("Options length should be between 1 and 25.")

        self._options = value

    @placeholder.setter
    def placeholder(self, value: str):
        self._placeholder = value

    @min_values.setter
    def min_values(self, value: int):
        self._min_values = value

    @max_values.setter
    def max_values(self, value: int):
        self._max_values = value

    @disabled.setter
    def disabled(self, value: bool):
        self._disabled = value

    def set_id(self, value: str):
        self.id = value

    def set_custom_id(self, value: str):
        self.custom_id = value

    def set_options(self, value: List[SelectOption]):
        self.options = value

    def set_placeholder(self, value: str):
        self.placeholder = value

    def set_min_values(self, value: int):
        self.min_values = value

    def set_max_values(self, value: int):
        self.max_values = value

    def set_disabled(self, value: bool):
        self.disabled = value

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            id=data.get("custom_id"),
            options=list(map(lambda x: SelectOption.from_json(x), data.get("options"))),
            placeholder=data.get("placeholder"),
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
            disabled=data.get("disabled", False),
        )


class ButtonStyle(IntEnum):
    blue = 1
    gray = 2
    grey = 2
    green = 3
    red = 4
    URL = 5

class InputOption(Component):
    __slots__ = ("_label", "_value", "_id", "_placeholder", "_min_length", "_max_length", "_style", "_required")

    def __init__(
        self,
        *,
        label: str = None,
        id : str = None,
        value: str = None,
        style : int = None,
        placeholder: str = None,
        min_length : int = None,
        max_length : int = None,
        required : bool = True,
    ):
        self._label = label
        self._id = id
        self._value = value
        self._style = style
        self._placeholder = placeholder
        self._min_length = min_length
        self._max_length = max_length
        self._required = required

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value

    @property
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value):
        self._placeholder = value

    @property
    def min_length(self):
        return self._min_length

    @min_length.setter
    def min_length(self, value):
        self._min_length = value

    @property
    def max_length(self):
        return self._max_length

    @max_length.setter
    def max_length(self, value):
        self._max_length = value

    @property
    def required(self):
        return self._required

    @required.setter
    def required(self, value):
        self._required = value

    def to_dict(self) -> dict:
        data = {
            "type": 1,
            "value": self.value,
            "components": [{
                "type": 4,
                "custom_id": self.id,
                "label": self.label,
                "style": self.style,
                "placeholder": self.placeholder,
                "required": self.required,
                "min_length": self.min_length,
                "max_length": self.max_length
            }]
        }
        return data

    @classmethod
    def from_dict(cls, data : dict):
        return cls(
            id = data.get("custom_id"),
            value = data.get("value")
        )

class InputText(Component):
    __slots__ = ("_title", "_id", "_options")

    def __init__(
        self,
        title: str = None,
        id : str = None,
        options : List[InputOption] = None
        ):
        self._title = title
        self._id = id
        self._options = options

    @property
    def title(self) -> str:
        return self._title

    @property
    def id(self) -> str:
        return self._id

    @property
    def options(self) -> List[InputOption]:
        return self._options

    @title.setter
    def title(self, value: str):
        self._title = value

    @id.setter
    def id(self, value: str):
        self._id = value

    @options.setter
    def options(self, value: List[SelectOption]):
        self._options = options

    def set_title(self, value: int):
        self._title = value

    def set_id(self, value: str):
        self._id = value

    def set_options(self, value: List[InputOption]):
        self.options = value

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            id=data.get("custom_id"),
            options=list(map(lambda x: InputOption.from_dict(x), data.get("components"))),
            title=data.get("title", "")
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "components": list(map(lambda option: option.to_dict(), self.options)),
            "custom_id": self.id,
        }

class Button(Component):
    __slots__ = ("_style", "_label", "_id", "_url", "_disabled", "_emoji")

    def __init__(
        self,
        *,
        label: str = None,
        style: int = ButtonStyle.gray,
        id: str = None,
        custom_id: str = None,
        url: str = None,
        disabled: bool = False,
        emoji: Union[Emoji, PartialEmoji, str] = None,
    ):

        self._style = style
        self._label = label
        self._url = url
        self._disabled = disabled

        if emoji is not None:
            self._emoji = _get_partial_emoji(emoji)
        else:
            self._emoji = None

        if not self.style == ButtonStyle.URL:
            self._id = id or custom_id or str(uuid1())
        else:
            self._id = None

    def to_dict(self) -> dict:
        data = {
            "type": 2,
            "style": self.style,
            "label": self.label,
            "custom_id": self.id,
            "url": self.url if self.style == ButtonStyle.URL else None,
            "disabled": self.disabled,
        }
        if self.emoji:
            data["emoji"] = self.emoji.to_dict()
        return data

    @property
    def style(self) -> int:
        return self._style

    @property
    def label(self) -> str:
        return self._label

    @property
    def id(self) -> str:
        return self._id

    @property
    def custom_id(self) -> str:
        return self._id

    @property
    def url(self) -> Optional[str]:
        return self._url

    @property
    def disabled(self) -> bool:
        return self._disabled

    @property
    def emoji(self) -> PartialEmoji:
        return self._emoji

    @style.setter
    def style(self, value: int):
        if value == ButtonStyle.URL and self.id:
            raise InvalidArgument("Both ID and URL are set.")
        if not (1 <= value <= ButtonStyle.URL):
            raise InvalidArgument(f"Style must be between 1, {ButtonStyle.URL}.")

        self._style = value

    @label.setter
    def label(self, value: str):
        if not value and not self.emoji:
            raise InvalidArgument("Label should not be empty.")

        self._label = value

    @url.setter
    def url(self, value: str):
        if value and self.style != ButtonStyle.URL:
            raise InvalidArgument("Button style is not URL. You shouldn't provide URL.")

        self._url = value

    @id.setter
    def id(self, value: str):
        if self.style == ButtonStyle.URL:
            raise InvalidArgument(
                "Button style is set to URL. You shouldn't provide ID."
            )

        self._id = value

    @custom_id.setter
    def custom_id(self, value: str):
        if self.style == ButtonStyle.URL:
            raise InvalidArgument(
                "Button style is set to URL. You shouldn't provide ID."
            )

        self._id = value

    @disabled.setter
    def disabled(self, value: bool):
        self._disabled = value

    @emoji.setter
    def emoji(self, emoji: Union[Emoji, PartialEmoji, str]):
        self._emoji = _get_partial_emoji(emoji)

    def set_style(self, value: int):
        self.style = value

    def set_label(self, value: int):
        self.label = value

    def set_url(self, value: int):
        self.url = value

    def set_id(self, value: str):
        self.id = value

    def set_custom_id(self, value: str):
        self.custom_id = value

    def set_disabled(self, value: bool):
        self.disabled = value

    def set_emoji(self, emoji: Union[Emoji, PartialEmoji, str]):
        self.emoji = emoji

    @classmethod
    def from_json(cls, data: dict):
        emoji = data.get("emoji")
        return cls(
            style=data.get("style"),
            label=data.get("label"),
            id=data.get("custom_id"),
            url=data.get("url"),
            disabled=data.get("disabled", False),
            emoji=PartialEmoji(
                name=emoji["name"],
                animated=emoji.get("animated", False),
                id=emoji.get("id"),
            )
            if emoji
            else None,
        )


class ActionRow(Component):
    __slots__ = ("_components",)

    def __init__(self, *args: List[Component]):
        self._components = list(args) if args is not None else []

    def disable_components(self) -> List[Component]:
        def disable(component: Component):
            component.disabled = True
            return component

        self._components = list(map(disable, self._components))
        return self

    def __list__(self) -> List[Component]:
        return self.components

    def __len__(self) -> int:
        return len(self.components)

    def __iter__(self) -> Iterable[Component]:
        return iter(self.components)

    def __getitem__(self, index: int) -> Component:
        return self.components[index]

    def __setitem__(self, index: int, value: Component):
        self._components[index] = value

    def __delitem__(self, index: int):
        del self._components[index]

    def to_dict(self) -> dict:
        data = {
            "type": 1,
            "components": [component.to_dict() for component in self.components],
        }
        return data

    def append(self, component: Component):
        self.components.append(component)

    @property
    def components(self) -> List[Component]:
        return self._components

    @components.setter
    def components(self, value: List[Component]):
        self._components = value

    def set_components(self, value: List[Component]):
        self.components = value

    def add_component(self, value: Component):
        self.components.append(value)

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            *[Button.from_json(component) for component in data.get("components")]
        )


def _get_component_type(type: int):
    return {1: ActionRow, 2: Button, 3: Select, 4: InputText}[type]
