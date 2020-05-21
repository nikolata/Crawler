import requests
from bs4 import BeautifulSoup
import sys
from database import session
from database import Base, engine
from model import Websites, Counter
from timeout import timeout
from try_functions import timeout_error, add_to_database


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
                        to_be_visited = add_to_database(link_string, server, parent, to_be_visited)
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
                        to_be_visited = add_to_database(link_string, server, parent, to_be_visited)
                except (requests.exceptions.ConnectionError, KeyError, requests.exceptions.InvalidSchema,
                        requests.exceptions.InvalidURL):
                    pass


def start_crawling():
    curr_id = session.query(Counter.curr_id).filter(Counter.counter_id == 1).first()
    curr_link = session.query(Websites.website_link).filter(Websites.url_id == curr_id[0]).first()
    response = requests.get(str(curr_link[0]), timeout=10)
    current_id = curr_id[0]
    try:
        response.content.decode('utf-8')
    except UnicodeDecodeError:
        print('GRUMNA')
        session.query(Counter).filter(Counter.counter_id == 1)\
            .update({Counter.curr_id: current_id + 1}, synchronize_session=False)
        session.commit()
        return start_crawling()
    while True:
        current_parent_link = session.query(Websites.website_link).filter(Websites.url_id == current_id).first()
        add_all_new_websites(current_parent_link[0], current_id)
        session.query(Counter).filter(Counter.counter_id == 1)\
            .update({Counter.curr_id: current_id + 1}, synchronize_session=False)
        session.commit()
        current_id += 1


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
    else:
        raise ValueError(f'Unknown command {command}. Valid ones are "create" and "start"')


if __name__ == '__main__':
    main()
