from app.database import engine
from app.models import Base
from app.models.user_dashboard_config import UserDashboardConfig
Base.metadata.create_all(bind=engine)
print('Tables created successfully')
