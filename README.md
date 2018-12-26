# TestingPlatform
自动化测试管理平台
## 使用步骤：
* 工程目录执行celery -A TestingPlatform worker -l info
* 或者celery multi start w1 -A TestingPlatform -l info --logfile = celerylog.log --pidfile = celerypid.pid(后台执行)

