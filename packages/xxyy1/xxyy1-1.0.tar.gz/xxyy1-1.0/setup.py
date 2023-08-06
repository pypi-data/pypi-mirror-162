from distutils.core import setup

setup(
    name = 'xxyy1' ,#对外我们模块的名字
    version ='1.0'  ,#版本号
    description = '这是第一个对外发布的模块，测试'  ,#描述
    author = 'xy' ,#作者
    author_email = '1972900624@qq.com',#作者邮箱
    py_modules = ['xxyy1.salary'] #要发布的模块
)