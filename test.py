from app.db.session import engine
from app.models.deployment import Deployment as DBDeployment
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

deployment_id = 1  # Replace with a valid deployment ID

deployment = session.query(DBDeployment).filter(DBDeployment.id == deployment_id).first()
print(deployment)