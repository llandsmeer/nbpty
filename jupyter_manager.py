import os
import json
import queue

import jupyter_client

class JupyterManager:
    def __init__(self, blocks):
        self.blocks = blocks
        self.connection_file = os.path.abspath('_jupyter.json')
        self.client = jupyter_client.BlockingKernelClient()
        self.execute_requests = {}

    def launch(self):
        self.blocks.add_terminal('Jupyter Kernel', [
            '/usr/bin/env', 'jupyter', 'console',
                f'--ZMQTerminalIPythonApp.connection_file={self.connection_file}'])
        while not os.path.exists(self.connection_file):
            pass
        self.client.load_connection_file(self.connection_file)
        self.client.start_channels()

        self.blocks.inputs.add(self.client.iopub_channel.socket.FD, self.edge_event)
        self.blocks.inputs.add(self.client.shell_channel.socket.FD, self.edge_event)

    def edge_event(self):
        self.clear_buffers()

    def launch_editor(self, header='Python Cell', code=''):
        self.blocks.add_eval(header, self, code)

    def clear_buffers(self):
        try:
            while True:
                msg = self.client.get_shell_msg(timeout=0)
                self.handle_shell_msg(msg)
        except queue.Empty:
            pass
        try:
            while True:
                msg = self.client.get_iopub_msg(timeout=0)
                self.handle_iopub_msg(msg)
        except queue.Empty:
            pass

    def handle_shell_msg(self, msg):
        pid = msg['parent_header']['msg_id']
        if pid in self.execute_requests:
            f = self.execute_requests[pid]
            if msg['content']['status'] == 'error':
                tb = '\n'.join(msg['content']['traceback'])
                ename = msg['content']['ename']
                evalue = msg['content']['evalue']
                f(f'{tb}\n\n{ename}\n{evalue}')
            else:
                content_dump = json.dumps(msg['content'], default=str, indent=1)
                f('# execution ok')
        else:
            print('discarding', msg['msg_type'], msg['msg_id'])
            dump = json.dumps(msg, default=str, indent=1)
            #print(dump)

    def handle_iopub_msg(self, msg):
        if msg['msg_type'] == 'status':
            #print(msg['content']['execution_state']) # => busy / idle
            pass
        elif msg['msg_type'] == 'stream':
            pid = msg['parent_header']['msg_id'] if 'msg_id' in msg['parent_header'] else None
            if pid in self.execute_requests:
                f = self.execute_requests[pid]
                #msg['content']['name'] == 'stdout'
                if 'text' in msg['content']:
                    f(msg['content']['text'])
                else:
                    dump = json.dumps(msg['content'], default=str, indent=1)
                    print(dump)
            else:
                print(msg['content']['text'])
        elif msg['msg_type'] == 'execute_input':
            pass
        else:
            print('discarding iopub', msg['msg_type'], msg['msg_id'])
            dump = json.dumps(msg['content'], default=str, indent=1)
            print(dump)

    def stop_listen(self, id_):
        if id_ is None: return
        del self.execute_requests[id_]

    def execute(self, code, f):
        id_ = self.client.execute(code)
        self.execute_requests[id_] = f
        self.clear_buffers()
        return id_
