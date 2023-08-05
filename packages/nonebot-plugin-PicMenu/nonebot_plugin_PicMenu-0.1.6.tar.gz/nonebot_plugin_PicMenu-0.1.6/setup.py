from distutils.core import setup

setup(
    name='nonebot_plugin_PicMenu',
    packages=['nonebot_plugin_PicMenu'],
    version='0.1.6',
    license='MIT',
    description='A Plugin for Nonebot2 to generate picture menu of Plugins',
    author='hamo-reid',
    author_email='190395489@qq.com',
    url='https://github.com/hamo-reid/nonenot_plugin_PicMenu',
    dowload_url='https://github.com/hamo-reid/nonenot_plugin_PicMenu/archive/v_0_1_6.tar.gz',
    install_requires=[
        'pillow',
        'fuzzywuzzy',
        'nonebot2',
        'nonebot-adapter-onebot'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ]
)