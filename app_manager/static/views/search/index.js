import { BaseScope, View } from "./../../js/ui/BaseScope.js";
//import { ui_rect_picker } from "../../js/ui/ui_rect_picker.js";
//import { ui_pdf_desk } from "../../js/ui/ui_pdf_desk.js";
import api from "../../js/ClientApi/api.js"
import { redirect, urlWatching, getPaths, msgError } from "../../js/ui/core.js"

var searchView = await View(import.meta, class SearchView extends BaseScope {
    listOfApp = [1]
    currentApp = undefined
    listOfFiles = []
    currentAppName = undefined
    async init() {

        this.listOfApp = await api.post(`admin/apps`, {
            Token: window.token
        })
        this.currentApp = this.listOfApp[0];
        this.currentAppName = this.currentApp.Name;
        
        this.$apply();
    }
    async doFullTextSearch() {
       
        this.data = await api.post(`${this.currentAppName}/search`, {
            content: this.searchContent
        });
        this.$applyAsync();
    }
    
    
    
    
    
   
});
export default searchView;