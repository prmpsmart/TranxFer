from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
all_perm = 'elramwMT'
authorizer.add_user('admin', 'password', '../', perm=all_perm)
authorizer.add_anonymous('../')

FTPHandler.authorizer = authorizer
ipp = addr, port = '127.0.0.1', 7767


FTPServer(ipp, FTPHandler).serve_forever()















