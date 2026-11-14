import argparse
from log import log_info
from database import database

def parse_args():
    parser = argparse.ArgumentParser(description="Turisty backend")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Deletes all touristy's stored data before launching it (clean start)"
    )
    return parser.parse_args()

def run():
    args = parse_args()
    if args.reset:
        database.remove()
        log_info("Removing saved data")
