"""
Thee must use get_producer().topics.topic.<topic_key>.send(<dic data>)
or thy can use getattr(get_producer().topics.topic,"<topic key with special character>").send(<dic data>)
"""


def get_producer():
    """
    Create new producer
    :return:
    """
    import web.settings  # Dùng web settings để lấy thông tin broker server
    import ReCompact_Kafka.producer
    bs = ReCompact_Kafka.producer.Bootstrap(
        web.settings.KAFKA["BROKERS"]
    )
    return bs.producers
