from app import app, db
from app.models import User, Activity, ActivityType
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Activity': Activity, 'ActivityType': ActivityType}
