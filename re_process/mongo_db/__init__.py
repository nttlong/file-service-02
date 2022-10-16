import pymongo.database


def get_db(app_name) -> pymongo.database.Database:
    """
    lấy mongodb database dựa vào cấu hình trong re_process.configuration
    :param app_name:
    :return:
    """
    import ReCompact.db_context
    import re_process.config
    db = ReCompact.db_context.get_db_connection(
        host=re_process.config.mongo_db_config["host"],
        password=re_process.config.mongo_db_config["password"],
        username=re_process.config.mongo_db_config["username"],
        authSource=re_process.config.mongo_db_config["authSource"],
        replicaSet=re_process.config.mongo_db_config["replicaSet"],
        authMechanism=re_process.config.mongo_db_config["authMechanism"],
        port=re_process.config.mongo_db_config["port"]

    ).get_database(app_name)
    return db
