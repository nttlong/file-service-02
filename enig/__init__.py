import logging
import os.path
import pathlib
import sys
import threading
from typing import TypeVar, Generic, List
__working_dir__=None
__lock__=threading.Lock()
__catch_log__ ={}
import kink
import yaml
from kink import di
from matplotlib import __getattr__

T = TypeVar('T')
__cache_yam_dict__ = {}

__DbContext__cache__ ={}
__DbContext__init__ ={}
__DbContext__cache__lock__ = threading.Lock()
class Singleton(object):
    def __new__(cls, *args, **kw):
        global __DbContext__cache__
        global __DbContext__init__
        global __DbContext__cache__lock__
        key = f"{cls.__module__}/{cls.__name__}"
        if not hasattr(cls, '_instance'):
            __DbContext__cache__lock__.acquire()
            try:
                orig = super(Singleton, cls)
                cls._instance = orig.__new__(cls)
               # old_init=getattr(cls,"__init__")

                # cls._instance.__init__(*args, **kw)
                # def empty(obj,*a,**b):
                #     if __DbContext__init__.get(key) is None:
                #         old_init(obj,*a,**b)
                #         __DbContext__init__[key]=key
                #
                #
                # setattr(cls,"__init__",empty)
            except Exception as e:
                raise e
            finally:
                __DbContext__cache__lock__.release()
        return cls._instance


def inject(cls,*args,**kwargs):
    return kink.inject(cls,*args,**kwargs)
__cache_depen__ = {}
__lock_depen__ =threading.Lock()
def depen(cls:T,*args,**kwargs)->T:
    if issubclass(cls,Singleton):
        key=f"{cls.__module__}/{cls.__name__}"
        ret= None
        if __cache_depen__.get(key) is None:
            # __lock_depen__.acquire()
            try:
                ret= kink.inject(cls)
                v=ret(*args,**kwargs)
                __cache_depen__[key] = v
            except Exception as e:
                raise e
            # finally:
            #     __lock_depen__.release()
        return __cache_depen__[key]
    else:
        ret = kink.inject(cls)
        return  ret(*args,**kwargs)
def create_instance(cls:T,*args,**kwargs)->T:
    ret = kink.inject(cls)
    return ret(*args, **kwargs)

def get_working_dir():
    global __working_dir__
    global __lock__
    if __working_dir__ is None:
        __lock__.acquire()
        __working_dir__=str(pathlib.Path(__file__).parent.parent)
        __lock__.release()
    return __working_dir__

def load_from_yam_file(path_to_yam_file)->dict:
    """
    Onetime read yaml filr to dict
    On the next time this method will return from cache
    :param path_to_yam_file:
    :return:
    """
    global __cache_yam_dict__
    global __lock__
    p=path_to_yam_file
    if p[0:2]=="./":
        p=p[2:]
        p=os.path.join(get_working_dir(),p).replace('/',os.sep)
    if __cache_yam_dict__.get(p) is None:
        try:
            __lock__.acquire()
            print(f"Load config from {p}")
            with open(p, 'r') as stream:
                __config__ = yaml.safe_load(stream)
                __cache_yam_dict__[p] = __config__
        finally:
            __lock__.release()

    return __cache_yam_dict__.get(p)
class cls_dict:
    def __init__(self,data:dict):
        self.__data__=data
    def __parse__(self,ret):
        if isinstance(ret, dict):
            return cls_dict(ret)
        if isinstance(ret, list):
            ret_list = []
            for x in ret:
                ret_list += {self.__parse__(x)}
        return ret
    def __getattr__(self, item):
        if item[0:2]=="__" and item[-2:]=="__":
            return self.__dict__.get(item)
        ret= self.__data__.get(item)
        if isinstance(ret,dict):
            return cls_dict(ret)
        if isinstance(ret,list):
            ret_list=[]
            for x in ret:
                ret_list+= {self.__parse__(x)}
            return ret_list
        return ret
def get_logger(logger_name:str="enig", logger_dir:str="./logs")-> logging.Logger:
    global __lock__
    global __catch_log__
    if logger_dir[0:2]=="./":
        logger_dir=logger_dir[2:logger_dir.__len__()]
        working_dir = str(pathlib.Path(__file__).parent.parent)
        logger_dir = os.path.join(working_dir,logger_dir)
        if not os.path.isdir(logger_dir):
            os.makedirs(logger_dir)

    if __catch_log__.get(logger_name) is not None:
        return __catch_log__.get(logger_name)
    __lock__.acquire()
    try:
        # create logger for prd_ci
        log = logging.Logger(logger_name)
        # log.setLevel(level=logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        full_log_dir= os.path.join(logger_dir,"logs","apps",logger_name)
        if not os.path.isdir(full_log_dir):
            os.makedirs(full_log_dir)

        info_handler = logging.FileHandler(os.path.join(full_log_dir,"log.txt"))
        info_handler.setFormatter(formatter)

        log.addHandler(info_handler)
        __catch_log__[logger_name]=log
        return log
    finally:
        __lock__.release()

def container(*args,**kwargs):
    fx=args
    def container_wrapper(cls):
        old_getattr=None
        if hasattr(cls,"__getattribute__"):
            old_getattr = getattr(cls,"__getattribute__")

        def __container__getattribute____(obj, item):
            ret= None
            if item[0:2]=="__" and item[-2]=="__":
                if old_getattr is not None:
                    return old_getattr(obj,item)
                else:
                    ret = cls.__dict__.get(item)

            else:
                ret = cls.__dict__.get(item)
            if ret is None:
                __annotations__ = cls.__dict__.get('__annotations__')
                if isinstance(__annotations__,dict):
                    ret =__annotations__.get(item)
            import inspect
            if inspect.isclass(ret):
                ret=container_wrapper(ret)
                return ret


            return ret
        setattr(cls,"__getattribute__",__container__getattribute____)
        return cls()

    return container_wrapper


def convert_to_dict(str_path:str,value):
    items = str_path.split('.')
    if items.__len__()==1:
        return {items[0]:value}
    else:
        return {items[0]: convert_to_dict(str_path[items[0].__len__()+1:],value)}

from copy import deepcopy

def __dict_of_dicts_merge__(x, y):
    z = {}
    if isinstance(x,dict) and isinstance(y,dict):
        overlapping_keys = x.keys() & y.keys()
        for key in overlapping_keys:
            z[key] = __dict_of_dicts_merge__(x[key], y[key])
        for key in x.keys() - overlapping_keys:
            z[key] = deepcopy(x[key])
        for key in y.keys() - overlapping_keys:
            z[key] = deepcopy(y[key])
        return z
    else:
        return y

def combine_agruments(data:dict):
    ret={}
    for x in sys.argv:
        if x.split('=').__len__()==2:
            k=x.split('=')[0]
            if x.split('=').__len__()==2:
                v=x.split('=')[1]
                c= convert_to_dict(k,v)
                ret=__dict_of_dicts_merge__(ret,c)
            else:
                c = convert_to_dict(k, None)
                ret = __dict_of_dicts_merge__(ret, c)
    ret = __dict_of_dicts_merge__(data,ret)
    return ret
def combine_os_variables(data:dict):
    import os
    ret={}
    for k,v in os.environ.items():
        if k.startswith('config.'):
            k=k['config.'.__len__():]
            c = convert_to_dict(k,v)
            ret=__dict_of_dicts_merge__(ret,c)
    ret = __dict_of_dicts_merge__(data,ret)
    return ret
def create_instance_from_moudle(module_name,class_name,force_reload=False):
    import importlib
    if force_reload:
        if module_name in list(sys.modules.keys()):
            importlib.reload(sys.modules[module_name])
    mdl = importlib.import_module(module_name)
    cls = getattr(mdl,class_name)
    return depen(cls)

import mimetypes

mime_data={}
mime_data[".323"]="text/h323"
mime_data[".3g2"]="video/3gpp2"
mime_data[".3gp2"]="video/3gpp2"
mime_data[".3gp"]="video/3gpp"
mime_data[".3gpp"]="video/3gpp"
mime_data[".aaf"]="application/octet-stream"
mime_data[".aac"]="audio/aac"
mime_data[".aca"]="application/octet-stream"
mime_data[".accdb"]="application/msaccess"
mime_data[".accde"]="application/msaccess"
mime_data[".accdt"]="application/msaccess"
mime_data[".acx"]="application/internet-property-stream"
mime_data[".adt"]="audio/vnd.dlna.adts"
mime_data[".adts"]="audio/vnd.dlna.adts"
mime_data[".afm"]="application/octet-stream"
mime_data[".ai"]="application/postscript"
mime_data[".aif"]="audio/x-aiff"
mime_data[".aifc"]="audio/aiff"
mime_data[".aiff"]="audio/aiff"
mime_data[".application"]="application/x-ms-application"
mime_data[".art"]="image/x-jg"
mime_data[".asd"]="application/octet-stream"
mime_data[".asf"]="video/x-ms-asf"
mime_data[".asi"]="application/octet-stream"
mime_data[".asm"]="text/plain"
mime_data[".asr"]="video/x-ms-asf"
mime_data[".asx"]="video/x-ms-asf"
mime_data[".atom"]="application/atom+xml"
mime_data[".au"]="audio/basic"
mime_data[".avi"]="video/avi"
mime_data[".axs"]="application/olescript"
mime_data[".bas"]="text/plain"
mime_data[".bcpio"]="application/x-bcpio"
mime_data[".bin"]="application/octet-stream"
mime_data[".bmp"]="image/bmp"
mime_data[".c"]="text/plain"
mime_data[".cab"]="application/vnd.ms-cab-compressed"
mime_data[".calx"]="application/vnd.ms-office.calx"
mime_data[".cat"]="application/vnd.ms-pki.seccat"
mime_data[".cdf"]="application/x-cdf"
mime_data[".chm"]="application/octet-stream"
mime_data[".class"]="application/x-java-applet"
mime_data[".clp"]="application/x-msclip"
mime_data[".cmx"]="image/x-cmx"
mime_data[".cnf"]="text/plain"
mime_data[".cod"]="image/cis-cod"
mime_data[".cpio"]="application/x-cpio"
mime_data[".cpp"]="text/plain"
mime_data[".crd"]="application/x-mscardfile"
mime_data[".crl"]="application/pkix-crl"
mime_data[".crt"]="application/x-x509-ca-cert"
mime_data[".csh"]="application/x-csh"
mime_data[".css"]="text/css"
mime_data[".csv"]="application/octet-stream"
mime_data[".cur"]="application/octet-stream"
mime_data[".dcr"]="application/x-director"
mime_data[".deploy"]="application/octet-stream"
mime_data[".der"]="application/x-x509-ca-cert"
mime_data[".dib"]="image/bmp"
mime_data[".dir"]="application/x-director"
mime_data[".disco"]="text/xml"
mime_data[".dll"]="application/x-msdownload"
mime_data[".dll.configuration"]="text/xml"
mime_data[".dlm"]="text/dlm"
mime_data[".doc"]="application/msword"
mime_data[".docm"]="application/vnd.ms-word.document.macroEnabled.12"
mime_data[".docx"]="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
mime_data[".dot"]="application/msword"
mime_data[".dotm"]="application/vnd.ms-word.template.macroEnabled.12"
mime_data[".dotx"]="application/vnd.openxmlformats-officedocument.wordprocessingml.template"
mime_data[".dsp"]="application/octet-stream"
mime_data[".dtd"]="text/xml"
mime_data[".dvi"]="application/x-dvi"
mime_data[".dvr-ms"]="video/x-ms-dvr"
mime_data[".dwf"]="drawing/x-dwf"
mime_data[".dwp"]="application/octet-stream"
mime_data[".dxr"]="application/x-director"
mime_data[".eml"]="message/rfc822"
mime_data[".emz"]="application/octet-stream"
mime_data[".eot"]="application/vnd.ms-fontobject"
mime_data[".eps"]="application/postscript"
mime_data[".etx"]="text/x-setext"
mime_data[".evy"]="application/envoy"
mime_data[".exe"]="application/octet-stream"
mime_data[".exe.configuration"]="text/xml"
mime_data[".fdf"]="application/vnd.fdf"
mime_data[".fif"]="application/fractals"
mime_data[".fla"]="application/octet-stream"
mime_data[".flr"]="x-world/x-vrml"
mime_data[".flv"]="video/x-flv"
mime_data[".gif"]="image/gif"
mime_data[".gtar"]="application/x-gtar"
mime_data[".gz"]="application/x-gzip"
mime_data[".h"]="text/plain"
mime_data[".hdf"]="application/x-hdf"
mime_data[".hdml"]="text/x-hdml"
mime_data[".hhc"]="application/x-oleobject"
mime_data[".hhk"]="application/octet-stream"
mime_data[".hhp"]="application/octet-stream"
mime_data[".hlp"]="application/winhlp"
mime_data[".hqx"]="application/mac-binhex40"
mime_data[".hta"]="application/hta"
mime_data[".htc"]="text/x-component"
mime_data[".htm"]="text/html"
mime_data[".html"]="text/html"
mime_data[".htt"]="text/webviewhtml"
mime_data[".hxt"]="text/html"
mime_data[".ico"]="image/x-icon"
mime_data[".ics"]="text/calendar"
mime_data[".ief"]="image/ief"
mime_data[".iii"]="application/x-iphone"
mime_data[".inf"]="application/octet-stream"
mime_data[".ins"]="application/x-internet-signup"
mime_data[".isp"]="application/x-internet-signup"
mime_data[".IVF"]="video/x-ivf"
mime_data[".jar"]="application/java-archive"
mime_data[".java"]="application/octet-stream"
mime_data[".jck"]="application/liquidmotion"
mime_data[".jcz"]="application/liquidmotion"
mime_data[".jfif"]="image/pjpeg"
mime_data[".jpb"]="application/octet-stream"
mime_data[".jpe"]="image/jpeg"
mime_data[".jpeg"]="image/jpeg"
mime_data[".jpg"]="image/jpeg"
mime_data[".js"]="application/javascript"
mime_data[".json"]="application/json"
mime_data[".jsx"]="application/javascrip"
mime_data[".latex"]="application/x-latex"
mime_data[".lit"]="application/x-ms-reader"
mime_data[".lpk"]="application/octet-stream"
mime_data[".lsf"]="video/x-la-asf"
mime_data[".lsx"]="video/x-la-asf"
mime_data[".lzh"]="application/octet-stream"
mime_data[".m13"]="application/x-msmediaview"
mime_data[".m14"]="application/x-msmediaview"
mime_data[".m1v"]="video/mpeg"
mime_data[".m2ts"]="video/vnd.dlna.mpeg-tts"
mime_data[".m3u"]="audio/x-mpegurl"
mime_data[".m4a"]="audio/mp4"
mime_data[".m4v"]="video/mp4"
mime_data[".man"]="application/x-troff-man"
mime_data[".manifest"]="application/x-ms-manifest"
mime_data[".map"]="text/plain"
mime_data[".mdb"]="application/x-msaccess"
mime_data[".mdp"]="application/octet-stream"
mime_data[".me"]="application/x-troff-me"
mime_data[".mht"]="message/rfc822"
mime_data[".mhtml"]="message/rfc822"
mime_data[".mid"]="audio/mid"
mime_data[".midi"]="audio/mid"
mime_data[".mix"]="application/octet-stream"
mime_data[".mmf"]="application/x-smaf"
mime_data[".mno"]="text/xml"
mime_data[".mny"]="application/x-msmoney"
mime_data[".mov"]="video/quicktime"
mime_data[".movie"]="video/x-sgi-movie"
mime_data[".mp2"]="video/mpeg"
mime_data[".mp3"]="audio/mpeg"
mime_data[".mp4"]="video/mp4"
mime_data[".mp4v"]="video/mp4"
mime_data[".mpa"]="video/mpeg"
mime_data[".mpe"]="video/mpeg"
mime_data[".mpeg"]="video/mpeg"
mime_data[".mpg"]="video/mpeg"
mime_data[".mpp"]="application/vnd.ms-project"
mime_data[".mpv2"]="video/mpeg"
mime_data[".ms"]="application/x-troff-ms"
mime_data[".msi"]="application/octet-stream"
mime_data[".mso"]="application/octet-stream"
mime_data[".mvb"]="application/x-msmediaview"
mime_data[".mvc"]="application/x-miva-compiled"
mime_data[".nc"]="application/x-netcdf"
mime_data[".nsc"]="video/x-ms-asf"
mime_data[".nws"]="message/rfc822"
mime_data[".ocx"]="application/octet-stream"
mime_data[".oda"]="application/oda"
mime_data[".odc"]="text/x-ms-odc"
mime_data[".ods"]="application/oleobject"
mime_data[".oga"]="audio/ogg"
mime_data[".ogg"]="video/ogg"
mime_data[".ogv"]="video/ogg"
mime_data[".one"]="application/onenote"
mime_data[".onea"]="application/onenote"
mime_data[".onetoc"]="application/onenote"
mime_data[".onetoc2"]="application/onenote"
mime_data[".onetmp"]="application/onenote"
mime_data[".onepkg"]="application/onenote"
mime_data[".osdx"]="application/opensearchdescription+xml"
mime_data[".otf"]="font/otf"
mime_data[".p10"]="application/pkcs10"
mime_data[".p12"]="application/x-pkcs12"
mime_data[".p7b"]="application/x-pkcs7-certificates"
mime_data[".p7c"]="application/pkcs7-mime"
mime_data[".p7m"]="application/pkcs7-mime"
mime_data[".p7r"]="application/x-pkcs7-certreqresp"
mime_data[".p7s"]="application/pkcs7-signature"
mime_data[".pbm"]="image/x-portable-bitmap"
mime_data[".pcx"]="application/octet-stream"
mime_data[".pcz"]="application/octet-stream"
mime_data[".pdf"]="application/pdf"
mime_data[".pfb"]="application/octet-stream"
mime_data[".pfm"]="application/octet-stream"
mime_data[".pfx"]="application/x-pkcs12"
mime_data[".pgm"]="image/x-portable-graymap"
mime_data[".pko"]="application/vnd.ms-pki.pko"
mime_data[".pma"]="application/x-perfmon"
mime_data[".pmc"]="application/x-perfmon"
mime_data[".pml"]="application/x-perfmon"
mime_data[".pmr"]="application/x-perfmon"
mime_data[".pmw"]="application/x-perfmon"
mime_data[".png"]="image/png"
mime_data[".pnm"]="image/x-portable-anymap"
mime_data[".pnz"]="image/png"
mime_data[".pot"]="application/vnd.ms-powerpoint"
mime_data[".potm"]="application/vnd.ms-powerpoint.template.macroEnabled.12"
mime_data[".potx"]="application/vnd.openxmlformats-officedocument.presentationml.template"
mime_data[".ppam"]="application/vnd.ms-powerpoint.addin.macroEnabled.12"
mime_data[".ppm"]="image/x-portable-pixmap"
mime_data[".pps"]="application/vnd.ms-powerpoint"
mime_data[".ppsm"]="application/vnd.ms-powerpoint.slideshow.macroEnabled.12"
mime_data[".ppsx"]="application/vnd.openxmlformats-officedocument.presentationml.slideshow"
mime_data[".ppt"]="application/vnd.ms-powerpoint"
mime_data[".pptm"]="application/vnd.ms-powerpoint.presentation.macroEnabled.12"
mime_data[".pptx"]="application/vnd.openxmlformats-officedocument.presentationml.presentation"
mime_data[".prf"]="application/pics-rules"
mime_data[".prm"]="application/octet-stream"
mime_data[".prx"]="application/octet-stream"
mime_data[".ps"]="application/postscript"
mime_data[".psd"]="application/octet-stream"
mime_data[".psm"]="application/octet-stream"
mime_data[".psp"]="application/octet-stream"
mime_data[".pub"]="application/x-mspublisher"
mime_data[".qt"]="video/quicktime"
mime_data[".qtl"]="application/x-quicktimeplayer"
mime_data[".qxd"]="application/octet-stream"
mime_data[".ra"]="audio/x-pn-realaudio"
mime_data[".ram"]="audio/x-pn-realaudio"
mime_data[".rar"]="application/octet-stream"
mime_data[".ras"]="image/x-cmu-raster"
mime_data[".rf"]="image/vnd.rn-realflash"
mime_data[".rgb"]="image/x-rgb"
mime_data[".rm"]="application/vnd.rn-realmedia"
mime_data[".rmi"]="audio/mid"
mime_data[".roff"]="application/x-troff"
mime_data[".rpm"]="audio/x-pn-realaudio-plugin"
mime_data[".rtf"]="application/rtf"
mime_data[".rtx"]="text/richtext"
mime_data[".scd"]="application/x-msschedule"
mime_data[".sct"]="text/scriptlet"
mime_data[".sea"]="application/octet-stream"
mime_data[".setpay"]="application/set-payment-initiation"
mime_data[".setreg"]="application/set-registration-initiation"
mime_data[".sgml"]="text/sgml"
mime_data[".sh"]="application/x-sh"
mime_data[".shar"]="application/x-shar"
mime_data[".sit"]="application/x-stuffit"
mime_data[".sldm"]="application/vnd.ms-powerpoint.slide.macroEnabled.12"
mime_data[".sldx"]="application/vnd.openxmlformats-officedocument.presentationml.slide"
mime_data[".smd"]="audio/x-smd"
mime_data[".smi"]="application/octet-stream"
mime_data[".smx"]="audio/x-smd"
mime_data[".smz"]="audio/x-smd"
mime_data[".snd"]="audio/basic"
mime_data[".snp"]="application/octet-stream"
mime_data[".spc"]="application/x-pkcs7-certificates"
mime_data[".spl"]="application/futuresplash"
mime_data[".spx"]="audio/ogg"
mime_data[".src"]="application/x-wais-source"
mime_data[".ssm"]="application/streamingmedia"
mime_data[".sst"]="application/vnd.ms-pki.certstore"
mime_data[".stl"]="application/vnd.ms-pki.stl"
mime_data[".sv4cpio"]="application/x-sv4cpio"
mime_data[".sv4crc"]="application/x-sv4crc"
mime_data[".svg"]="image/svg+xml"
mime_data[".svgz"]="image/svg+xml"
mime_data[".swf"]="application/x-shockwave-flash"
mime_data[".t"]="application/x-troff"
mime_data[".tar"]="application/x-tar"
mime_data[".tcl"]="application/x-tcl"
mime_data[".tex"]="application/x-tex"
mime_data[".texi"]="application/x-texinfo"
mime_data[".texinfo"]="application/x-texinfo"
mime_data[".tgz"]="application/x-compressed"
mime_data[".thmx"]="application/vnd.ms-officetheme"
mime_data[".thn"]="application/octet-stream"
mime_data[".tif"]="image/tiff"
mime_data[".tiff"]="image/tiff"
mime_data[".toc"]="application/octet-stream"
mime_data[".tr"]="application/x-troff"
mime_data[".trm"]="application/x-msterminal"
mime_data[".ts"]="video/vnd.dlna.mpeg-tts"
mime_data[".tsv"]="text/tab-separated-values"
mime_data[".ttf"]="application/octet-stream"
mime_data[".tts"]="video/vnd.dlna.mpeg-tts"
mime_data[".txt"]="text/plain"
mime_data[".u32"]="application/octet-stream"
mime_data[".uls"]="text/iuls"
mime_data[".ustar"]="application/x-ustar"
mime_data[".vbs"]="text/vbscript"
mime_data[".vcf"]="text/x-vcard"
mime_data[".vcs"]="text/plain"
mime_data[".vdx"]="application/vnd.ms-visio.viewer"
mime_data[".vml"]="text/xml"
mime_data[".vsd"]="application/vnd.visio"
mime_data[".vss"]="application/vnd.visio"
mime_data[".vst"]="application/vnd.visio"
mime_data[".vsto"]="application/x-ms-vsto"
mime_data[".vsw"]="application/vnd.visio"
mime_data[".vsx"]="application/vnd.visio"
mime_data[".vtx"]="application/vnd.visio"
mime_data[".wav"]="audio/wav"
mime_data[".wax"]="audio/x-ms-wax"
mime_data[".wbmp"]="image/vnd.wap.wbmp"
mime_data[".wcm"]="application/vnd.ms-works"
mime_data[".wdb"]="application/vnd.ms-works"
mime_data[".webm"]="video/webm"
mime_data[".wks"]="application/vnd.ms-works"
mime_data[".wm"]="video/x-ms-wm"
mime_data[".wma"]="audio/x-ms-wma"
mime_data[".wmd"]="application/x-ms-wmd"
mime_data[".wmf"]="application/x-msmetafile"
mime_data[".wml"]="text/vnd.wap.wml"
mime_data[".wmlc"]="application/vnd.wap.wmlc"
mime_data[".wmls"]="text/vnd.wap.wmlscript"
mime_data[".wmlsc"]="application/vnd.wap.wmlscriptc"
mime_data[".wmp"]="video/x-ms-wmp"
mime_data[".wmv"]="video/x-ms-wmv"
mime_data[".wmx"]="video/x-ms-wmx"
mime_data[".wmz"]="application/x-ms-wmz"
mime_data[".woff"]="font/x-woff"
mime_data[".wps"]="application/vnd.ms-works"
mime_data[".wri"]="application/x-mswrite"
mime_data[".wrl"]="x-world/x-vrml"
mime_data[".wrz"]="x-world/x-vrml"
mime_data[".wsdl"]="text/xml"
mime_data[".wtv"]="video/x-ms-wtv"
mime_data[".wvx"]="video/x-ms-wvx"
mime_data[".x"]="application/directx"
mime_data[".xaf"]="x-world/x-vrml"
mime_data[".xaml"]="application/xaml+xml"
mime_data[".xap"]="application/x-silverlight-app"
mime_data[".xbap"]="application/x-ms-xbap"
mime_data[".xbm"]="image/x-xbitmap"
mime_data[".xdr"]="text/plain"
mime_data[".xht"]="application/xhtml+xml"
mime_data[".xhtml"]="application/xhtml+xml"
mime_data[".xla"]="application/vnd.ms-excel"
mime_data[".xlam"]="application/vnd.ms-excel.addin.macroEnabled.12"
mime_data[".xlc"]="application/vnd.ms-excel"
mime_data[".xlm"]="application/vnd.ms-excel"
mime_data[".xls"]="application/vnd.ms-excel"
mime_data[".xlsb"]="application/vnd.ms-excel.sheet.binary.macroEnabled.12"
mime_data[".xlsm"]="application/vnd.ms-excel.sheet.macroEnabled.12"
mime_data[".xlsx"]="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
mime_data[".xlt"]="application/vnd.ms-excel"
mime_data[".xltm"]="application/vnd.ms-excel.template.macroEnabled.12"
mime_data[".xltx"]="application/vnd.openxmlformats-officedocument.spreadsheetml.template"
mime_data[".xlw"]="application/vnd.ms-excel"
mime_data[".xml"]="text/xml"
mime_data[".xof"]="x-world/x-vrml"
mime_data[".xpm"]="image/x-xpixmap"
mime_data[".xps"]="application/vnd.ms-xpsdocument"
mime_data[".xsd"]="text/xml"
mime_data[".xsf"]="text/xml"
mime_data[".xsl"]="text/xml"
mime_data[".xslt"]="text/xml"
mime_data[".xsn"]="application/octet-stream"
mime_data[".xtp"]="application/octet-stream"
mime_data[".xwd"]="image/x-xwindowdump"
mime_data[".z"]="application/x-compress"
mime_data[".zip"]="application/x-zip-compressed"
#------------------audio-------------------------
mime_data[".weba"]="audio/webm"

#----Image ---------------------------------
mime_data[".webp"]="image/webp"
mime_data[".avif"]="image/avif"

mimetypes.types_map = {**mime_data,**mimetypes.types_map}
__old__=mimetypes.guess_type
def __new__fn__(url, strict=True):
    import os
    items= url.split('.')
    item="."+items[items.__len__()-1]
    a,b = mime_data.get(item),None
    if a is None:
        a,b= __old__(url,strict)
    if a is None:
        x= os.path.splitext(url)[1]
        a = mime_data.get(x)
        if a is None:
            a = r'application/octet-stream'
    return a,b

mimetypes.guess_type=__new__fn__
