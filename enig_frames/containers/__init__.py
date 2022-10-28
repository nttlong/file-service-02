import enig

import enig_frames.services.accounts
import enig_frames.services.applications
import enig_frames.services.sercurities
import enig_frames.services.hosts
import enig_frames.services.web_apps
import enig_frames.services.files
import enig_frames.services.file_system
import enig_frames.config
import enig_frames.db_context
import enig_fast_api.application
import enig_frames.loggers
import enig_frames.services.file_system_utils
import enig_frames.services.search_engine
import enig_frames.db_logs
import enig_frames.services.plugins


@enig.container()
class Container(enig.Singleton):
    class Services(enig.Singleton):
        web = None

        web = enig.create_instance(enig_frames.services.web_apps.WebApp)
        host = enig.create_instance(enig_frames.services.hosts.Hosts)
        applications: enig_frames.services.applications.Applications = enig.create_instance(
            enig_frames.services.applications.Applications)
        """
        Dich vu app
        """
        accounts = enig.create_instance(enig_frames.services.accounts.Accounts)
        security = enig.create_instance(enig_frames.services.sercurities.Sercurities)
        search_engine = enig.create_instance(enig_frames.services.search_engine.SearchEngineService)
        files = enig.create_instance(enig_frames.services.files.Files)
        file_system: enig_frames.services.file_system.FileSystem = enig.create_instance(
            enig_frames.services.file_system.FileSystem)
        plugin_services: enig_frames.services.plugins.PlugInService = enig.create_instance(
            enig_frames.services.plugins.PlugInService
        )

    config = enig.create_instance(enig_frames.config.Configuration)
    db_context = enig.create_instance(enig_frames.db_context.DbContext)
    web_application = enig.create_instance(enig_fast_api.application.WebApp)
    loggers = enig.create_instance(enig_frames.loggers.Loggers)
    file_system_utils_service = enig.create_instance(enig_frames.services.file_system_utils.FileSystemUtils)
    db_log = enig.create_instance(enig_frames.db_logs.DbLogs)
