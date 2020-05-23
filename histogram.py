import matplotlib.pyplot as plt
import numpy as np
from database import session
from model import Websites


def show_histogram():
    plt.rcdefaults()
    number_of_columns = int(input("Select how many collums: "))
    columns = []
    objects = ()
    for column in range(number_of_columns):
        like_hour = input('Input hour(h:m:s) or date(y-m-d): ')
        columns.append(len(session.query(Websites).filter(Websites.created_date.like(f'%{like_hour}%')).all()))
        objects = objects + ('added at ' + like_hour,)

    y_pos = np.arange(len(objects))
    performance = columns

    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Websites')
    plt.title('Histogram of added websites')

    plt.show()


def show_histogram_servers():
    all_servers = session.query(Websites.server).group_by(Websites.server).all()
    plt.rcdefaults()
    columns = []
    objects = ()
    count = 0
    for server in all_servers:
        if count == 20:
            break
        columns.append(len(session.query(Websites).filter(Websites.server == server[0]).all()))
        objects = objects + (server[0],)
        count += 1
    y_pos = np.arange(len(objects))
    performance = columns

    plt.bar(y_pos, performance, align='center', alpha=0.5)
    plt.xticks(y_pos, objects, rotation='vertical')
    plt.ylabel('Number of servers')
    plt.xlabel('Servers')
    plt.title('Histogram of all servers')

    plt.show()