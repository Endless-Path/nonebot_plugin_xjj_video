from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State
import httpx
import os
import tempfile
import asyncio
import time
from collections import defaultdict

__plugin_meta__ = PluginMetadata(
    name="小姐姐视频",
    description="获取并发送小姐姐视频",
    usage='输入"小姐姐视频"或"小姐姐"触发',
    type="application",
    homepage="https://github.com/chsiyu/nonebot_plugin_xjj_video",
    supported_adapters={"~onebot.v11"},

)

last_use_time = defaultdict(float)
COOLDOWN_TIME = 60  # 冷却时间，单位：秒

xjj_video = on_command("小姐姐视频", aliases={"小姐姐"}, rule=to_me(), priority=5)

API_ENDPOINTS = [
    "https://tools.mgtv100.com/external/v1/pear/xjj",
    "http://api.yujn.cn/api/zzxjj.php?type=json",
    "http://www.wudada.online/Api/ScSp",
    "https://api.qvqa.cn/api/cos/?type=json",
    "https://jx.iqfk.top/api/sjsp.php"
]

async def get_video_url(client, url):
    try:
        response = await client.get(url, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        
        if url == API_ENDPOINTS[4]:
            return url
        
        data = response.json()
        
        if url == API_ENDPOINTS[0]:
            return data.get("data")
        elif url == API_ENDPOINTS[1]:
            return data.get("data")
        elif url == API_ENDPOINTS[2]:
            return data.get("data")
        elif url == API_ENDPOINTS[3]:
            return data.get("data", {}).get("video")
        
    except Exception as e:
        logger.error(f"Error fetching video from {url}: {str(e)}")
    return None

async def download_video(client, url):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            async with client.stream("GET", url, timeout=30.0, follow_redirects=True) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    temp_file.write(chunk)
            return temp_file.name
    except Exception as e:
        logger.error(f"Error downloading video from {url}: {str(e)}")
        return None

@xjj_video.handle()
async def handle_xjj_video(bot: Bot, event: MessageEvent, state: T_State):
    user_id = event.get_user_id()
    current_time = time.time()
    if current_time - last_use_time[user_id] < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - (current_time - last_use_time[user_id]))
        await bot.send(event, f"命令冷却中，请在{remaining_time}秒后再试。")
        return

    last_use_time[user_id] = current_time

    temp_files = []
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            video_urls = await asyncio.gather(*[get_video_url(client, url) for url in API_ENDPOINTS])
            video_urls = [url for url in video_urls if url]
            
            logger.info(f"Retrieved {len(video_urls)} valid video URLs")
            
            if not video_urls:
                await bot.send(event, "获取视频失败，请稍后再试。")
                return
            
            temp_files = await asyncio.gather(*[download_video(client, url) for url in video_urls])
            temp_files = [file for file in temp_files if file]  # 过滤掉下载失败的视频
        
        if not temp_files:
            await bot.send(event, "所有视频下载失败，请稍后再试。")
            return

        msg_list = []
        for i, temp_file in enumerate(temp_files, start=1):
            try:
                msg_list.append({
                    "type": "node",
                    "data": {
                        "name": "小姐姐视频Bot",
                        "uin": event.self_id,
                        "content": MessageSegment.video(file=temp_file)
                    }
                })
                logger.info(f"Added video {i} to messages")
            except Exception as e:
                logger.error(f"Error adding video {i} to messages: {str(e)}")
        
        if not msg_list:
            await bot.send(event, "所有视频处理失败，请稍后再试。")
            return
        
        # 发送合并转发消息
        if event.message_type == "group":
            await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_list)
        else:
            await bot.send_private_forward_msg(user_id=event.user_id, messages=msg_list)
        
        logger.info(f"Sent {len(msg_list)} videos successfully")
        await bot.send(event, f"成功发送了 {len(msg_list)} 个视频。")
    except Exception as e:
        logger.error(f"Error in handle_xjj_video: {str(e)}")
        await bot.send(event, f"发送视频失败：{str(e)}")
    finally:
        # 删除所有临时文件
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
                logger.info(f"Deleted temporary file: {temp_file}")
            except Exception as e:
                logger.error(f"Error deleting temporary file {temp_file}: {str(e)}")