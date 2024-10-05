#!pip install --upgrade appbuilder-sdk qianfan nest_asyncio discord.py redis

import os
import re
import socket
import qianfan
import discord
import asyncio
import nest_asyncio
import appbuilder
import logging

print(dir(appbuilder))
nest_asyncio.apply()

# 设置环境变量以进行认证
QIANFAN_ACCESS_KEY = os.environ["QIANFAN_ACCESS_KEY"]
QIANFAN_SECRET_KEY = os.environ["QIANFAN_SECRET_KEY"]

# 设置环境中的 TOKEN，以下 TOKEN 请替换为您的个人 TOKEN
APPBUILDER_TOKEN = os.environ["APPBUILDER_TOKEN"]

# 初始化全局锁
lock = asyncio.Lock()

chat_comp = qianfan.ChatCompletion()

# Discord 配置
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def main():
    try:
        await client.start(APPBUILDER_TOKEN)
    except discord.errors.LoginFailure as e:
        logging.error(f'Login failed: {e}')
    except discord.errors.HTTPException as e:
        logging.error(f'HTTP Exception occurred: {e}')
    except Exception as e:
        logging.error(f'Unexpected error: {e}')


powerOff = False
powerOff_user = ""
powerOff_user_input = ""
Post_review = ""

# 设置日志记录
logging.basicConfig(level=logging.INFO)

# 你可以在这里设置指定的频道 ID
target_channel_id = 1273112599885647883  # 替换为你的实际频道 ID


def get_ip_address():
    hostname = socket.gethostname()  # 获取主机名
    ip_address = socket.gethostbyname(hostname)  # 获取 IP 地址
    return ip_address


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # 获取指定频道
    # 如果需要发送启动消息，可以取消注释以下两行
    # channel = client.get_channel(target_channel_id)
    # if channel:
    #     await channel.send("""fairy 启动 ！""")


@client.event
async def on_disconnect():
    logging.warning('Bot has disconnected.')


@client.event
async def on_message(message):
    try:
        async with lock:  # 使用锁来确保并发调用不会发生
            global powerOff, powerOff_user, powerOff_user_input, Post_review
            if message.author == client.user:
                return

            username = str(message.author)
            user_input = message.content.lower()
            print(username, user_input)

            if "频道id" in user_input:
                channel_id = message.channel.id
                await message.channel.send(f"这里的频道 ID 是：{channel_id}")
                return

            if "论坛内容" in user_input and "评论内容" in user_input:
                # 从 AppBuilder 控制台获取已发布应用的 ID
                REVIEW_APP_ID = os.environ["REVIEW_APP_ID"]

                try:
                    user_input = user_input.replace("无法判断", "")
                    app_builder_client = appbuilder.AppBuilderClient(
                        REVIEW_APP_ID
                    )
                    conversation_id = app_builder_client.create_conversation()
                    resp = app_builder_client.run(conversation_id, user_input)
                    await message.channel.send(resp.content.answer)
                    print(resp.content.answer)
                except Exception as e:
                    logging.error(f"API request failed: {e}")
                    await message.channel.send("等待，发生了错误。")
                return

            if "!wait!" in user_input:
                user_input = re.sub(r"!wait!", "", user_input).strip()
                Post_review += user_input
                print(Post_review)
                await message.channel.send("继续")
                print("继续")
                return

            if "!end!" in user_input:
                user_input = re.sub(r"!end!", "", user_input).strip()
                Post_review += user_input
                # 从 AppBuilder 控制台获取已发布应用的 ID
                try:
                    REVIEW_APP_ID = os.environ["REVIEW_APP_ID"]
                    app_builder_client = appbuilder.AppBuilderClient(
                        REVIEW_APP_ID
                    )
                    conversation_id = app_builder_client.create_conversation()
                    resp = app_builder_client.run(conversation_id, Post_review)
                    await message.channel.send(resp.content.answer)
                    print(resp.content.answer)
                except Exception as e:
                    logging.error(f"Failed to process request: {e}")
                    await message.channel.send(
                        " 艹! 出错了! 联系一下<@1140530007555444797>"
                    )
                Post_review = ""
                return

            if "fairy" in user_input or "1275123343376515214" in user_input:
                if powerOff:
                    if (
                        (username == "haobinoo" and "启动" in user_input)
                        or (username == "nahida_buer" and "启动" in user_input)
                        or (username == "furina1048576" and "启动" in user_input)
                        or (username == "myitian" and "启动" in user_input)
                    ):
                        powerOff = False
                        await message.channel.send("我的好主人，我回来了！")
                        return
                    await message.channel.send(
                        f"Fairy已因 @{powerOff_user} 说了 '{powerOff_user_input}' 导致关闭，"
                        f"现无法回答问题，请等待 <@1140530007555444797> "
                        f"<@1165292898699464725> <@1130876908750512228> "
                        f"<@964838656420491285>。"
                    )
                    return

                if any(
                    word in user_input
                    for word in [
                        "再见！", "滚！", "拜拜！", "离开！", "关闭！",
                        "sb!", "关机！", "智障！"
                    ]
                ):
                    await message.channel.send("再见！")
                    powerOff_user = username
                    powerOff_user_input = user_input
                    powerOff = True
                    return

                if username == "haobinoo" and "ip" in user_input:
                    ip = get_ip_address()
                    await message.channel.send("我的好主人，我在这里：" + ip)
                    return

                # 定义正则表达式
                pattern1 = r'[a-zA-Z]+:[a-zA-Z]+:\d+'  # 匹配 str + str + int
                pattern2 = r'@\d+'                    # 匹配 @ + int

                for text in user_input:
                    # 查找符合两种模式的内容
                    match1 = re.search(pattern1, text)
                    match2 = re.search(pattern2, text)

                    # 如果匹配成功则打印
                    if match1:
                        print(f"匹配到 'str + str + int' 的字符串: {text}")
                    if match2:
                        print(f"匹配到 '@ + int' 的字符串: {text}")

                # 发起对话请求
                # 移除类似 <@userID> 的模式
                user_input = re.sub(
                    r"<@\d+>|<[a-zA-Z]+:[a-zA-Z]+:\d+>|<:[a-zA-Z]+:\d+>",
                    "",
                    user_input
                ).strip()
                print("过滤后：", user_input)
                response = await make_qianfan_request(username, user_input)
                print(response)
                await message.channel.send(response)
    except Exception as e:
        logging.error(
            f"Error occurred while processing message: {message.content}, "
            f"error: {e}"
        )


async def make_qianfan_request(username, user_input):
    try:
        # 从 AppBuilder 控制台获取已发布应用的 ID
        CHAT_APP_ID = os.environ["CHAT_APP_ID"]

        app_builder_client = appbuilder.AppBuilderClient(CHAT_APP_ID)
        conversation_id = await asyncio.to_thread(
            app_builder_client.create_conversation
        )
        resp = await asyncio.to_thread(
            app_builder_client.run, conversation_id, user_input
        )
        content = resp.content.answer

        if username == "haobinoo":
            return "我的好主人，" + content
        return content

    except Exception as e:
        # 记录错误并返回默认消息
        logging.error(f"Error during Qianfan API request: {e}")
        return "等待，发生了错误。"


@client.event
async def on_error(event, *args, **kwargs):
    logging.error(f"Error occurred in {event}: {args} - {kwargs}")
    await asyncio.sleep(5)  # 延时重连，防止无限循环重连
    try:
        await client.close()  # 关闭当前连接
        await client.start(APPBUILDER_TOKEN)  # 重新启动 bot
    except Exception as e:
        logging.error(f"Reconnection failed: {e}")


# 启动 Bot
asyncio.run(main())