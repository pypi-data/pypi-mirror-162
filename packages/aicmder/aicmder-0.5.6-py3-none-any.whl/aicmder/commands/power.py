from multiprocessing import Process, Event
from typing import List
import os
import aicmder as cmder
from aicmder.commands import register
from aicmder.commands.utils import _command_prefix as cmd 
import argparse

import falcon
import falcon.asgi
import uvicorn

class PowerService:

    def __init__(self, args):
        super().__init__()
        self.args = args


    async def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = falcon.MEDIA_TEXT  # Default is JSON, so override
        resp.text = ('ERR')
        if "s" in req.params:
            if req.params["s"] == self.args.secret:
                if "on" in req.params:
                    resp.text = ('ON')
                elif "off" in req.params:
                    resp.text = ('OFF')
                    os.system("shutdown now")
                elif "suspend" in req.params:
                    resp.text = ('SUSPEND')
                    os.system("systemctl suspend")

class HeartbeatService:

    async def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = falcon.MEDIA_TEXT  # Default is JSON, so override
        resp.text = ('OK')
            

class HttpService(Process):

    def __init__(self, args):
        super().__init__()
        self.args = args
        self.is_ready = Event()
        self.app = self.create_app()


    def create_app(self):
        import falcon.asgi
        app = falcon.asgi.App()
        # Resources are represented by long-lived class instances
        power = PowerService(self.args)
        heart = HeartbeatService()
        # things will handle all requests to the '/things' URL path
        app.add_route('/power', power)
        app.add_route('/heart', heart)
        return app


    def run(self):
        self.is_ready.set()
        uvicorn.run(self.app, host="0.0.0.0", port=self.args.http_port)

@register(name='{}.power'.format(cmd), description='Power manager.')
class PowerCommand:

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description=self.__class__.__doc__, prog='{} serve'.format(cmd), usage='%(prog)s', add_help=True)

        self.parser.add_argument('--http_port', '-p', type=int, default=7500,
                        help='server port for receiving HTTP requests')
        self.parser.add_argument('--secret', '-s', type=str, default=None, required=True,
                        help='A secret for managering the power')        
 

    def execute(self, argv: List) -> bool:
        args = self.parser.parse_args(argv)
        print("power", argv, args.http_port)
        httpService = HttpService(args)
        httpService.start()
        return True