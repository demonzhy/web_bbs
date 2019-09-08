#!/usr/bin/env bash

set -ex

# 系统设置
apt-get install -y curl ufw
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 465
ufw default deny incoming
ufw default allow outgoing
ufw status verbose
ufw -f enable

# redis 需要 ipv6
sysctl -w net.ipv6.conf.all.disable_ipv6=0
# 安装过程中选择默认选项，这样不会弹出 libssl 确认框
export DEBIAN_FRONTEND=noninteractive
# 装依赖
apt-get install -y git supervisor nginx python3-pip mysql-server redis-server apache2-utils
#apt-get install -y git supervisor nginx python3-pip mysql-server apache2-utils
pip3 install jinja2 flask gevent gunicorn pymysql flask_sqlalchemy flask_mail marrow.mailer redis Celery
#pip3 install jinja2 flask gevent gunicorn pymysql flask_sqlalchemy flask_mail marrow.mailer

# 删除测试用户和测试数据库
# 删除测试用户和测试数据库并限制关闭公网访问
mysql -u root -pzhy1002 -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -pzhy1002 -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -pzhy1002 -e "DROP DATABASE IF EXISTS test;"
mysql -u root -pzhy1002 -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
# 设置密码并切换成密码验证
mysql -u root -pzhy1002 -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'zhy1002';"

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default
# 不要再 sites-available 里面放任何东西
cp /var/www/my_project/flask_bbs/new_web.nginx /etc/nginx/sites-enabled/new_web.nginx
chmod -R o+rwx /var/www/my_project/flask_bbs

cp new_web.service /etc/systemd/system/new_web.service
cp new_message_queue.service /etc/systemd/system/new_message_queue.service


# 初始化
cd /var/www/my_project/flask_bbs
python3 reset.py

# 重启服务器
systemctl daemon-reload
systemctl restart new_web.service
systemctl restart new_message_queue.service
systemctl restart nginx

echo 'succsss'
echo 'ip'
hostname -I
curl http://localhost
