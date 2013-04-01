#!/usr/bin/python
#
# Simple-minded static http/https server, for when things go really wrong.
#
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import BaseHTTPServer, ssl, subprocess, shlex

def serve_text(port, text, code=200, pem_path=None):
    """ 
    launch an http server that returns the given text/code
    (for any request). If path to a pem file is specified,
    launch an https server.
    
    This never returns.
    """
    class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(code)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(text)

    httpd = BaseHTTPServer.HTTPServer(('', port), Handler)
    if pem_path:
        httpd.socket = ssl.wrap_socket (httpd.socket, certfile=pem_path, 
                                        server_side=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

def system(cmd):
    """
    execute a shell command and return its output or throw its error text.
    """
    if type(cmd) != list:
        cmd = shlex.split(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (text,err) = p.communicate()
    if p.returncode != 0:
        raise Exception('Failed "%s": %s' % (cmd, err))
    return text

