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
from histogram import show_histogram, show_histogram_servers
import json
# from flask_display import display_json
from json2html import *


def get_server(link):
    with timeout(seconds=20):
        try:
            r = requests.get(link)
            server = r.headers['Server']
            return server
        except TimeoutError:
            raise TimeoutError


def add_all_new_websites(website, parent, counter):
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
                        print(counter, link_string)
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
                        print(counter, link_string)
                except (requests.exceptions.ConnectionError, KeyError, requests.exceptions.InvalidSchema,
                        requests.exceptions.InvalidURL):
                    pass
    print('WILL RETURN')
    return to_be_added


def start_crawling():
    while True:
        try:
            current_id = session.query(Counter.curr_id).filter(Counter.counter_id == 1).first()
            current_id = current_id[0]
            websites = session.query(Websites)\
                .filter(and_(Websites.url_id >= current_id,
                             Websites.url_id <= current_id + 5,
                             Websites.used == 0)).all()
            print(websites)
            current_id = current_id + 5
            session.query(Counter).filter(Counter.counter_id == 1)\
                .update({Counter.curr_id: current_id}, synchronize_session=False)
            session.commit()
            to_be_added = []
            counter = 0
            for website in websites:
                counter += 1
                try:
                    to_be_added.extend(add_all_new_websites(website.website_link, website.server, counter))
                except Exception:
                    print('vurna nishto')
                    pass
            print('FOR-A SVURSHI')
            if len(to_be_added) != 0:
                for website in to_be_added:
                    session.query(Websites).filter(Websites.website_link == website.website_link)\
                        .update({Websites.used: 1})
                session.commit()
                while True:
                    try:
                        bulk_add_to_db(to_be_added)
                        session.commit()
                        print('dobavih gi')
                        break
                    except Exception:
                        print('error in bulk add')
                        time.sleep(5)
        except sqlalchemy.exc.OperationalError:
            print('except')
            time.sleep(5)


def show_json(servers):
    infoFromJson = json.loads(servers)
    print(json2html.convert(json=infoFromJson))


def display_servers():
    all_servers = session.query(Websites.server).group_by(Websites.server).all()
    to_be_dumped = {}
    for server in all_servers:
        server_count = len(session.query(Websites).filter(Websites.server == server[0]).all())
        server_name = server[0]
        to_be_dumped.update({server_name: server_count})
    server_json = json.dumps(to_be_dumped, sort_keys=True, indent=4)
    return server_json


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
            start_crawling()
        except KeyboardInterrupt:
            session.commit()
            session.close()
    elif command == 'histogram':
        show_histogram()
    elif command == 'histogram_servers':
        show_histogram_servers()
    elif command == 'flask_servers':
        display_servers()
    else:
        raise ValueError(f'Unknown command {command}. Valid ones are "create" and "start"')


if __name__ == '__main__':
    main()
