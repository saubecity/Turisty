from fastapi import FastAPI
from log import log_err, log_ok, log_info, log_info

from database import connection

app = FastAPI(title="Turisty", version="1.0")

with connection.get_db() as conn:
    connection.init_schema(conn)
