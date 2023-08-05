from .menus import MenuManager
from .img_tool import img2b64

from nonebot import get_driver
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_startswith, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import MessageSegment
import re

__plugin_meta__ = PluginMetadata(
    name='PicMenu',
    description='为已安装的插件提供可视化的帮助菜单',
    usage='显示所有插件及描述：菜单\n'
          '显示某一插件的功能菜单：菜单 插件名/序号\n'
          '显示某一功能详情：菜单 插件名/序号 功能名/序号\n'
          '注：插件名/功能名 支持模糊匹配',
    extra={
        'author': 'hamo-reid',
        'menu_data': [
            {
                'func': '查询菜单',
                'trigger_method': '命令：菜单',
                'trigger_condition': '开头匹配[Any]',
                'brief_des': '用于查询本插件的各级菜单',
                'detail_des': '查看插件总表、插件命令和命令详情,具体方法如下：\n'
                              '查看菜单总表：菜单\n'
                              '查看插件命令：菜单 插件名/编号\n'
                              '查看命令详情：菜单 插件名/编号 命令/命令编号\n'
                              '插件名和命令均支持模糊查找'
            },
        ],
        'menu_template': 'default'
    }
)

driver = get_driver()

menu_manager = MenuManager()
menu = on_startswith('菜单', priority=1)
switch = on_fullmatch('开关菜单', priority=1)

menu_switch = True

@driver.on_bot_connect
async def _():
    if not menu_manager.data_manager.plugin_menu_data_list:
        menu_manager.load_plugin_info()

@switch.handle()
async def _():
    global menu_switch
    menu_switch = not menu_switch
    if menu_switch:
        await switch.finish(MessageSegment.text('菜单已开启'))
    else:
        await switch.finish(MessageSegment.text('菜单已关闭'))

async def check_switch(matcher: Matcher):
    if not menu_switch:
        matcher.skip()

@menu.handle()
async def _(event: Event, check=Depends(check_switch)):
    msg = str(event.get_message())
    if match_result := re.match(r'^菜单 (.*?) (.*?)$|^/菜单 (.*?) (.*?)$', msg):
        result = [x for x in match_result.groups() if x is not None]
        plugin_name = result[0]
        cmd = result[1]
        temp = menu_manager.generate_func_details_image(plugin_name, cmd)
        if isinstance(temp, str):
            if temp == 'PluginIndexOutRange':
                await menu.finish(MessageSegment.text('插件序号不存在'))
            elif temp == 'CannotMatchPlugin':
                await menu.finish(MessageSegment.text('插件名过于模糊或不存在'))
            elif temp == 'PluginNoFuncData':
                await  menu.finish(MessageSegment.text('该插件无功能数据'))
            elif temp == 'CommandIndexOutRange':
                await menu.finish(MessageSegment.text('命令序号不存在'))
            else:
                await menu.finish(MessageSegment.text('命令过于模糊或不存在'))
        else:
            await menu.finish(MessageSegment.image('base64://' + img2b64(temp)))
    elif match_result := re.match(r'^菜单 (.*)$|^/菜单 (.*)$', msg):
        result = [x for x in match_result.groups() if x is not None]
        plugin_name = result[0]
        temp = menu_manager.generate_plugin_menu_image(plugin_name)
        if isinstance(temp, str):
            if temp == 'PluginIndexOutRange':
                await menu.finish(MessageSegment.text('插件序号不存在'))
            else:
                await menu.finish(MessageSegment.text('插件名过于模糊或不存在'))
        else:
            await menu.finish(MessageSegment.image('base64://' + img2b64(temp)))
    else:
        img = menu_manager.generate_main_menu_image()
        await menu.finish(MessageSegment.image('base64://' + img2b64(img)))
