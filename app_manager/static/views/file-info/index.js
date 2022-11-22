
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import {parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var fileInfoView = await View(import.meta, class FileInfoView extends BaseScope {
      async init() {


      }
      async loadDetailInfo(appName, uploadId){
        this.appName=appName;
        this.uploadId=uploadId;
        this.data = await api.post(`${appName}/files/info`, {
            UploadId: uploadId
        })

        this.$applyAsync();
      }
      async doCopy(){
      //{app_name}/files/clone
        this.ret= await api.post(`${this.appName}/files/clone`, {
            UploadId:this.uploadId
        });
      }


});
export default fileInfoView;