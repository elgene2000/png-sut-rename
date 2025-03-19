import models
from backend import SystemData
from database.database import DatabaseController

SYSTEM_DATA_DB_CONTROLLER = DatabaseController(
    model=models.SystemData, endpoint=SystemData()
)
