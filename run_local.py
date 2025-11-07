# run_local.py
# Lightweight runner that injects a safe mock for routeros_api if needed
# Usage: set env MOCK_ROUTEROS=1 to force mock (we set it in the runner below)

import sys
import types
import os

# Force mock in this runner to avoid network dependency
os.environ.setdefault('MOCK_ROUTEROS', '1')

if os.environ.get('MOCK_ROUTEROS') == '1':
    mock = types.ModuleType('routeros_api')
    class RouterOsApiPool:
        def __init__(self, *args, **kwargs):
            pass
        def get_api(self):
            return self
        # app expects api.get_resource(...).get()
        def get_resource(self, path):
            return self
        def get(self):
            # return empty list for active users
            return []
        def disconnect(self):
            pass
    mock.RouterOsApiPool = RouterOsApiPool
    sys.modules['routeros_api'] = mock

# Import Flask app after mocking
from app import app

if __name__ == '__main__':
    print("Starting Flask app with MOCK_ROUTEROS=1 — MikroTik calls are mocked.")
    # Bind to 0.0.0.0 so bisa diakses dari perangkat lain juga (tetap aman untuk dev)
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
