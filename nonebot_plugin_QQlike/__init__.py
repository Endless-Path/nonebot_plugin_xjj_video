from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from nonebot.exception import MatcherException, ActionFailed

__plugin_meta__ = PluginMetadata(
    name="QQlike",
    description="给QQ个人主页点赞的插件",
    usage="发送'赞我'即可"
)

like = on_command("赞我", aliases={"点赞"}, priority=5, block=True)

@like.handle()
async def _(bot: Bot, event: Event):
    user_id = event.get_user_id()
    try:
        # 调用 OneBot V11 的 send_like 接口给用户点赞
        await bot.call_api("send_like", user_id=user_id, times=10)
        msg = Message(MessageSegment.text("已为你点赞10次啦~"))
    except ActionFailed as e:
        if "点赞数已达上限" in str(e):
            msg = Message(MessageSegment.text("今天已经给你点过赞啦，明天再来吧~"))
        else:
            msg = Message(MessageSegment.text(f"点赞失败了呢: {e.message}"))
    except Exception as e:
        logger.error(f"点赞过程中发生未预期的错误: {str(e)}")
        msg = Message(MessageSegment.text("哎呀，出了点小问题，请稍后再试~"))

    try:
        await like.finish(msg)
    except MatcherException:
        raise
    except Exception as e:
        logger.error(f"发送消息时发生未预期的错误: {str(e)}")