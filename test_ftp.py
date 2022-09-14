# from pyftpdlib.handlers import FTPHandler
# from pyftpdlib.servers import FTPServer
# from pyftpdlib.authorizers import WindowsAuthorizer
#
# def main():
#     authorizer = WindowsAuthorizer()
#     # Use Guest user with empty password to handle anonymous sessions.
#     # Guest user must be enabled first, empty password set and profile
#     # directory specified.
#     #authorizer = WindowsAuthorizer(anonymous_user="Guest", anonymous_password="")
#     handler = FTPHandler
#     handler.authorizer = authorizer
#     server = FTPServer(('14.241.179.38', 2121), handler)
#     server.serve_forever()
#
# if __name__ == "__main__":
#     main()
import sys
