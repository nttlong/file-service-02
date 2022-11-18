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

import enig_frames.loggers
import enig_frames.services.file_system_utils
import enig_frames.services.search_engine
import enig_frames.db_logs
import enig_frames.services.plugins
import enig_frames.services.gc_collect
import enig_frames.services.msgs
@enig.container()
class Container(enig.Singleton):
    class Services(enig.Singleton):
        web = None

        web = enig.depen(enig_frames.services.web_apps.WebApp)
        host = enig.depen(enig_frames.services.hosts.Hosts)
        applications: enig_frames.services.applications.Applications = enig.depen(
            enig_frames.services.applications.Applications)
        """
        Dich vu app
        """
        accounts = enig.depen(enig_frames.services.accounts.Accounts)
        security = enig.depen(enig_frames.services.sercurities.Sercurities)
        search_engine = enig.depen(enig_frames.services.search_engine.SearchEngineService)
        files = enig.depen(enig_frames.services.files.Files)
        file_system: enig_frames.services.file_system.FileSystem = enig.depen(
            enig_frames.services.file_system.FileSystem)
        plugin_services: enig_frames.services.plugins.PlugInService = enig.depen(
            enig_frames.services.plugins.PlugInService
        )
        msg_service = enig.depen(
            enig_frames.services.msgs.Message

        )
    clean_up_service=enig.depen(enig_frames.services.gc_collect.GCCollec)
    config = enig.depen(enig_frames.config.Configuration)
    db_context = enig.depen(enig_frames.db_context.DbContext)
    # web_application = enig.depen(enig_fast_api.application.WebApp)
    loggers = enig.depen(enig_frames.loggers.Loggers)
    file_system_utils_service = enig.depen(enig_frames.services.file_system_utils.FileSystemUtils)
    db_log = enig.depen(enig_frames.db_logs.DbLogs)
