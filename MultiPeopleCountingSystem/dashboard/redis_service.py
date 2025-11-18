import redis
import threading
import json


class RedisMessagingService:
    def __init__(self, host='localhost', port=6379, db=0, channel='ai_results'):
        # اتصال به Redis
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
        # ایجاد pubsub برای ارسال و دریافت پیام
        self.pubsub = self.redis_client.pubsub()
        # نام کانال برای انتشار داده‌ها
        self.channel = channel

    # تابع انتشار داده ها
    # داده ای که از AI داریم رو به کانال Redis ارسال میکنیم
    # داده تبدیل میشه به JSON تا استاندارد و خوانا باشه
    # همه ی subscriberها این پیام رو دریافت میکنند
    def publish_detection(self, camera_id, data):
        message = {
            "camera_id": camera_id,
            "data": data
        }
        self.redis_client.publish(self.channel, json.dumps(message))

    # تایع شنود داده ها
    # یک نخ جداگانه اجرا میکنه تا شنود پیام ها مسدود کننده برنامه اصلی نباشه
    # هر پیام جدید که تو کانال منتشر شد بصورت JSON دریافت میشه
    def subscribe_to_ai_results(self, callback):
        def listen():
            self.pubsub.subscribe(self.channel)
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    payload = json.loads(message['data'])
                    # callback->تابعی که مشخص میکنیم اجرا میشه
                    callback(payload)

        thread = threading.Thread(target=listen)
        thread.daemon = True
        thread.start()
