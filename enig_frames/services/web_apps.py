import enig
import enig_frames.config
import enig_frames.services.hosts


class WebApp(enig.Singleton):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(
                     enig_frames.config.Configuration
                 ),
                 host: enig_frames.services.hosts.Hosts = enig.depen(
                     enig_frames.services.hosts.Hosts

                 )):
        self.host: enig_frames.services.hosts.Hosts = host
        self.configuration: enig_frames.config.Configuration = configuration
        from fastapi.templating import Jinja2Templates
        self.templates = Jinja2Templates(directory=self.configuration.config.jinja_templates_dir)

    def render(self, file, data):
        return self.templates.TemplateResponse(
            file,
            data
        )
