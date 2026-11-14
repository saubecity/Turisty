from fastapi import FastAPI
from log import log_err, log_ok, log_info
import parser

from database import connection
from database import dataset
app = FastAPI(title="Turisty", version="1.0")

def main():
    parser.run()
    connection.init_schema()
    dataset.sync()

if __name__ == "__main__": main()
