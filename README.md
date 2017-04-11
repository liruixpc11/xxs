# 线下赛平台

## 数据库

### 测试环境搭建

1. 运行命令行`pip install -r requirements.txt`；
2. 运行[init_test_db.py](xxs/tools/init_test_db.py)，初始化SQLite3数据库，数据库位置默认是/var/lib/cadts/xxs/xxs.db；
3. 运行[main.py](xxs/webapp/main.py)，运行测试用Web服务器；
4. 访问[http://localhost:8080/pwn_data?task_id=1&last_id=0](http://localhost:8080/pwn_data?task_id=1&last_id=0)，获取pwn墙数据；
5. 访问[http://localhost:8080/flag_data?task_id=1](http://localhost:8080/flag_data?task_id=1)，获取Flag数据。
