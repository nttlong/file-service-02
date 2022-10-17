import enig
import enig_frames.config


@enig.container()
class Container(enig.Singleton):
    class Services(enig.Singleton):

        web = None
        import enig_frames.services.accounts
        import enig_frames.services.applications
        import enig_frames.services.sercurities
        import enig_frames.services.hosts
        import enig_frames.services.web_apps
        web = enig.create_instance(enig_frames.services.web_apps.WebApp)
        host = enig.create_instance(enig_frames.services.hosts.Hosts)
        applications:enig_frames.services.applications.Applications= enig.create_instance(enig_frames.services.applications.Applications)
        """
        Dich vu app
        """
        accounts= enig.create_instance(enig_frames.services.accounts.Accounts)
        security = enig.create_instance(enig_frames.services.sercurities.Sercurities)
    config=enig.create_instance(enig_frames.config.Configuration)

