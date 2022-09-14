import fasty
@fasty.api_get("/system/info")
async def system_info():
    return fasty.config.host