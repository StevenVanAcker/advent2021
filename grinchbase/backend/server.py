#!/usr/bin/env python3

import logging
import os
import string
from concurrent import futures

import grinchbase_pb2
import grinchbase_pb2_grpc
import grpc
from TBAG import TBAG


def preload_gamedata(fn):
    def __inner(self, *args, **kwargs):
        request, context = args
        headers = dict([(k.lower(), v.lower())
                        for (k, v) in context.invocation_metadata()])

        if "x-game-auth" in headers:
            gameid = headers["x-game-auth"]

            if len(gameid) == 32 and all(c in string.hexdigits
                                         for c in gameid):
                kwargs["gamedata"] = gameid

        return fn(self, *args, **kwargs)

    return __inner


class GrinchBaseServer(grinchbase_pb2_grpc.GrinchBaseServicer):
    def __init__(self):
        self.clients = {}

    @preload_gamedata
    def HandleCommand(self, request, context, gamedata=None):
        res = grinchbase_pb2.CommandResult(code=1,
                                           type="text",
                                           extra="",
                                           text="Something went wrong")

        if gamedata is None:
            return res

        try:
            statefile = os.path.join("states", f"{gamedata}.json")
            tbag = TBAG(statefile)
            output = tbag.handle(request.text)
            outtype = "text"
            extra = ""
            if tbag.setName:
                outtype = "name"
                tbag.setName = False
                extra = tbag.getProperty("name")
            res = grinchbase_pb2.CommandResult(code=0,
                                               type=outtype,
                                               extra=extra,
                                               text=output)
        except Exception as e:
            logging.error(f"Exception in HandleCommand: {e}")

        return res


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grinchbase_pb2_grpc.add_GrinchBaseServicer_to_server(
        GrinchBaseServer(), server)
    server.add_insecure_port('[::]:12345')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    serve()
