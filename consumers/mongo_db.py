import pymongo.database
from  consumers import config

def get_db(app_name) -> pymongo.database.Database:
    """
    lấy mongodb database dựa vào cấu hình trong re_process.configuration
    :param app_name:
    :return:
    """
    import ReCompact.db_context
    # import configuration
    db= None
    if config.mongo_db_config.get("replicaSet"):
        db = ReCompact.db_context.get_db_connection(
            host=config.mongo_db_config["host"],
            password=config.mongo_db_config["password"],
            username=config.mongo_db_config["username"],
            authSource=config.mongo_db_config["authSource"],
            replicaSet=config.mongo_db_config["replicaSet"],
            authMechanism=config.mongo_db_config["authMechanism"],
            port=config.mongo_db_config["port"]

        ).get_database(app_name)
    else:
        db = ReCompact.db_context.get_db_connection(
            host=config.mongo_db_config["host"],
            password=config.mongo_db_config["password"],
            username=config.mongo_db_config["username"],
            authSource=config.mongo_db_config["authSource"],
            authMechanism=config.mongo_db_config["authMechanism"],
            port=config.mongo_db_config["port"]

        ).get_database(app_name)
    return db
