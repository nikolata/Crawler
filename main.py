import requests
from bs4 import BeautifulSoup
import sys
from database import session
from database import Base, engine
from model import Websites, Counter
from timeout import timeout
from try_functions import timeout_error, add_to_database, bulk_add_to_db
import settings
import time
import sqlalchemy
from sqlalchemy import and_


def show_histogram():
    all_servers = session.query(Websites.server).group_by(Websites.server).all()
    for server in all_servers:
        print(server[0])


def get_server(link):
    with timeout(seconds=10):
        try:
            r = requests.get(link)
            server = r.headers['Server']
            return server
        except TimeoutError:
            raise TimeoutError


def add_all_new_websites(website, parent):
    print(website)
    response = requests.get(website, timeout=10)
    try:
        html = response.content.decode('utf-8')
    except UnicodeDecodeError:
        print('GRUMNA')
        return
    soup = BeautifulSoup(html, 'html.parser')
    to_be_visited = []
    to_be_added = []
    for link in soup.find_all('a'):
        try:
            link_string = link.get('href')
        except requests.exceptions.ConnectionError:
            pass
        if link_string is not None:
            if 'http' in link_string and str(link_string) not in to_be_visited:
                try:
                    can_procede = True
                    server, can_procede = timeout_error(link_string)
                    if can_procede is True:
                        to_be_visited.append(link_string)
                        to_be_added.append(Websites(website_link=link_string, server=server, parent_id=parent))
                        print(link_string)
                except (requests.exceptions.ConnectionError, KeyError, requests.exceptions.InvalidSchema,
                        requests.exceptions.InvalidURL):
                    print('ERROR 2')
                    pass
            if 'link.php' in link_string and str(link_string) not in to_be_visited:
                try:
                    url = 'https://register.start.bg/'
                    link_string = url + link_string
                    can_procede = True
                    server, can_procede = timeout_error(link_string)
                    if can_procede is True:
                        to_be_visited.append(link_string)
                        to_be_added.append(Websites(website_link=link_string, server=server, parent_id=parent))
                        print(link_string)
                except (requests.exceptions.ConnectionError, KeyError, requests.exceptions.InvalidSchema,
                        requests.exceptions.InvalidURL):
                    pass
    print('WILL RETURN')
    return to_be_added
    # bulk_add_to_db(to_be_added)


# def start_crawling():
#     curr_id = session.query(Counter.curr_id).filter(Counter.counter_id == 1).first()
#     curr_link = session.query(Websites.website_link).filter(Websites.url_id == curr_id[0]).first()
#     response = requests.get(str(curr_link[0]), timeout=10)
#     current_id = curr_id[0]
#     try:
#         response.content.decode('utf-8')
#     except UnicodeDecodeError:
#         print('GRUMNA')
#         session.query(Counter).filter(Counter.counter_id == 1)\
#             .update({Counter.curr_id: current_id + 1}, synchronize_session=False)
#         session.commit()
#         return start_crawling()
#     while True:
#         current_parent_link = session.query(Websites.website_link).filter(Websites.url_id == current_id).first()
#         add_all_new_websites(current_parent_link[0], current_id)
#         session.query(Counter).filter(Counter.counter_id == 1)\
#             .update({Counter.curr_id: current_id + 1}, synchronize_session=False)
#         session.commit()
#         current_id += 1

def start_crawling():
    while True:
        try:
            current_id = session.query(Counter.curr_id).filter(Counter.counter_id == 1).first()
            current_id = current_id[0]
            websites = session.query(Websites)\
                .filter(and_(Websites.url_id >= current_id,
                             Websites.url_id <= current_id + 20,
                             Websites.used == 0)).all()
            current_id = current_id + 20
            session.query(Counter).filter(Counter.counter_id == 1)\
                .update({Counter.curr_id: current_id}, synchronize_session=False)
            session.commit()
            to_be_added = []
            for website in websites:
                try:
                    to_be_added.extend(add_all_new_websites(website.website_link, website.server))
                except TypeError:
                    print('vurna nishto')
                    pass
            print('FOR-A SVURSHI')
            while True:
                try:
                    bulk_add_to_db(to_be_added)
                    session.commit()
                    print('dobavih gi')
                    break
                except Exception:
                    print('error in bulk add')
                    time.sleep(5)
            for website in to_be_added:
                session.query(Websites).filter(Websites.website_link == website.website_link)\
                    .update({Websites.used: 1})
            session.commit()
        except sqlalchemy.exc.OperationalError:
            print('except')
            time.sleep(5)


#     print('vurtq se')
#     check = session.query(Terminals.is_ready).filter(Terminals.terminal_name == settings.CURRENT_TERMINAL).first()
#     if check[0] is True:
#         session.query(Terminals).filter(Terminals.terminal_name == settings.CURRENT_TERMINAL)\
#             .update({Terminals.is_ready: False}, synchronize_session=False)
#         session.commit()
#         all_links = session.query(ToBeVisited).filter(ToBeVisited.terminal_name == settings.CURRENT_TERMINAL).all()
#         for link in all_links:
#             print('zapochvam da tursq')
#             to_be_added = add_all_new_websites(link.website_link, link.parent_id)
#         session.query(Terminals).filter(Terminals.terminal_name == settings.CURRENT_TERMINAL)\
#             .update({Terminals.is_ready: True}, synchronize_session=False)
#         break
# while True:
#     check = session.query(Terminals.can_insert).filter(Terminals.terminal_name == settings.CURRENT_TERMINAL).first()
#     if check[0] is True:
#         bulk_add_to_db(to_be_added)
#         session.commit()
#         for link in to_be_added:
#             session.query(Websites).filter(Websites.website_link == link.website_link)\
#                 .update({Websites.used: True}, synchronize_session=False)
#             session.commit()
#         break
# start_crawling()

def add_starting_links(start, to_be_visited=[]):
    Base.metadata.create_all(engine)
    response = requests.get(start, timeout=10)
    html = response.content.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        try:
            link_string = link.get('href')
        except requests.exceptions.ConnectionError:
            pass
        if link_string is not None:
            if 'http' in link_string and str(link_string) not in to_be_visited:
                try:
                    can_procede = True
                    server, can_procede = timeout_error(link_string)
                    if can_procede is True:
                        to_be_visited = add_to_database(link_string, server, 0, to_be_visited)
                except (requests.exceptions.ConnectionError, KeyError, requests.exceptions.InvalidSchema,
                        requests.exceptions.InvalidURL):
                    pass
            if 'link.php' in link_string and str(link_string) not in to_be_visited:
                try:
                    url = 'https://register.start.bg/'
                    link_string = url + link_string
                    # r = requests.get(link_string)
                    # server = r.headers['Server']
                    can_procede = True
                    server, can_procede = timeout_error(link_string)
                    if can_procede is True:
                        to_be_visited = add_to_database(link_string, server, 0, to_be_visited)
                except (requests.exceptions.ConnectionError, KeyError, requests.exceptions.InvalidSchema,
                        requests.exceptions.InvalidURL):
                    pass
    session.close()


def main():
    command = sys.argv[1]
    if command == 'create':
        add_starting_links('https://register.start.bg/')
    elif command == 'start':
        try:
            settings.CURRENT_TERMINAL = sys.argv[2]
            #insert_terminal(settings.CURRENT_TERMINAL)
            start_crawling()
        except KeyboardInterrupt:
            session.commit()
            session.close()
    elif command == 'controller':
        controll()
    elif command == 'histogram':
        show_histogram()
    else:
        raise ValueError(f'Unknown command {command}. Valid ones are "create" and "start"')


if __name__ == '__main__':
    main()
