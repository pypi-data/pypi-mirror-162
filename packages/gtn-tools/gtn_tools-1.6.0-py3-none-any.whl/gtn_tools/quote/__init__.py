import os
from typing import Union
from .Doc import Editable, Uneditable
from .Quote import QuoteClass as Quote  # noqa


# return Editable or Uneditable Document
def Document(path) -> Union[Editable, Uneditable]:
    """
    Initialize Document Class
    """
    type = os.path.splitext(path)[1].replace('.', '').upper()
    if type in ['DOCX', 'DOC', 'PPTX', 'PPT']:
        return Editable(path)
    elif type in ['PDF', 'JPG']:
        return Uneditable(path)
