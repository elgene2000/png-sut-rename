from typing import Dict, Optional

from models.model import Model
from models.platform import Platform

class SystemData(Model):
    def __init__(self, **kwargs):
        super().__init__(
            model_attrs=dict(
                platforms=Platform,
            )
        )
        self.username: Optional[str] = None
        self.scraped_data: Optional[Dict] = {}
        self.platform_config: Optional[Dict] = {}
        self.name: Optional[str] = None
        self.hostname_ip: Optional[str] = None
        self.platforms: Optional[Platform] = None
        self.from_dict(kwargs)
