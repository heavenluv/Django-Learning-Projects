

Before use the command python manage.py runserver, **remember to start**:
1. If you want to use memcached, run the command below:
>memcached -l 127.0.0.1:11211

2.run the uwsgi
>sudo uwsgi --ini config/uwsgi.ini 
```
Some important point:
remember to configure the uwsgi.ini ---> uid = your_username gid= your_group      
```
3.Before run nginx, run this
```
sudo nginx -c /usr/local/etc/nginx/nginx.conf
sudo nginx -s reload
sudo nginx -s stop/quit
```
If not successfully activated and encountered permission problem, then:
navigate to the nginx.conf(default one)
```
cd /usr/local/etc/nginx/          
then vim nginx.conf
change the below line:
user nobody
to:
user your_username your_group(for mac normally is staff)
```
4. Remember to export the configured setting file:
>export DJANGO_SETTINGS_MODULE=educa.settings.pro

5.To enable the chat room, pls remember run redis on shell:
>redis-server
