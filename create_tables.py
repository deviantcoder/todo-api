from core.database import engine
from models.task import Base


Base.metadata.create_all(bind=engine)
print('*** Tables created ***')
