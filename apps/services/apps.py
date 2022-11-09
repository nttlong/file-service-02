import cy_kit
import apps.dbs.db_context
import apps.models.apps
import cy_docs
class AppServices:
    def __init__(
            self,
            db_context=cy_kit.single(
               apps.dbs.db_context.DbContext
            )
    ):
        self.db_context = db_context
    def get_list(self, app_name:str):
        """

        :param app_name:
        :return:
        """
        """
        {
            "Name":"lv-test",
            "Domain":"localhost",
            "LoginUrl":"http://localhost:5001/login",
            "ReturnUrlAfterSignIn":"http://localhost:5001",
            "Description":"By definition, a media server is a device that simply stores and shares media. This definition is vague, and can allow several different devices to be called media servers. It may be a NAS drive, a home theater PC running Windows XP Media Center Edition, MediaPortal or MythTV, or a commercial web server that hosts media for a large web site. In a home setting, a media server acts as an aggregator of information: video, audio, photos, books, etc. These different types of media (whether they originated on DVD, CD, digital camera, or in physical form) are stored on the media server's hard drive. Access to these is then available from a central location. It may also be used to run special applications that allow the user(s) to access the media from a remote location via the internet.","CreatedOn":"2022-02-14T06:46:00.957000","AppId":"5ffcf491-7a2f-4791-b44d-33e53ba99df3"},{"Name":"lv-elearning-cms","Domain":"localhost","LoginUrl":"http://localhost/login","ReturnUrlAfterSignIn":"http://localhost","Description":null,"CreatedOn":"2022-02-14T10:27:26.899000","AppId":"03001e63-9748-4b21-9491-5070ed46369e"},{"Name":"lv-docs","Domain":"localhost","LoginUrl":"~/login","ReturnUrlAfterSignIn":"~/","CreatedOn":"2022-06-06T09:56:22.305000","AppId":"629d6cd622304de6d0252a8c"},{"Name":"lv-cms","Domain":"172.16.13.72","LoginUrl":"http://172.16.13.72:5001/login","ReturnUrlAfterSignIn":"http://172.16.13.72:5001","Description":"A content management system, often abbreviated as CMS, is software that helps users create, manage, and modify content on a website without the need for specialized technical knowledge.\n\nIn simpler language, a content management system is a tool that helps you build a website without needing to write all the code from scratch (or even know how to code at all).\n\nInstead of building your own system for creating web pages, storing images, and other functions, the content management system handles all that basic infrastructure stuff for you so that you can focus on more forward-facing parts of your website.\n\nBeyond websites, you can also find content management systems for other functions – like document management.","CreatedOn":"2022-02-14T09:27:44.989000","AppId":"88bec806-74f0-4311-a9d9-66de7eba22b7"},{"Name":"long-test-123","Domain":"long-test-123.com.vn","LoginUrl":"http://long-test-123.com.vn/login","Description":null,"ReturnUrlAfterSignIn":"http://long-test-123.com.vn","CreatedOn":"2022-10-07T02:05:20.239000","AppId":"633f8960559cd4dac14ac976"},{"Name":"long-test","Domain":"long-test.com.vn","LoginUrl":"http://localhost/login","ReturnUrlAfterSignIn":"http://localhost/home","AppId":"b03776fc-acdb-471f-a4a1-fc0b0c2cb2fd"},{"Name":"lms","Domain":"lms.surelrn.vn","LoginUrl":"https://lms.surelrn.vn/","ReturnUrlAfterSignIn":"https://lms.surelrn.vn/","Description":"Hệ thống đào tạo trực tuyến Lạc Việt sẽ mang lại những trải nghiệm DẠY & HỌC tương tác nội dung học tập sinh động.\nKết nối  NHÀ TRƯỜNG - GIÁO VIÊN - HỌC SINH - PHỤ HUYNH","CreatedOn":"2022-02-16T04:42:26.106000","AppId":"21a334bc-e840-4cd8-9e13-f83323de138f"},{"Name":"hps-file-test","Domain":"localhost","LoginUrl":"http://localhost:4200/tester/auth/login","ReturnUrlAfterSignIn":"http://localhost:4200/tester","Description":null,"CreatedOn":"2022-02-18T10:01:28.566000","AppId":"e07ef903-9ed9-42ff-800e-62d3bc09e6b2"},{"Name":"codx-aws","Domain":"localhost","LoginUrl":"http://localhost","Description":null,"ReturnUrlAfterSignIn":"http://localhost","CreatedOn":"2022-10-11T07:06:42.754000","AppId":"634516026c64c179f9f0455b"},{"Name":"app-test-dev","Domain":"localhost","LoginUrl":"http://localhost/login","ReturnUrlAfterSignIn":"http://localhost","Description":"Dành cho DEV test, có thể xóa nội dung khi cần","CreatedOn":"2022-04-19T03:02:36.340000","AppId":"c3a79d4f-c571-4673-8e0e-5a7dda4060b5"
        }
        """
        app_expr = cy_docs.expr(apps.models.apps.App)
        aggr = self.db_context.db(app_name).doc(apps.models.apps.App).aggregate()
        aggr.project(
            app_expr._id >> app_expr.AppId,
            app_expr.Name,
            app_expr.Domain,
            app_expr.LoginUrl,
            app_expr.ReturnUrlAfterSignIn,
            app_expr.Description
        ).sort(app_expr.Name.asc())
        return list(aggr.to_json_convertable())

