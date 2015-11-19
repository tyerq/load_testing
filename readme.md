# op load tests

Under Debuntu:

``` $ sudo apt-get install libev-dev libzmq-dev python-dev```

Prepare environment:

```
git clone [repository]
```
Edit configuration file buildout.cfg. Set agents-count.
```
virtualenv .
source bin/activate
python bootstrap.py
bin/buildout
bin/circusd etc/circus.ini --daemon --pidfile circusd.pid
```

Run tests
====
``` bin/loads-runner -b tcp://0.0.0.0:13001 op_loads_tests.TestWebSite.test_main_page --hits 20 -u 10 -a 5 ```