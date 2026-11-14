from fastapi import FastAPI
from log import log_err, log_ok, log_info
import parser

from database import connection
app = FastAPI(title="Turisty", version="1.0")

def main():
    parser.run()
    connection.init_schema()

if __name__ == "__main__": main()
