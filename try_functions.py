from timeout import timeout
import requests
from database import session
from model import Websites
import sqlalchemy


def get_server(link):
    with timeout(seconds=10):
        try:
            r = requests.get(link)
            server = r.headers['Server']
            return server
        except TimeoutError:
            raise TimeoutError


def timeout_error(link):
    try:
        server = get_server(link)
        return server, True
    except TimeoutError:
        return False, False


def add_to_database(link_string, server, parent, to_be_visited):
    try:
        session.add(Websites(website_link=link_string, server=server, parent_id=parent))
        session.commit()
        to_be_visited.append(link_string)
        print(link_string)
        return to_be_visited
    except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
        print('this website is already added')
        session.rollback()
        return to_be_visited


#     try:
#         can_procede = True
#         try:
#             server = get_server(link_string)
#         except TimeoutError:
#             can_procede = False
#         if can_procede is True:
#             try:
#                 session.add(Websites(website_link=link_string, server=server, parent_id=parent))
#                 session.commit()
#                 to_be_visited.append(link_string)
#                 print(link_string)
#             except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
#                 print('this website is already added')
#                 session.rollback()
#                 pass

# try:
#     server = get_server(link_string)
# except TimeoutError:
#     can_procede = False
# if can_procede is True:
#     try:
#         session.add(Websites(website_link=link_string, server=server, parent_id=parent))
#         session.commit()
#         to_be_visited.append(link_string)
#         print(link_string)
#     except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
#         session.rollback()
#         print('this website is already added')
#         pass