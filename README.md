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
This will take all links from the main page [register.start.bg](https://register.start.bg/). Keep in mind that this will take time and it depends if your ubuntu is on Hard drive or SSD. Mine is on Hard drive and took me 25+ minutes. The program can work totally fine if you stop it with CNTR + C whenever you want.
#### The second step is to run ```python3 main.py start```. :spider_web:
This is where the crawler start to crawl into website links. It will crawl website by website with BFS logic. You can stop it anytime and all your progress will be saved to database.
#### To see all servers run ```python3 main.py histogram```.
You will see rows of servers arranged from A to Z

Database
----------------------------

#### We have 2 tables. Websites and Counter.
##### Websites
url_id  | website_link | server | parent_id |
------- | ------------ | ------ |	---------	|
1  | http://www.link1.bg/ |	Apache | 0 |
2  | http://www.link2.bg/ | Apache/2.2.3 | 0 |
##### Counter
counter_id | curr_id |
---------- | ------- |
1 | 3 |

Project logic
----------------------------

Our project is using BFS logic. When getting all starting links with ```python3 main.py create```, they are saved with parent_id = 0, because they are the main page parent links. When starting the program with ```python3 main.py start```, the program will look for current parent from 'counter' table and will start crawling all links of this parent and save them into the database. When all links are crawled, the program will get the next id and this will repeat until you stop the program or you reach the maximum list length.
With 'Counter' table we ensure that when the program is started again, we will continue from the last crawled website.

Some problems
----------------------------
#### With the way this program works, we have some minor problems:
1. Program skips links to websites that are not 'utf-8'
2. The program skips links to websites that take more than 10 seconds to get a server name. This time is optional.
3. The program skips links that take more than 10 seconds to get HTTP link. This time is optional.
4. When the program is started with 'start' command, the program is looking at parent links that are already added.
```bash
Example:
If your current parent is id=17 with 100 website links and you already crawled 10 links. 
The program will check all this 10 links(will not add them to the database).
This can be a problem if you already checked 90 links. 
```
Hint
----------------------------
#### I added the database, so you can skip the 'create' part :muscle: :muscle: :muscle:
