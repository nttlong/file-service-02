import quicky.config


def save_config(app, app_config: quicky.config.Config):
    setattr(app, "app_config", app_config)


def get_config() -> quicky.config.Config:
    from flask import current_app
    return getattr(current_app, "app_config")
