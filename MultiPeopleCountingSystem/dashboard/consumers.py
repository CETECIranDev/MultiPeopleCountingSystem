# dashboard/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Camera, PeopleCount

class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.camera_id = self.scope['url_route']['kwargs']['camera_id']
        self.room_group_name = f'camera_{self.camera_id}'
        
        # بررسی وجود دوربین
        if not await self.camera_exists():
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # ارسال داده اولیه
        initial_data = await self.get_initial_data()
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'data': initial_data
        }))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'timestamp': data.get('timestamp')
            }))
    
    async def people_count_update(self, event):
        """دریافت آپدیت شمارش از سیستم AI"""
        await self.send(text_data=json.dumps({
            'type': 'count_update',
            'data': event['data']
        }))
    
    async def anomaly_alert(self, event):
        """دریافت هشدار ناهنجاری"""
        await self.send(text_data=json.dumps({
            'type': 'anomaly_alert',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def camera_exists(self):
        return Camera.objects.filter(id=self.camera_id, is_active=True).exists()
    
    @database_sync_to_async
    def get_initial_data(self):
        camera = Camera.objects.get(id=self.camera_id)
        recent_count = PeopleCount.objects.filter(camera=camera).order_by('-timestamp').first()
        
        return {
            'camera_name': camera.name,
            'current_count': recent_count.total_inside if recent_count else 0,
            'last_update': recent_count.timestamp.isoformat() if recent_count else None,
            'status': 'connected'
        }