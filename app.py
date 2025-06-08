import os
from app import create_app, db
from app.models import User, Region, DisasterType, ReliefRequest, AuditLog

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Region': Region,
        'DisasterType': DisasterType,
        'ReliefRequest': ReliefRequest,
        'AuditLog': AuditLog
    }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)