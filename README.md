# xueqiublog
Grab Blogs from Xueqiu

# 使用说明

### 安装依赖

```
virtualenv env --python=python2.7

source env/bin/activate

pip install requests
```

### 执行


1. 获得用户uid
2. 修改文件 blogGrabber.py:139 添加uid
3. 登陆雪球, 获得cookie, 修改Headers配置 
4. python blogGrabber.py
