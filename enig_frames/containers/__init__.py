import enig



@enig.container()
class Container(enig.Singleton):
    class Services(enig.Singleton):

        web = None
        import enig_frames.services.accounts
        import enig_frames.services.applications
        import enig_frames.services.sercurities
        import enig_frames.services.hosts
        import enig_frames.services.web_apps
        import enig_frames.services.full_text_search
        import enig_frames.services.files
        web = enig.create_instance(enig_frames.services.web_apps.WebApp)
        host = enig.create_instance(enig_frames.services.hosts.Hosts)
        applications:enig_frames.services.applications.Applications= enig.create_instance(enig_frames.services.applications.Applications)
        """
        Dich vu app
        """
        accounts= enig.create_instance(enig_frames.services.accounts.Accounts)
        security = enig.create_instance(enig_frames.services.sercurities.Sercurities)
        search_engine = enig.create_instance(enig_frames.services.full_text_search.FullTextSearch)
        files = enig.create_instance(enig_frames.services.files.Files)

    import enig_frames.config
    import enig_frames.db_context
    config = enig.create_instance(enig_frames.config.Configuration)
    db_context = enig.create_instance(enig_frames.db_context.DbContext)

