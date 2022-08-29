"""
var UserProfileId = Guid.NewGuid().ToString();
            var UserProfileFullPath = Path.Combine(ProfileDir, UserProfileId);
            Directory.CreateDirectory(UserProfileFullPath);


            var uno =string.Format("uno:socket,host={0},port={1};urp;Negotiate=0,ForceSynchronous=0;",UnonHost,UnoPort.ToString("0000"));
            if (!File.Exists(sofficePath))
                throw new Exception("'" + sofficePath + "' was not found");
            if (!File.Exists(officeFile))
                throw new Exception("'" + officeFile + "' was not found");
            var direcrory = new FileInfo(officeFile).Directory.FullName;

            return await Task.Run<string>(() =>
            {

                var thumbnai = officeFile.Split("\\").ToList();
                var namedist = thumbnai[thumbnai.Count() - 1];
                ProcessStartInfo info;


                try
                {
                    using (var th = new Process())
                    {

                        info = th.StartInfo;

                        info.FileName = sofficePath;
                        var arg = "--outdir {0} {1}";
                        var argList = new List<string>();
                        argList.Add("--headless");
                        argList.Add("--convert-to png");
                        argList.Add(string.Format(@"--accept={0}", uno));



                        argList.Add(@"-env:UserInstallation=file:///"+UserProfileFullPath.Replace(@"\", @"/"));
                        arg = string.Format(arg, tmpDir, officeFile, uno);

                        argList.Add(arg);
                        info.Arguments = string.Join(" ", argList);

                        info.UseShellExecute = true;
                        info.CreateNoWindow = false;
                        if (!string.IsNullOrEmpty(Username))
                        {
                            info.UserName = Username;
                            info.PasswordInClearText = Password;
                            info.Domain = domain;
                        }

                        th.EnableRaisingEvents = true;
                        th.OutputDataReceived += (S,E)=> {
                            Console.WriteLine($"----------------------------------------------");
                            Console.WriteLine($"Process file '{officeFile}' recive data at :" + DateTime.Now.ToString("dd-MM-yyyy hh:mm;ss"));
                            Console.WriteLine($"----------------------------------------------");
                        };
                        th.ErrorDataReceived += (S, E) =>
                        {
                            Console.WriteLine($"----------------------------------------------");
                            Console.WriteLine($"'{sofficePath}' is error :");
                            Console.WriteLine(E.Data);
                            Console.WriteLine($"----------------------------------------------");
                        };
                        th.Exited += (S, E) =>
                        {
                            Console.WriteLine($"----------------------------------------------");
                            Console.WriteLine($"'{sofficePath}'");
                            Console.WriteLine("Exist at :" + DateTime.Now.ToString("dd - MM - yyyy hh: mm:ss"));
                            Console.WriteLine($"----------------------------------------------");

                        };

                        th.Start();
                        th.WaitForExit();
                        return Path.Combine(tmpDir,  Path.GetFileNameWithoutExtension(new FileInfo(officeFile).Name)+".png");


                    }
                }
                catch (Exception)
                {

                    throw;
                }




            });


"""
import ReCompact_Kafka.consumer
import re_process.config

import logging


def handler_use_aspose(consumer: ReCompact_Kafka.consumer.Consumer_obj, msg, logger: logging.Logger):
    """
    Sử dụng aspose cần phải có bản quyền chạy nhanh hơn
    :param consumer:
    :param msg:
    :param logger:
    :return:
    """
    import re_process.config
    import os
    import uuid
    import aspose.words as aw

    data = consumer.get_json(msg)

    file_path = data["FilePath"]  # Đường dẫn đến file vật lý
    upload_info = data["UploadInfo"]  # Thông tin lúc upload
    if upload_info["FileExt"] == "pdf":
        consumer.commit(msg)
        return
    app_name = data["AppName"]  # Tên App
    ThumbWidth, ThumbHeight = upload_info.get('ThumbWidth', 700), upload_info.get('ThumbHeight', 700)
    out_put_dir = os.path.join(re_process.config.temp_thumbs, app_name)
    if not os.path.isdir(out_put_dir):
        os.mkdir(out_put_dir)
    out_put_file = os.path.join(out_put_dir, f"{upload_info['_id']}.png")
    # load document
    doc = aw.Document(file_path)

    # set output image format
    options = aw.saving.ImageSaveOptions(aw.SaveFormat.PNG)

    # loop through pages and convert them to PNG images
    for pageNumber in range(doc.page_count):
        options.page_set = aw.saving.PageSet(pageNumber)
        doc.save(out_put_file, options)
        break

    uno = "uno:socket,host=localhost,port=10;urp;Negotiate=0,ForceSynchronous=0;"


def handler_use_libre_office(consumer: ReCompact_Kafka.consumer.Consumer_obj, msg, logger: logging.Logger):
    """
    Sử dụng Libre Office
    Chú ý: Không cần bắt lỗi trong trường hợp không cần thiết
           Nếu lỗi xãy ra hệ thống sẽ tự động ghi nhận
    :param consumer:
    :param msg:
    :param logger:
    :return:
    """
    import subprocess
    import uuid
    import re_process.config
    import os
    import time
    data = consumer.get_json(msg)
    file_path = data["FilePath"]  # Đường dẫn đến file vật lý
    upload_info = data["UploadInfo"]
    file_ext = upload_info["FileExt"]
    file_name = upload_info["FileName"]
    if file_ext=="pdf":
        """
        file pdf bỏ qua
        """
        consumer.commit(msg)
        return

    app_name = data["AppName"]
    upload_info = data["UploadInfo"]  # Thông tin lúc upload
    upload_id = upload_info["_id"]
    image_file_path = os.path.join(re_process.config.temp_thumbs, app_name, f"{upload_id}.png")
    out_put_dir = os.path.join(re_process.config.temp_thumbs, app_name)
    if not os.path.isfile(image_file_path):
        user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
        # kg xử lý song song được
        full_user_profile_path = os.path.join(re_process.config.temp_libre_office_user_profile_dir, user_profile_id)
        uno = f"uno:socket,host=localhost,port=10;urp;Negotiate=0,ForceSynchronous=0;"

        if not os.path.isdir(out_put_dir):
            os.makedirs(out_put_dir)
        arg = f"--outdir { out_put_dir} {file_path}"
        arg_list = [
            f'"{re_process.config.libre_office_path}"',

            "--headless",
            "--convert-to png",
            f"--accept={uno}",
            f"-env:UserInstallation=file:///{full_user_profile_path.replace(os.sep, '/')}",
            arg
        ]
        full_comand_line = " ".join(arg_list)
        logger.info(full_comand_line)
        p = subprocess.Popen(full_comand_line  , shell=True)
        p.communicate() # Đợi
        import shutil
        shutil.rmtree(full_user_profile_path)
        logger.info(f"Process file {file_path} to image is finish")
    thumb_file_path = os.path.join(out_put_dir, f"{upload_id}_thumb.png")
    if not os.path.isfile(thumb_file_path):
        ThumbWidth, ThumbHeight = upload_info.get('ThumbWidth', 700), upload_info.get('ThumbHeight', 700)
        """
        Dòng tren lay kích thươc cua thumb
        Anh thum thuc su se co lai vua van voi khung
    
        """

        from PIL import Image


        img = Image.open(image_file_path)
        w, h = img.size
        rate = ThumbWidth / w  # Mặc dịnh bóp theo bề rộng
        if h > w:  # Nhưng vì bề dọc lớn hơn bề rộng
            rate = ThumbHeight / h  # nên bóp theo bề dọc
        nh = int((float(h) * float(rate)))
        nw = int((float(w) * float(rate)))
        img = img.resize((nw, nh), Image.ANTIALIAS)
        img.save(thumb_file_path)
        logger.info(f"Create thumb {file_path} is success at {thumb_file_path}")
    """
    Bước cuối cùng cập nhật ảnh thumb
    """

    import ReCompact.dbm.DbObjects # Dùng để thao tác dữ liệu ter6n mongodb
    import re_process.mongo_db # Dùng để lấy database thao tác
    import ReCompact.db_context # Dùng để tạo file trên mongodb
    import api_models.Model_Files # Sử dụng model
    import ReCompact.dbm
    db = re_process.mongo_db.get_db(app_name)
    """
    Đưa file thumb vào fs.file của  database
    """
    fs = ReCompact.db_context.create_mongodb_fs_from_file(
        db=db,
        full_path_to_file= thumb_file_path
    )
    logger.info(f"save {thumb_file_path} is success at ")
    """
    Đã đưa file vào xong
    """

    ret =ReCompact.dbm.DbObjects.update(
        db,
        data_item_type= api_models.Model_Files.DocUploadRegister,
        filter= ReCompact.dbm.FILTER._id == upload_id,
        updator= ReCompact.dbm.SET (
            ReCompact.dbm.FIELDS.ThumbFileId==fs._id,
            ReCompact.dbm.FIELDS.HasThumb==True
        )
    )
    logger.info(f"update thumb id of {upload_id} with value  {thumb_file_path}")
    print(f"update thumb id of {file_name} with value  {thumb_file_path}")
    consumer.commit(msg)



