## Web Crawler By Nikola Metodiev :spider: :spider:

Requirements
----------------------------
Before you can use the web crawler you need to install some packages.
```bash
pip install -r requirements.txt
```

How it works
----------------------------
#### Firstly you need to run in the terminal ```python3 main.py create```.
This will take all links from the main page [register.start.bg](https://register.start.bg/). Keep in mind that this will take time and it depends if your ubuntu is on Hard drive or SSD. Mine is on Hard drive and took me 15+ minutes. The program can work totally fine if you stop it with CNTR + C whenever you want.
#### The second step is to run ```python3 main.py start```. :spider_web:
This is where the crawler start to crawl into website links. It will crawl website by website with BFS logic. You can run several terminals at the same time to crawl faster. You can stop it anytime and all your progress will be saved to database.
#### To see all added links in chosen by you date/time run ```python3 main.py histogram```.
First you need to choose how many colums you want.
Then you need to input the date or time you for each column.
Examples: 
'2020-05-24' - this will show all websites added on 2020-05-24
'15:33' - this will show all websites added at 15:33
You can combine date and time to be more precise - '2020-05-24 15:3'
#### To see histogram of first 20 servers run ```python3 main.py histogram_servers```
This will show you histogram of first 20 servers, ordered A-Z
#### To see all servers on localhost run:
```bash
export FLASK_APP=flask_display.py
```
```bash
flask run
```
Then open [127.0.0.1:5000](http://127.0.0.1:5000/) to see all servers

Database
----------------------------

#### We have 2 tables. Websites and Counter.
##### Websites
url_id  | website_link | server | parent_id | created_date | used |
------- | ------------ | ------ |	---------	|	-------- | ---- |
1  | http://www.link1.bg/ |	Apache | 0 | 2020-05-24 16:30:40.2142 | 1 |
2  | http://www.link2.bg/ | Apache/2.2.3 | 0 | 2020-05-24 17:30:40.2142 | 0 |
##### Counter
counter_id | curr_id |
---------- | ------- |
1 | 3 |

Project logic
----------------------------

Our project is using BFS logic. When getting all starting links with ```python3 main.py create```, they are saved with parent_id = 0 and used = 0, because they are the main page parent links. When starting the program with ```python3 main.py start```, the program takes curr_id from 'Counter' and gets from 'Websites' 5 links that have bigger 'url_id' than 'curr_id' and are unused. In list we are saving all "children" links and after all links are crawled the program bulk adds them into database, then the program changes all crawled links from used = False to used = True. This way we ensure that we don't visit already crawled links.
With 'Counter' table we ensure that when the program is started again, we will continue from the last crawled website and we can run several terminals at the same time.

Some problems
----------------------------
#### With the way this program works, we have some minor problems:
1. Program skips links to websites that are not 'utf-8'
2. The program skips links to websites that take more than 20 seconds to get a server name. This time is optional.
3. The program skips links that take more than 10 seconds to get HTTP link. This time is optional.
4. If you stop the program before the links are added, the counter will increase and the next time you start the program you will skip this 5 links.

### Have a good day! :four_leaf_clover: