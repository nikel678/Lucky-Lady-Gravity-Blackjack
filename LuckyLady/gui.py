import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from counter import ICounter
import base64
from PIL import Image
import asyncio
import numpy as np
from io import BytesIO


class GUI:
    def __init__(self):
        self.app = FastAPI()
        self.template_response = Jinja2Templates(directory="templates").TemplateResponse
        self.app.add_api_route("/", self.serve_gui, methods=["GET"])
        self.app.add_api_route("/hands", self.hands, methods=["GET"])
        self.counter = ICounter()

    async def serve_gui(self, request: Request):
        dealer_image_b64 = self.get_base64('state/dealer_cards.png')
        player_image_b64 = self.get_base64('state/player_cards.png')
        return self.template_response(request=request, name="gui.html", context={
            "dealer_image_b64":dealer_image_b64, 
            "player_image_b64":player_image_b64,
        })

    async def hands(self, request: Request):
        return self.counter.hand_history

    def start(self, port):
        uvicorn.run("main:gui.app", host="127.0.0.1", port=port, reload=False)

    def get_base64(self, path):
        img = Image.open(path)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return image_b64
