"""
WebSocket server for streaming voice input
"""

import asyncio
import json
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import speech_recognition as sr
import io
import base64


class WebSocketServer:
    """WebSocket server for voice input"""
    
    def __init__(self, analysis_agent=None):
        """
        Initialize WebSocket server
        
        Args:
            analysis_agent: Instance of analysis agent to process queries
        """
        self.app = FastAPI()
        self.analysis_agent = analysis_agent
        self.recognizer = sr.Recognizer()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def get():
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Excel Analysis Agent - Voice Input</title>
            </head>
            <body>
                <h1>Excel Analysis Agent</h1>
                <p>WebSocket endpoint: ws://localhost:8000/ws</p>
                <p>Use WebSocket client to send audio data</p>
            </body>
            </html>
            """)
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    # Receive audio data
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    if message.get("type") == "audio":
                        # Process audio
                        audio_data = message.get("data", "")
                        text = await self._process_audio(audio_data)
                        
                        # Send transcription back
                        await websocket.send_json({
                            "type": "transcription",
                            "text": text
                        })
                        
                        # If analysis agent is available, process the query
                        if self.analysis_agent and text:
                            result = await self._process_query(text)
                            await websocket.send_json({
                                "type": "analysis_result",
                                "result": result
                            })
                    
                    elif message.get("type") == "text":
                        # Direct text input
                        text = message.get("text", "")
                        if self.analysis_agent and text:
                            result = await self._process_query(text)
                            await websocket.send_json({
                                "type": "analysis_result",
                                "result": result
                            })
            
            except WebSocketDisconnect:
                print("Client disconnected")
            except Exception as e:
                print(f"WebSocket error: {e}")
                await websocket.close()
    
    async def _process_audio(self, audio_data: str) -> str:
        """
        Process audio data and convert to text (mock STT)
        
        Args:
            audio_data: Base64 encoded audio data or audio bytes
        
        Returns:
            Transcribed text
        """
        # Mock implementation - in production, use real STT service
        # For now, return a placeholder
        try:
            # If audio_data is base64, decode it
            if isinstance(audio_data, str):
                # Try to decode base64
                try:
                    audio_bytes = base64.b64decode(audio_data)
                except:
                    # If not base64, treat as text (for testing)
                    return audio_data
            
            # Mock STT - in production, use:
            # - Google Speech-to-Text API
            # - Azure Speech Services
            # - AWS Transcribe
            # - Whisper API
            
            # For now, return placeholder
            return "Mock transcription: Please use text input for now"
        
        except Exception as e:
            print(f"Error processing audio: {e}")
            return ""
    
    async def _process_query(self, query: str) -> dict:
        """
        Process analysis query
        
        Args:
            query: User's question
        
        Returns:
            Analysis result
        """
        if self.analysis_agent:
            return await asyncio.to_thread(
                self.analysis_agent.analyze,
                query
            )
        return {"error": "Analysis agent not available"}
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the WebSocket server
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)

