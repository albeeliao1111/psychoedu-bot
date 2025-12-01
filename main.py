from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os

app = FastAPI()

# --- Load secrets ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# --- Setup LINE SDK ---
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)

# --- Setup Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # 你可以改成 pro / flash / whatever


@app.post("/callback")
async def callback(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")

    # Parse LINE events
    events = parser.parse(body.decode("utf-8"), signature)

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):

            user_msg = event.message.text

            # --- Gemini 回覆 ---
            response = model.generate_content(user_msg)
            bot_reply = response.text if hasattr(response, "text") else "我現在有點忙，等我一下喔～"

            # 回覆 LINE
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=bot_reply)
            )

    return "OK"
