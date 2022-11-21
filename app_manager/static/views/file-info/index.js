
import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import {parseUrlParams, dialogConfirm, redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var fileInfoView = await View(import.meta, class FileInfoView extends BaseScope {
      onInit() {
        var queryData = parseUrlParams();
        this.uploadId  = queryData["id"]
        this.appName = queryData["app"]
        this.loadDetailInfo()

      }
      async loadDetailInfo(){
        this.data = await api.post(`${this.appName}/files/info`, {
            UploadId: this.uploadId
        })

        this.$applyAsync();
      }


});
export default fileInfoView;