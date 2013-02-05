from __future__ import absolute_import
from apu_webtools.app import app
import os

app.run(port=os.environ['PORT'])
