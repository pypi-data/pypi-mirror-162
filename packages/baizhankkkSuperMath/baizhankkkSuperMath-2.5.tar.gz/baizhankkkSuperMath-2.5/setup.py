from distutils.core import setup

setup(
    name='baizhankkkSuperMath',    #对外我们模块的名字
    version='2.5',      #版本号
    description='这是第一个对外发布的模块，里面只有数学方法，用于测试哦',     #描述
    author='gaoqi',     #作者
    author_email='gaoqi110@163.com',       #作者邮箱
    py_modules=['baizhanSuperMath.demo1','baizhanSuperMath.demo2']     #要发布的模块
)