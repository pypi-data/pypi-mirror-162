def create_action_row_component(components: list = []):
    """
    Create an action row component.
    components: list, list of components to add to the action row.
    """
    action_row_component = {
        "type": 1,
        "components": components
    }
    return action_row_component

def create_button_component(style: int = 1, label: str = "", emoji: dict = None, custom_id: str = "", url: str = "", disabled: bool = False):
    """
    Create a button component.
    style: int, the style of the button:
    1: primary
    2: secondary
    3: success
    4: danger
    5: link
    label: str, the label of the button.
    emoji: dict, the partial emoji of the button (id, name and animated).
    custom_id: str, the custom ID of the button.
    url: str, the url of the button.
    disabled: bool, whether the button is disabled or not.
    """
    button_component = {
        "type": 2,
        "style": style,
        "label": label,
        "emoji": emoji,
        "custom_id": custom_id,
        "url": url,
        "disabled": disabled
    }
    return button_component


def create_select_menu_component(custom_id: str = "", options: list = [], placeholder: str = "", min_values: int = 1, max_values: int = 1, disabled: bool = False):
    """
    Create a select menu component.
    custom_id: str, the custom ID of the select menu, max 100 characters.
    options: list, list of options to add to the select menu, max 25.
    placeholder: str, the placeholder of the select menu, max 150 characters.
    min_values: int, the minimum number of values to select (default: 1, min: 0, max: 25).
    max_values: int, the maximum number of values to select (default: 1, max: 25).
    disabled: bool, whether the select menu is disabled or not.
    """
    select_menu_component = {
        "type": 3,
        "custom_id": custom_id,
        "options": options,
        "placeholder": placeholder,
        "min_values": min_values,
        "max_values": max_values,
        "disabled": disabled
    }
    return select_menu_component


def create_select_option(label: str = "", value: str = "", description: str = "", emoji: dict = None, default: bool = False):
    """
    Create a select option.
    label: str, the label of the option, max 100 characters.
    value: str, the value of the option, max 100 characters.
    description: str, the description of the option, max 100 characters.
    emoji: dict, the partial emoji of the option (id, name and animated).
    default: bool, whether the option is default or not.
    """
    select_option = {
        "label": label,
        "value": value,
        "description": description,
        "emoji": emoji,
        "default": default
    }
    return select_option


def create_text_input_component(custom_id: str = "", style: int = 1, label: str = "", min_length: int = 0, max_length: int = 10, required: bool = True, value: str = "", placeholder: str = ""):
    """
    Create a text input component.
    custom_id: str, the custom ID of the text input, max 100 characters.
    style: int, the style of the text input:
    1: short
    2: paragraph
    label: str, the label of the text input, max 45 characters.
    min_length: int, the minimum length of the text input (default: 0, min: 0, max: 4000).
    max_length: int, the maximum length of the text input (default: 10, min: 1, max: 4000).
    required: bool, whether the text input is required or not.
    value: str, the value of the text input, max 4000 characters.
    placeholder: str, the placeholder of the text input, max 100 characters.
    """
    text_input_component = {
        "type": 4,
        "custom_id": custom_id,
        "style": style,
        "label": label,
        "min_length": min_length,
        "max_length": max_length,
        "required": required,
        "value": value,
        "placeholder": placeholder
    }
    return text_input_component