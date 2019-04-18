# activity-tracker

## About
This Python Flask Webapp enables users to record activities of different types for statistical evaluation.

Despite being in personal use since 01st January 2019, it is still in very early development status. Use at your own risk.

In the future I will supply some documentation of the features.

Thanks for reading.


## Installation

**Make sure you have Docker installed.**

0. Create your own mysql database or use this to spawn a container: `sudo docker run --name mysql -d -e MYSQL_RANDOM_ROOT_PASSWORD=yes -e MYSQL_DATABASE=trackr -e MYSQL_USER=trackr -e MYSQL_PASSWORD=MYSQL_PASSWORD mysql/mysql-server:5.7`
1. `git clone https://github.com/chrisdpk/activity-tracker`
2. `cd activity-tracker`
3. Optionally edit `config.py`
4. `sudo docker build -t trackr:latest`
5. Run `sudo docker run --name trackr -d -p 5000:5000 --rm --link mysql:dbserver -e DATABASE_URL=mysql+pymysql://MYSQL_USER:MYSQL_PASSWORD@dbserver/trackr trackr:latest` to start the service.
