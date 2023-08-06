    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //Base class on how to handle rendering the content area
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Def_Render_Content_Area{
        register_menu_obj( menu_obj){
            this.menu_obj = menu_obj
            this.init_content_area()
        } 

        init_content_area(){
            this._content_area = document.querySelector( this.menu_obj.wc_inp_data.main_div_selector );

            if( ! this._content_area){
                throw `**The associated element from attribute [main_div_selector=${this.menu_obj.wc_inp_data.main_div_selector }] could not be found `
            }
        } 

        menu_show_render_content_area(){ }
        menu_hide_render_content_area(){ }
        is_debug(){ return false; }
        log(message){ if(this.is_debug()){ console.log(message)} }
    }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
     export  class Render_Content_Area_Header extends Def_Render_Content_Area{
        menu_show_render_content_area(){ }
        init_content_area(){
            super.init_content_area();
            this._content_area.style.marginTop = this.menu_obj.wc_inp_data.header_height_px + "px";
        }
    }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
     export  class Render_Content_Area_Sidebar_Ontop extends Def_Render_Content_Area{ 
        menu_show_render_content_area(){
            this.menu_obj.notify_observer_linked_menu_opened()
            // var classname = this.menu_obj.menu_renderer.get_content_area_visible_classname();
            // this.menu_obj.wc_shadowRoot.getElementById('si_mview_topnav').classList.add( classname );
        }

        menu_hide_render_content_area(){  
            this.menu_obj.notify_observer_linked_menu_closed()
            // var classname = this.menu_obj.menu_renderer.get_content_area_visible_classname(); 
            // this.menu_obj.wc_shadowRoot.getElementById('si_mview_topnav').classList.remove( classname );

        }
     }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //Base class where the content area is pushed to the side when sidebar menu comes out
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
     export  class Render_Content_Area_Sidebar_Push extends Def_Render_Content_Area{
        menu_show_render_content_area(){
            this._content_area.style.marginLeft = this.menu_obj.menu_renderer.get_ca_left_expanded() + "px";

            this.menu_obj.notify_observer_linked_menu_opened()
            // var classname = this.menu_obj.menu_renderer.get_content_area_visible_classname();
            // this.menu_obj.wc_shadowRoot.getElementById('si_mview_topnav').classList.add( classname );

            // this.log( JSON.stringify( this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList ))
        }

        menu_hide_render_content_area(){ 
            this._content_area.style.marginLeft = this.menu_obj.menu_renderer.get_ca_left_reduced() + "px";

            this.menu_obj.notify_observer_linked_menu_closed()

            // var classname = this.menu_obj.menu_renderer.get_content_area_visible_classname(); 
            // this.menu_obj.wc_shadowRoot.getElementById('si_mview_topnav').classList.remove( classname );

        }
    }