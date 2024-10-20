from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER, Permission
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="群信息管理",
    description="管理群聊信息，包括设置群名片、群名、群头像和精华消息等。",
    usage="""
    - 设置群名片: 发送 "设置群名片 @用户 新名片" 或 "改群名片 @用户 新名片"。
    - 设置群名: 发送 "设置群名 新群名" 或 "改群名 新群名"。
    - 设置群头像: 发送 "设置群头像" 或 "改群头像" 并附带图片，或回复包含图片的消息。
    - 设置精华消息: 回复一条消息并发送 "设置精华" 或 "加精"。
    - 取消精华消息: 回复一条精华消息并发送 "取消精华" 或 "取消加精"。
    注意：以上命令仅群主、管理员或超级用户可用。
    """,
    type="application",
    homepage="https://github.com/Endless-Path/Endless-path-nonebot-plugins/nonebot-plugin-group-manager",
    supported_adapters={"~onebot.v11"},
)

async def _group_admin(bot: Bot, event: GroupMessageEvent) -> bool:
    return (await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id))["role"] in ["owner", "admin"]

GROUP_ADMIN = Permission(_group_admin)
ADMIN_PERMISSION = SUPERUSER | GROUP_ADMIN

set_card = on_command("设置群名片", aliases={"改群名片"}, permission=ADMIN_PERMISSION, priority=5, block=True)
set_name = on_command("设置群名", aliases={"改群名"}, permission=ADMIN_PERMISSION, priority=5, block=True)
set_portrait = on_command("设置群头像", aliases={"改群头像"}, permission=ADMIN_PERMISSION, priority=5, block=True)
set_essence = on_command("设置精华", aliases={"加精"}, permission=ADMIN_PERMISSION, priority=5, block=True)
del_essence = on_command("取消精华", aliases={"取消加精"}, permission=ADMIN_PERMISSION, priority=5, block=True)

@set_card.handle()
async def handle_set_card(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """设置群名片"""
    at_seg = args["at"]
    if not at_seg:
        await set_card.finish("请@要设置群名片的用户")
    
    new_card = args.extract_plain_text().strip()
    if not new_card:
        await set_card.finish("请提供新的群名片")
    
    user_id = at_seg[0].data['qq']
    
    try:
        await bot.set_group_card(group_id=event.group_id, user_id=int(user_id), card=new_card)
        await set_card.send(MessageSegment.text(f"已将 ") + at_seg[0] + MessageSegment.text(f" 的群名片修改为 {new_card}"))
    except Exception as e:
        await set_card.send(f"设置群名片失败: {str(e)}")
    
    await set_card.finish()

@set_name.handle()
async def handle_set_name(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """设置群名"""
    new_name = args.extract_plain_text().strip()
    if not new_name:
        await set_name.finish("请提供新的群名")
    
    try:
        await bot.set_group_name(group_id=event.group_id, group_name=new_name)
        await set_name.send(f"已将群名修改为: {new_name}")
    except Exception as e:
        await set_name.send(f"设置群名失败: {str(e)}")
    
    await set_name.finish()
        
@set_portrait.handle()
async def handle_set_portrait(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """设置群头像"""
    image = args["image"] if args["image"] else (event.reply.message["image"] if event.reply else None)
    
    if not image:
        await set_portrait.finish("请提供群头像图片（可以直接发送图片，或回复包含图片的消息）")
    
    try:
        # 获取图片信息
        image_info = await bot.get_image(file=image[0].data["file"])
        file_url = image_info["url"]
        
        # 设置群头像
        await bot.set_group_portrait(group_id=event.group_id, file=file_url)
        await set_portrait.send("群头像设置成功")
    except Exception as e:
        await set_portrait.send(f"设置群头像失败: {str(e)}")
    
    await set_portrait.finish()

@set_essence.handle()
async def handle_set_essence(bot: Bot, event: GroupMessageEvent):
    """设置精华消息"""
    if not (event.reply and event.reply.message_id):
        await set_essence.finish("请回复要设置为精华的消息")
    
    try:
        await bot.set_essence_msg(message_id=event.reply.message_id)
        await set_essence.send("已将该消息设置为精华消息")
    except Exception as e:
        await set_essence.send(f"设置精华消息失败: {str(e)}")
        
    await set_essence.finish()

@del_essence.handle()
async def handle_del_essence(bot: Bot, event: GroupMessageEvent):
    """取消精华消息"""
    if not (event.reply and event.reply.message_id):
        await del_essence.finish("请回复要取消精华的消息")
    
    try:
        await bot.delete_essence_msg(message_id=event.reply.message_id)
        await del_essence.send("已取消该精华消息")
    except Exception as e:
        await del_essence.send(f"取消精华消息失败: {str(e)}")
    
    await del_essence.finish()
