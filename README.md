# Pansidong
自动化WEB漏洞扫描器


## TODO

### 线程池相关
* 使用gevent改进进程池

### 代理池管理部分
* 检查代理存活时改用多线程

### Web爬虫相关
* Web爬虫深度控制
* Web爬虫关键字控制
* Web爬虫多线程控制
* Web爬虫的目标域限制
* 去重算法优化
* 增加爬取form的action部分
* 获取打开页面时加载的ajax请求
* 增加Web代理功能，让浏览器代理到爬虫上，手工点击增加链接数量
* 从代理池中获取可用的代理并自动利用代理爬取
* 增加cookie支持
* 增加UA支持

## 更新日志
* 2016-7-17
    * 增加 第一版Web爬虫。可以初步过滤URL相似以及重复。
    * 增加 对Mac系统的支持。
* 2016-7-16
    * 修改proxy表字段，增加是否存活的字段。
* 2016-7-10
    * ProxySpider v1.0.4版本完成。
    * ProxySpider封装完成，已经作为模块导入到盘丝洞中：https://github.com/LiGhT1EsS/Pansidong
