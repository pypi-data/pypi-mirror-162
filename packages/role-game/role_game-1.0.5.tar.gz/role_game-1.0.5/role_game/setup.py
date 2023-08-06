import setuptools


setuptools.setup(
    name="role_game",
    version="1.0.0",
    author="zhoufangfang",
    author_email="xczff001@163.com",
    maintainer="zhoufangfang",
    maintainer_email="xczff001@163.com",
    desciption="这是一个由编程猫用户创建的库，用来方便制作游戏",
    long_desciption=
        """
        这个库方便了创作游戏。
        此库加入了人物、道具、武器、防具与战斗系统。
        """,
    keywords=('game','tangsan'),
    packages=['Lib\\site-packages\\role_game'],
    install_requires=[
        'resis>=3.6'
    ],
    zip_safe=False

)
