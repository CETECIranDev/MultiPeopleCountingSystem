import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


# WebSocket consumer برای مدیریت real-time داده‌های چندین دوربین
# دریافت داده از backend و ارسال به کلاینت
class MultiCameraConsumer(AsyncWebsocketConsumer):
    # کلاینت رو قبول میکنه و subscription ها رو مدیریت میکنه
    async def connect(self):
        """
        هنگام اتصال کلاینت:
        - اتصال رو قبول کن
        - یک دیکشنری برای subscription ها ایجاد کن
        """
        # اینجا میشه چندین دوریین رو همزمان مدیریت کرد

        self.subscribed_cameras = set()  # دوربین‌هایی که کلاینت دنبال می‌کنه
        await self.accept()  # اتصال WebSocket رو قبول می‌کنه
        print(f"[WebSocket] Client connected: {self.channel_name}")

    # کلابینت از همه گروه ها خارج میشه
    # این باعث میشه دیگر داده های دوربین براش ارسال نشه
    async def disconnect(self, close_code):
        """
        هنگام قطع اتصال کلاینت:
        - از تمام گروه‌هایی که subscribe شده خارج میشه
        """
        for camera_id in self.subscribed_cameras:
            await self.channel_layer.group_discard(
                f"camera_{camera_id}", self.channel_name
            )
        print(f"[WebSocket] Client disconnected: {self.channel_name}")

    # دریافت پیام از کلاینت
    # کلاینت میتونه دو نوع درخواست بفرسته
    async def receive(self, text_data):
        """
        دریافت پیام از کلاینت
        - پیام‌ها به صورت JSON هستن
        - دستور subscribe/unsubscribe یا درخواست full config
        """
        data = json.loads(text_data)
        action = data.get("action")
        camera_id = data.get("camera_id")

        if action == "subscribe" and camera_id:
            # group_add برای مدیریت گروه های دوربین هاست
            await self.channel_layer.group_add(
                f"camera_{camera_id}", self.channel_name
            )
            self.subscribed_cameras.add(camera_id)
            await self.send_json({"status": "subscribed", "camera_id": camera_id})

        elif action == "unsubscribe" and camera_id:
            # group_discard برای مدیریت گروه های دوربین هاست
            await self.channel_layer.group_discard(
                f"camera_{camera_id}", self.channel_name
            )
            self.subscribed_cameras.discard(camera_id)
            await self.send_json({"status": "unsubscribed", "camera_id": camera_id})

        else:
            await self.send_json({"error": "invalid action or missing camera_id"})

    # زمانی که یک داده ی جدید پردازش شد backend آن را به کانال گروهی دوربین میفرسته
    async def receive_ai_data(self, event):
        """
        دریافت داده‌های AI از backend/Redis و ارسال به کلاینت
        event:
        {
            "camera_id": 1,
            "people_count": 5,
            "anomalies": [{"type": "congestion", "confidence": 0.85}]
        }
        """
        # سپس این داده ها به کلابینت هایی که سابسکرایب کردن ارسال میشه
        await self.send_json({
            "camera_id": event.get("camera_id"),
            "people_count": event.get("people_count"),
            "anomalies": event.get("anomalies", [])
        })

    async def send_json(self, content):
        """
        wrapper برای ارسال JSON به کلاینت
        """
        await self.send(text_data=json.dumps(content))
