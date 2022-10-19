import enig_frames.containers
from fastapi import FastAPI
print("XXXXXXXXXXXXXXXX")
print(__name__)
container = enig_frames.containers.Container
app = container.web_application.create_web_app(__name__)
