import time

from sqlalchemy import create_engine

# def main():
#     while True:
#         try:
#             engine = create_engine('postgresql+psycopg2://dev:dev\
# @172.17.0.1:5432/dev')
#             conn = engine.connect()
#             print("Connected to database")
#             time.sleep(10)
#             break
#         except:
#             print("Couldn't connect to database, container still building, trying again in 5 seconds")
#             time.sleep(5)
#             continue


if __name__ == "__main__":
    time.sleep(25)
    # main()
