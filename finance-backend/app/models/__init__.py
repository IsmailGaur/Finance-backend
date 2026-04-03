# Expose models so they are imported before Base.metadata.create_all()
from app.models.user_model import User            # noqa: F401
from app.models.record_model import FinancialRecord  # noqa: F401
