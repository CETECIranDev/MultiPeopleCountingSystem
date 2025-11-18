import redis
import json

# اتصال به Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# داده شبیه داده AI
ai_data = {
    "camera_id": 1,
    "timestamp": "2025-11-18T12:00:00",
    "count_in": 5,
    "count_out": 2,
    "anomalies": [{"type": "congestion", "confidence": 0.95}]
}

# انتشار داده روی کانال Redis
r.publish('ai_results_channel', json.dumps(ai_data))

print("AI data published to Redis!")
