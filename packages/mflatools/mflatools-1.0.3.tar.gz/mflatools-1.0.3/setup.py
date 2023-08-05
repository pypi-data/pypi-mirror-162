from distutils.core import setup

setup(
    name='mflatools',  # 对外我们模块的名字
    version='1.0.3',  # 版本号
    description='mfla的工具箱',  # 描述
    author='mfla',  # 作者
    author_email='871494698@qq.com',
    py_modules=['mflatools.tools_create_tips', 'mflatools.tools_sendAndReceiveMail']  # 要发布的模块
)
