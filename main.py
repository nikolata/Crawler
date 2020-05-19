import requests
from bs4 import BeautifulSoup
import sys

# def visit(to_be_visit):
#     for link in soup.find_all('a'):
#         link_string = link.get('href')
#         if 'https' in link_string or 'link' in link_string:
#             pass


def to_visit(curr_link, to_be_visited):
    response = requests.get(curr_link, timeout=10)
    try:
        html = response.content.decode('utf-8')
    except UnicodeDecodeError:
        print('GRUMNA')
        return to_be_visited
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        link_string = link.get('href')
        if link_string is not None:
            if ('http' in link_string or 'link.php' in link_string) and str(link_string) not in to_be_visited:
                to_be_visited.append(link_string)
            if 'link.php' in link_string and str(link_string) not in to_be_visited:
                url = 'https://register.start.bg/'
                link_string = url + link_string
                to_be_visited.append(link_string)
    return to_be_visited


def visit(start, to_be_visited=[], i=0):
    response = requests.get(start, timeout=10)
    try:
        html = response.content.decode('utf-8')
    except UnicodeDecodeError:
        visit(to_be_visited[i + 1], to_be_visited, i + 1)
    soup = BeautifulSoup(html, 'html.parser')
    br = 0
    for link in soup.find_all('a'):
        link_string = link.get('href')
        if link_string is not None:
            # print(link_string)
            if 'http' in link_string and str(link_string) not in to_be_visited:
                # print(link_string)
                r = requests.get(link_string)
                print(r.headers['Server'])
                br += 1
                # to_be_visited = to_visit(link_string, to_be_visited)
            if 'link.php' in link_string and str(link_string) not in to_be_visited:
                url = 'https://register.start.bg/'
                link_string = url + link_string
                br += 1
                r = requests.get(link_string)
                print(r.headers['Server'])
                # print(link_string)
                # try:
                #     to_be_visited = to_visit(link_string, to_be_visited)
                # except ConnectionError:
                #     pass
    print(br)
    # visit(to_be_visited[i], to_be_visited, i + 1)


def main():
    command = sys.argv[1]
    if command == 'create':
        visit('https://register.start.bg/')
    if command == 'start':
        pass
    else:
        raise ValueError(f'Unknown command {command}. Valid ones are "create" and "start"')


if __name__ == '__main__':
    main()
