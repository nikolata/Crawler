import requests
from bs4 import BeautifulSoup
import sys
from database import session
from database import Base, engine
from model import Websites, Counter
import sqlalchemy


def show_histogram():
    all_servers = session.query(Websites.server).group_by(Websites.server).all()
    for server in all_servers:
        print(server[0])


def add_all_new_websites(website, parent):
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
                    r = requests.get(link_string)
                    server = r.headers['Server']
                    try:
                        session.add(Websites(website_link=link_string, server=server, parent_id=parent))
                        session.commit()
                        to_be_visited.append(link_string)
                    except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
                        pass
                except (requests.exceptions.ConnectionError, KeyError):
                    pass
                print(link_string)
            if 'link.php' in link_string and str(link_string) not in to_be_visited:
                try:
                    url = 'https://register.start.bg/'
                    link_string = url + link_string
                    r = requests.get(link_string)
                    server = r.headers['Server']
                    try:
                        session.add(Websites(website_link=link_string, server=server, parent_id=parent))
                        session.commit()
                        to_be_visited.append(link_string)
                    except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
                        pass
                except (requests.exceptions.ConnectionError, KeyError):
                    pass
                print(link_string)
    session.close()
    return


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
        return start_crawling()
    websites = session.query(Websites).all()
    all_links = [w.website_link for w in websites if w.url_id >= current_id]
    for link in all_links:
        add_all_new_websites(link, current_id)
        session.query(Counter).filter(Counter.counter_id == 1)\
            .update({Counter.curr_id: current_id + 1}, synchronize_session=False)
        current_id += 1
        if len(all_links) - current_id <= 10:
            all_links = [w.website_link for w in websites if w.url_id >= current_id]


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
                    r = requests.get(link_string)
                    server = r.headers['Server']
                    session.add(Websites(website_link=link_string, server=server, parent_id=0))
                    session.commit()
                except (requests.exceptions.ConnectionError, KeyError):
                    pass
                print(link_string)
            if 'link.php' in link_string and str(link_string) not in to_be_visited:
                try:
                    url = 'https://register.start.bg/'
                    link_string = url + link_string
                    r = requests.get(link_string)
                    server = r.headers['Server']
                    session.add(Websites(website_link=link_string, server=server, parent_id=0))
                    session.commit()
                except (requests.exceptions.ConnectionError, KeyError):
                    pass
                print(link_string)
    session.close()


def main():
    command = sys.argv[1]
    if command == 'create':
        add_starting_links('https://register.start.bg/')
    elif command == 'start':
        start_crawling()
    elif command == 'histogram':
        show_histogram()
    else:
        raise ValueError(f'Unknown command {command}. Valid ones are "create" and "start"')


if __name__ == '__main__':
    main()
