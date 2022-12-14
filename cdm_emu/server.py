import json
import threading
from queue import Queue
from typing import Callable
import sys

from websocket_server import WebsocketServer

from cdm_emu.emulator import CDM8Emu

ws_client = None
exited = False


class EmulatorThread(threading.Thread):
    def __init__(self, emu: CDM8Emu, recvq: Queue, send_message: Callable[[dict], None]):
        super().__init__()
        self.emu = emu
        self.receive_queue = recvq
        self.send_message = send_message
        self.daemon = True
        self.running = False
        self.breakpoints: list[int] = []
        self.line_locations: list[int] = []


    def run(self) -> None:
        try:
            self.send_state()
            while not exited:
                self.handle_message()
        except NotImplementedError as e:
            self.send_message({'action': 'error', 'data': e.args[0]})
        except Exception as e:
            self.send_message({'action': 'error', 'data': str(type(e))})
        print('emulator thread stopped')

    def handle_message(self, block=True):
        if not block and self.receive_queue.empty():
            return
        msg: dict = self.receive_queue.get(block=True)
        if 'action' in msg.keys():
            action = msg['action']
            if action == 'step':
                self.command_step()
            if action == 'pause':
                self.running = False
            if action == 'continue':
                if not self.running:
                    self.command_run()
            if action == 'breakpoints':
                self.breakpoints = msg['data']
            if action == 'line_locations':
                self.line_locations = msg['data']

    def command_run(self):
        self.run_emu(breakOnLine=False)

    def command_step(self):
        self.run_emu(breakOnLine=True)

    def run_emu(self, breakOnLine = False):
        self.running = True
        stop_reason = 'pause'
        while self.running:
            self.emu.step()

            if self.emu.PC in self.line_locations and breakOnLine:
                stop_reason = 'step'
                break
            if self.emu.PC in self.breakpoints:
                stop_reason = 'breakpoint'
                break

            if self.emu.HALT:
                stop_reason = 'halt'
                break
            self.handle_message(block=False)
        self.running = False
        self.send_state()
        self.send_stop(stop_reason)

    def send_state(self):
        state = {
            'registers': {
                'r0': self.emu.regs[0],
                'r1': self.emu.regs[1],
                'r2': self.emu.regs[2],
                'r3': self.emu.regs[3],
                'pc': self.emu.PC,
                'sp': self.emu.SP,
                'ps': self.emu.CVZN,
            },
            'memory': self.emu.datamem
        }
        self.send_message({'action': 'state', 'data': state})

    def send_stop(self, reason: str):
        self.send_message({'action': 'stop', 'reason': reason})


def serve(emu: CDM8Emu, port: int):
    # print(port)

    def send_message(msg: dict):
        ws_server.send_message(ws_client, json.dumps(msg))

    receive_queue = Queue()
    emu_thread = EmulatorThread(emu, receive_queue, send_message)

    def on_new_client(client, server):
        global ws_client
        if ws_client is None:
            ws_client = client
            emu_thread.start()

    def on_client_left(client, server):
        global ws_client, exited
        if client == ws_client and not exited:
            print('client disconnected')
            exited = True
            ws_server.shutdown_abruptly()

    def on_message(client, server, message):
        if client != ws_client:
            return
        receive_queue.put(json.loads(message))

    ws_server = WebsocketServer(host='127.0.0.1', port=port)
    print(ws_server.port)
    sys.stdout.flush()
    ws_server.set_fn_new_client(on_new_client)
    ws_server.set_fn_client_left(on_client_left)
    ws_server.set_fn_message_received(on_message)
    ws_server.run_forever()

    print('Server thread stopped')
