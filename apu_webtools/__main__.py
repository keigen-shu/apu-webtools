from __future__ import absolute_import
from apuws.app import app
import os

host = None
port = None

if 'PORT' in os.environ:
    host = '0.0.0.0'
    port = int(os.environ['PORT'])

app.run(host=host, port=port, debug=True)
