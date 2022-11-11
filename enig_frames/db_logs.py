import datetime
import threading

import enig
import ReCompact.dbm
import enig_frames.config
import enig_frames.db_context

field= ReCompact.dbm.field
@ReCompact.dbm.table(
    table_name="sys_app_logs",
    index=["CreateDate", "Exception", "AppName"]
)
class SysAppLogs:
    Content = field(str)
    CreateDate = field(datetime.datetime)
    Exception = field(str)
    AppName = field(str)


SysAppLogsDoc = SysAppLogs()


class DbLogs(enig.Singleton):
    def __init__(
            self,
            configuration: enig_frames.config.Configuration = enig.depen(
                enig_frames.config.Configuration
            ),
            db_context=enig.depen(
                enig_frames.db_context.DbContext
            )
    ):
        self.db_context: enig_frames.db_context.DbContext = db_context

    def debug(self, app_name: str, e: Exception):
        import traceback
        error = traceback.format_exc()

        def run(msg, ex):
            self.db_context.context('admin').insert_one(
                SysAppLogsDoc,
                SysAppLogsDoc.Content == msg,
                SysAppLogsDoc.Exception == str(ex),
                SysAppLogsDoc.AppName == app_name,
                SysAppLogsDoc.CreateDate == datetime.datetime.now()
            )

        threading.Thread(target=run, args=(error, e,)).start()

    async def get_top_logs_async(self, top=100):
        db = self.db_context.context('admin')
        agg = db.aggregate(SysAppLogsDoc)
        ret = await agg.project(
            SysAppLogsDoc.AppName,
            SysAppLogsDoc.Exception,
            SysAppLogsDoc.Content,
            SysAppLogsDoc.CreateDate
        ).sort(
            SysAppLogsDoc.CreateDate.desc()
        ).pager(
            page_size=top,
            page_index=0
        ).to_list_async()
        return ret
