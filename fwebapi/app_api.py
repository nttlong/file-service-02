from __future__ import print_function

import routes
app =routes.app
app_config = routes.app_config

# import routes.api_file_upload


if __name__ == '__main__':
    app_config.logger.info("------------------------------------------------------")
    app_config.logger.info("web start with:")
    app_config.logger.info(dict(debug=app_config.debug, host=app_config.host, port=app_config.port))
    app_config.logger.info("------------------------------------------------------")
    app.run(
          debug=True,
          host= app_config.host,
          port=app_config.port,
          threaded=True
    )
    # print(app_config.full_url_root)
    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(
    #
    #     port=app_config.port,
    #     address=app_config.host
    # )
    # IOLoop.instance().start()
    # from tornado.wsgi import WSGIContainer
    # from tornado.httpserver import HTTPServer
    # from tornado.ioloop import IOLoop
    #
    #
    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(app_config.port)
    # IOLoop.instance().start()


