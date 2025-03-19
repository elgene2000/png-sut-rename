from models.model import Model
from typing import Dict, Optional

class Platform(Model):
    def __init__(self, **kwargs):
        super().__init__()
        self.name: Optional[str] = None
        self.short_name: Optional[str] = None
        self.schema: Optional[Dict] = {}
        self.from_dict(kwargs)