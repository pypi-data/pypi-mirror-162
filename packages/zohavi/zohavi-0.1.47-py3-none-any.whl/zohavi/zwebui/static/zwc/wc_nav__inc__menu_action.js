    import C_UTIL from '/webui/static/zjs/common_utils.js'; //

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //Abstract class for how the menu the to show
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Def_MenuAction{
        register_menu_obj( menu_obj ){ this.menu_obj = menu_obj; } 
        observer_menu_action_linked_menu_opened(){  console.log('opened menu action ' + this.constructor.name )}
        observer_menu_action_linked_menu_closed(){  console.log('clsoed menu action ' + this.constructor.name )}
        init_view(){  }
        menu_action_show(){ throw 'abstract - need to define'}
        menu_action_hide(){ throw 'abstract - need to define'}

        is_expandable(){ return false;}

        is_debug(){ return false; }
        log(message){ C_UTIL.log( message, this.is_debug(), 3) }

    }
    
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Sidebar_MenuAction extends Def_MenuAction{ 
        //**********************************************************************************************
        init_view(){ 
            if( window.innerWidth > this.menu_obj.wc_inp_data.mobile_width_breakpoint_px ){
                this.menu_obj.show();
                this.menu_obj.wc_shadowRoot.querySelector('#si_sbar_menu').style.position = 'fixed'
            }else{
                this.menu_obj.hide();
            }
            
            //this.log(`top position on the GPS: ${this.menu_obj.wc_shadowRoot.querySelector('#si_sbar_menu').offsetTop}`)
            // debugger;
        } 

        //**********************************************************************************************
        menu_action_show(){
            // console.log("showing")
            var si_sbar = this.menu_obj.wc_shadowRoot.getElementById('si_sbar');
            si_sbar.style.width = this.menu_obj.menu_renderer.get_menu_width() + "px"; 
            si_sbar.classList.add("sc_sbar_clicked_visible");

            // si_sbar.style.left = this.menu_obj.menu_renderer.get_menu_left()  + "px";

            this.menu_obj.notify_observer_linked_menu_opened()

            this.menu_obj.wc_shadowRoot.querySelector('#si_sbar_menu').style.position = 'fixed'
        }

        //**********************************************************************************************
        menu_action_hide(){
            this.log('hiding')
            var si_sbar = this.menu_obj.wc_shadowRoot.getElementById('si_sbar');
            si_sbar.style.width = "0px";
            si_sbar.classList.remove("sc_sbar_clicked_visible"); 
            this.menu_obj.notify_observer_linked_menu_closed()

            this.menu_obj.wc_shadowRoot.querySelector('#si_sbar_menu').style.position = ''
            // debugger;
        }

        //**********************************************************************************************
        //Match Media query
        evt_window_resized(media_query){ 
            if( media_query.matches ){ 
                this.menu_obj.show(); 
            }else{ 
                this.menu_obj.hide(); 
            } 
        }
    }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Sidebar_MenuAction_AlwaysOn extends Sidebar_MenuAction{
        //**********************************************************************************************
        init_view(){
            super.init_view();
            if( window.innerWidth > this.menu_obj.wc_inp_data.mobile_width_breakpoint_px ){
                this.menu_obj.show();
            }
        }
    }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Sidebar_MenuAction_AlwaysOff extends Sidebar_MenuAction{
        //******************************************************************** 
        init_view(){}
        //**********************************************************************************************
        evt_window_resized(media_query){  
            if( ! media_query.matches ){  this.hide(); }
        }

        is_expandable(){ return true;}
    }
 

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Sidebar_MenuAction_Slide_On_Top extends Sidebar_MenuAction{ }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Header_MenuAction  extends Def_MenuAction{
        //**********************************************************************************************
        init_view(){
            super.init_view();
        }

        observer_menu_action_linked_menu_opened(){
            this.log('header linked menu opened ' + this.constructor.name ) 
            // this.log('header linked menu opened ' + this.constructor.name ) 

            this.log( `render class: ${ this.menu_obj.menu_renderer.get_content_area_visible_classname() }`)
            // debugger;

            this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList.remove('sc_push_navbar_with_min_sbar_visible')
            this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList.remove('sc_push_navbar_with_full_sbar_visible')
            this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList.add( this.menu_obj.menu_renderer.get_content_area_visible_classname() )
            // this.log( JSON.stringify( this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList )) 
        }

        observer_menu_action_linked_menu_closed(){
            this.log('header linked menu closed ' + this.constructor.name )
            // this.log( `render class: ${ this.menu_obj.menu_renderer.get_content_area_visible_classname() }`)
            this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList.remove('sc_push_navbar_with_min_sbar_visible')
            this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList.remove('sc_push_navbar_with_full_sbar_visible')
            // this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList.add( this.menu_obj.menu_renderer.get_content_area_visible_classname() )
            // this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList.remove('sc_push_navbar_with_min_sbar_visible')
            // this.menu_obj.wc_shadowRoot.querySelector('#si_mview_topnav').classList.remove('sc_push_navbar_with_full_sbar_visible') 
        }
    }