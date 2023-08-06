def create_attachment(id: int = 0, description: str = "", filename: str = ""):
    """
    Create an attachment object.
    id: int, id of the attachment
    description: str, description of the attachment
    filename: str, filename of the attachment
    """
    attachment = {
        "id": id,
        "description": description,
        "filename": filename
    }
    return attachment