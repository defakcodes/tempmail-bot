#!/usr/bin/env python3
"""
WebSocket Server for Auto-Fill Bridge
Connects Telegram Bot with Browser Extension
"""

import asyncio
import json
import time
import logging
import os
from typing import Dict, Set
from datetime import datetime

# FastAPI and WebSocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, validator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL', f'ws://localhost:{SERVER_PORT}')

# CORS configuration - defaults to localhost only for security
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000').split(',')

app = FastAPI(title="TempMail OTP Auto-Fill Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specify exact origins for security
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Store active connections and pending OTPs
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pending_otps: Dict[str, Dict] = {}
        self.user_emails: Dict[str, str] = {}  # user_id -> current_email
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"✅ User {user_id} connected")
        
        # Send any pending OTP
        if user_id in self.pending_otps:
            await self.send_otp(user_id, self.pending_otps.pop(user_id))
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"❌ User {user_id} disconnected")
    
    async def send_otp(self, user_id: str, data: dict):
        """Send OTP to connected user"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(data)
                # Mask OTP in logs for security
                logger.info(f"📤 OTP sent to user {user_id}")
                return True
            except:
                self.disconnect(user_id)
                return False
        return False
    
    async def broadcast_status(self):
        """Broadcast server status to all connections"""
        status = {
            "type": "status",
            "connected_users": len(self.active_connections),
            "pending_otps": len(self.pending_otps),
            "timestamp": datetime.now().isoformat()
        }
        
        for user_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_json(status)
            except:
                self.disconnect(user_id)

manager = ConnectionManager()

# Data models
class OTPData(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    otp: str = Field(..., min_length=4, max_length=8, pattern=r'^\d+$')
    email: str = Field(..., min_length=5, max_length=255)
    sender: str = Field(default="Unknown", max_length=255)
    domain: str = Field(default="", max_length=100)
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
class EmailData(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower().strip()

# API Endpoints
@app.get("/")
async def root():
    """Health check and status"""
    return {
        "status": "running",
        "service": "TempMail OTP Auto-Fill Server",
        "connected_users": len(manager.active_connections),
        "pending_otps": len(manager.pending_otps)
    }

@app.get("/dashboard")
async def dashboard():
    """Simple dashboard HTML"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OTP Auto-Fill Server</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f0f0f0; }
            .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; }
            .status { padding: 10px; background: #4CAF50; color: white; border-radius: 5px; margin: 10px 0; }
            .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }
            .stat-card { padding: 15px; background: #f9f9f9; border-radius: 5px; text-align: center; }
            .stat-value { font-size: 2em; font-weight: bold; color: #333; }
            .stat-label { color: #666; margin-top: 5px; }
            #log { background: #f4f4f4; padding: 10px; border-radius: 5px; height: 200px; overflow-y: auto; }
            .log-entry { padding: 5px; margin: 2px 0; background: white; border-left: 3px solid #4CAF50; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 OTP Auto-Fill Server Dashboard</h1>
            <div class="status">✅ Server is running</div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="connected">0</div>
                    <div class="stat-label">Connected Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="pending">0</div>
                    <div class="stat-label">Pending OTPs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="delivered">0</div>
                    <div class="stat-label">Delivered Today</div>
                </div>
            </div>
            
            <h3>📊 Live Activity</h3>
            <div id="log"></div>
        </div>
        
        <script>
            const wsUrl = window.location.protocol === 'https:' ? 
                'wss://' + window.location.host + '/ws/dashboard' : 
                'ws://' + window.location.host + '/ws/dashboard';
            const ws = new WebSocket(wsUrl);
            let delivered = 0;
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'status') {
                    document.getElementById('connected').textContent = data.connected_users;
                    document.getElementById('pending').textContent = data.pending_otps;
                }
                
                if (data.type === 'otp_delivered') {
                    delivered++;
                    document.getElementById('delivered').textContent = delivered;
                    
                    const log = document.getElementById('log');
                    const entry = document.createElement('div');
                    entry.className = 'log-entry';
                    entry.innerHTML = `🔑 OTP delivered to ${data.user_id}: ${data.otp}`;
                    log.insertBefore(entry, log.firstChild);
                }
            };
            
            // Update every 5 seconds
            setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({action: 'status'}));
                }
            }, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for browser extensions"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and handle messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                message = json.loads(data)
                
                # Handle ping/pong
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                # Handle status request
                elif message.get("type") == "status":
                    status = {
                        "type": "status",
                        "connected": True,
                        "email": manager.user_emails.get(user_id),
                        "timestamp": time.time()
                    }
                    await websocket.send_json(status)
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        manager.disconnect(user_id)

@app.post("/api/otp")
async def receive_otp(data: OTPData):
    """Receive OTP from Telegram bot"""
    otp_info = {
        "type": "otp",
        "otp": data.otp,
        "email": data.email,
        "sender": data.sender,
        "domain": data.domain,
        "timestamp": time.time()
    }
    
    # Try to send immediately
    if await manager.send_otp(data.user_id, otp_info):
        logger.info(f"✅ OTP delivered to {data.user_id}")
        return {"status": "delivered", "user_id": data.user_id}
    else:
        # Store for later
        manager.pending_otps[data.user_id] = otp_info
        logger.info(f"📦 OTP stored for {data.user_id} (offline)")
        return {"status": "pending", "user_id": data.user_id}

@app.post("/api/email")
async def register_email(data: EmailData):
    """Register new email for user"""
    manager.user_emails[data.user_id] = data.email
    
    # Notify extension
    email_info = {
        "type": "new_email",
        "email": data.email,
        "timestamp": time.time()
    }
    
    await manager.send_otp(data.user_id, email_info)
    return {"status": "registered", "email": data.email}

@app.get("/api/status/{user_id}")
async def user_status(user_id: str):
    """Get user connection status"""
    return {
        "connected": user_id in manager.active_connections,
        "email": manager.user_emails.get(user_id),
        "has_pending": user_id in manager.pending_otps
    }

def main():
    """Run the server"""
    import uvicorn
    print("🚀 Starting OTP Auto-Fill WebSocket Server...")
    print(f"📡 Server: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"📊 Dashboard: http://localhost:{SERVER_PORT}/dashboard")
    print("-" * 50)
    
    uvicorn.run(
        app, 
        host=SERVER_HOST, 
        port=SERVER_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()
