#!/usr/bin/python
import SimpleHTTPServer
import SocketServer
from multiprocessing.process import Process
import json
import subprocess


class S(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def get_slurm(self):
        p = subprocess.Popen('squeue -h -t R -o %%A', shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        jobs = []
        for line in p.stdout.readlines():
            jobs.append(line.rstrip())
        return jobs

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        l = self.get_slurm()
        self.wfile.write(json.dumps(l))

    def log_request(self, message):
        return


def start_server(port):
    handler = S
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer(("", port), handler)
    httpd.serve_forever()


def server():
    PORT = 8000
    serv = Process(target=start_server, args=[PORT])
    serv.start()
    return serv


if __name__ == "__main__":
    start_server(8000)
