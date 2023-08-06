使用 python3  + click  编写的个人常用的工具  
* 服务器管理 
```shell script
m server 
```
* 本地常用工具 
```shell script
m local 
```
* 常用脚本管理
```shell script
m script 
```
* 本身配置管理 
```shell script
m config 
```

#### 安装更新工具  

>https://pypi.org/project/jiuming-tools/

```shell script
# ubuntu 使用python3 版本的pip 名字默认为pip3 
#安装
pip3 install jiuming-tools
#更新
pip3 install --upgrade jiuming-tools 
# 使用
m
#启用自动补全:
#bash:在.bashrc末尾添加 eval "$(_M_COMPLETE=source m)"
#zsh:在.zshrc末尾添加 eval "$(_M_COMPLETE=source_zsh m)"
```

#####  异常处理 
* 3.9.1 python  报错  无法读取 liblibc.a   这个应该是读取 Libc.a文件    将libc.a 复制一份 命名liblibc.a    
scrpy  3.9.1bug处理  将原本的libc.a 复制一份命名未Liblibc.a    
/usr/lib32/liblibc.a  
/usr/lib/liblibc.a   
  
```shell
sudo find / -name libc.a 

#新增兼容 
sudo cp /usr/lib32/libc.a /usr/lib32/liblibc.a
sudo cp /usr/lib/libc.a /usr/lib/liblibc.a
```

#### 后续计划 
本项目 就是参考 mmh的相关功能简化和添加一些自己常用的功能开发的   
> https://github.com/mritd/mmh    

* 调整 m server test功能  更名为 m server ping 功能 并且 提供数组参数    默认全部ping        
* 添加server 打洞相关功能  类似 mtun(mmh的端口映射)    ssh tun   ssh -R  ssh -L  ssh -D   ssh -W 
* 增加release whl包功能  提供在github release中提供whl包下载
* ssh相关功能增加心跳超时自动断开 等功能  
* ssh多级跳板功能  
