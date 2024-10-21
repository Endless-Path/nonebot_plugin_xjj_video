from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters import Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message
from nonebot.log import logger

__plugin_meta__ = PluginMetadata(
    name="机器人资料设置",
    description="设置机器人的头像、昵称和个人签名。",
    usage="""
    - 设置头像: 发送 "设置头像" 并附带图片，或回复包含图片的消息。
    - 设置签名: 发送 "设置签名 新签名内容"。
    - 设置昵称: 发送 "设置昵称 新昵称"。
    注意：以上命令仅超级用户可用。
    """,
    type="application",
    homepage="https://github.com/your_username/your_repo",
    supported_adapters={"~onebot.v11"},
)

# 设置头像的命令
set_avatar = on_command("设置头像", permission=SUPERUSER, priority=10, block=True)
# 设置签名的命令
set_signature = on_command("设置签名", permission=SUPERUSER, priority=10, block=True)
# 设置昵称的命令
set_nickname = on_command("设置昵称", permission=SUPERUSER, priority=10, block=True)

@set_avatar.handle()
async def handle_set_avatar(bot: Bot, event: Event, args: Message = CommandArg()):
    image = args["image"] if args["image"] else (event.reply.message["image"] if event.reply else None)
    
    if not image:
        await set_avatar.finish("请提供要设置的头像图片（可以直接发送图片，或回复包含图片的消息）")
    
    try:
        # 获取图片信息
        image_info = await bot.call_api("get_image", file=image[0].data["file"])
        file_url = image_info["url"]
        
        # 设置头像
        await bot.call_api("set_qq_avatar", file=file_url)
        await set_avatar.send("头像设置成功")
    except Exception as e:
        logger.exception("设置头像失败")
        await set_avatar.send(f"设置头像失败: {str(e)}")
    
    await set_avatar.finish()

@set_signature.handle()
async def handle_set_signature(bot: Bot, event: Event, args: Message = CommandArg()):
    # 检查是否有签名参数
    if not args:
        await set_signature.finish("请提供要设置的个人签名")
    
    signature = args.extract_plain_text().strip()
    
    try:
        # 调用 set_self_longnick API 设置个人签名
        await bot.call_api("set_self_longnick", longNick=signature)
        await set_signature.send("个人签名设置成功!")
    except Exception as e:
        logger.exception("设置个人签名失败")
        await set_signature.send(f"设置个人签名失败: {str(e)}")
    
    await set_signature.finish()

@set_nickname.handle()
async def handle_set_nickname(bot: Bot, event: Event, args: Message = CommandArg()):
    # 检查是否有昵称参数
    if not args:
        await set_nickname.finish("请提供要设置的昵称")
    
    nickname = args.extract_plain_text().strip()
    
    try:
        # 调用 set_qq_profile API 设置昵称
        await bot.call_api("set_qq_profile", nickname=nickname)
        await set_nickname.send("昵称设置成功!")
    except Exception as e:
        logger.exception("设置昵称失败")
        await set_nickname.send(f"设置昵称失败: {str(e)}")
    
    await set_nickname.finish()
