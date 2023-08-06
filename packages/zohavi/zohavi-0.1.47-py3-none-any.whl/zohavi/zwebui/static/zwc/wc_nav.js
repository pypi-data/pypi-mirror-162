
    import WCMaster from  '/webui/static/zwc/wc_master.js' ;

    import {Def_Menu, 
                Header_Menu,
                Sidebar_Menu} from  '/webui/static/zwc/wc_nav__inc__menu.js' ;

    import {Def_Render_Menu, 
                Render_Menu_Header,
                Render_Menu_Sidebar_Full, 
                Render_Menu_Sidebar_Mini} from  '/webui/static/zwc/wc_nav__inc__render_menu.js' ;


    import {Def_Render_Content_Area, 
                Render_Content_Area_Header, 
                Render_Content_Area_Sidebar_Ontop, 
                Render_Content_Area_Sidebar_Push} from  '/webui/static/zwc/wc_nav__inc__render_content_area.js' ;

    import {Def_MenuAction, 
                Sidebar_MenuAction, 
                Sidebar_MenuAction_Slide_On_Top, 
                Sidebar_MenuAction_AlwaysOff,
                Sidebar_MenuAction_AlwaysOn,
                Header_MenuAction} from  '/webui/static/zwc/wc_nav__inc__menu_action.js' ;


    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export default class WCNav extends WCMaster { 
        define_template_globals(){
            return `:host{
                        --sbar_full_width: [placeholder::sbar_full_width_px]px;
                        --sbar_min_width:  [placeholder::sbar_min_width_px]px;
                        --header_height:   [placeholder::header_height_px]px;
                        --main_view_margin:10px;  
                        --transition_speed: all 0.1s; 
                        --wc_background_color: white;
                    
                        --section_menu_text_color: var(--light_text_color_cat1_subdued);
                        --sbar_color: [placeholder::sbar_color];
                        --sbar_color_logo: #161c25;
                        --sub_menu_text_color: var(--light_text_color_cat1);
                        --sbar_menu_selected : var(--light_text_color_cat1_background);
                    }`
        }

        define_template_header_css(){
            if( ! this._inp.header_on ){ return '';}
            return `
            /************  HEADER  ***************/
                    #header { 
                        display: flex;
                        position: fixed;
                        top: 0;
                        width: 100%; 
                        z-index:10;
                        overflow:hidden;
                    }
                   
                    #si_mview_topnav{
                        background-color: var(--wc_background_color);
                        margin-left: 10px;
                        transition:  var(--transition_speed);
                    }
                    
                    .sc_push_navbar_with_full_sbar_visible {
                        margin-left: var(--sbar_full_width) !important; 
                        padding-left: var(--main_view_margin) ;
                    }

                    .sc_push_navbar_with_min_sbar_visible {
                        margin-left: var(--sbar_min_width) !important; 
                        padding-left: var(--main_view_margin) ;
                    }
                    
                    @media screen and (min-width: [placeholder::mobile_width_breakpoint_px]px) {
                        #header {
                            margin-left: (--sbar_full_width);
                            padding-left: var(--main_view_margin) ;
                        }
                    }`
        }

        define_template_header_html(){
            if( ! this._inp.header_on ){ return '';}
            return `
                <!-- ## HEADER ## -->
                <div id="header">
                    <nav id="si_mview_topnav" class="navbar is-fixed-top has-shadow " role="navigation"
                        aria-label="main navigation">
                        <div class="navbar-brand">
                            <a id="si_header_sbar_menu_icon" class="navbar-item sc_sbar_menuicon " href="#">
                                <i class="fas fa-bars"></i>
                            </a>
                            <a class="navbar-item" id="si_logo_header_link">
                                <img id="si_logo_header_img" src="" width="112" height="28">
                            </a>
                
                            <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false"
                                data-target="si_navbar_menu_list">
                                <span aria-hidden="true"></span>
                                <span aria-hidden="true"></span>
                                <span aria-hidden="true"></span>
                            </a>
                        </div>
                
                        <div id="si_navbar_menu_list" class="navbar-menu" style="z-index: 100;">
                            <div id='si_navbar_menu_start' class="navbar-start">
                                <!-- insert menu items here -->
                            </div>
                
                            <div class="navbar-end">
                                <div class="navbar-item">
                                    <div class="buttons">
                                        <a class="button is-primary">
                                            <strong>Sign up</strong>
                                        </a>
                                        <a class="button is-light">
                                            Log in
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </nav>
                </div>
            `
        }

        define_template_sidebar_css(){
            return `/************  SIDEBAR FRAME ***************/ 
                    .sc_sbar {
                        height: 100%;
                        width: 0px;
                        transition:  var(--transition_speed);
                        padding-top: 0px;
                        overflow: hidden;

                        xxtop: 0px;
                        xxz-index: 1;
                        xxz-index: 1;
                        xxleft: 0px; 
                        xxoverflow-y:none; //THIS -> ADD
                        xxoverflow: hidden; 
                        xxheight: 100%;
                        xxposition: relative;
                        xxdisplay:block;
                        xxdisplay: flex;
                        xxflex-direction: column;
                        xxdisplay:flex;
                        xxflex-direction:column;
                        xxoxxverflow-y: none;

                        
                    }
                    
                    .sc_sbar_menu_item {
                        padding: 8px 8px 8px 32px;
                        text-decoration: none;
                        font-size: 25px;
                        color: var(--sub_menu_text_color);
                        display: block;
                    } 

                    .sc_sbar_clicked_visible {
                        width: var(--sbar_full_width);
                    }

                    xxxx_@media screen and (min-width: [placeholder::mobile_width_breakpoint_px]px) {
                        #si_header_sbar_menu_icon{
                            display: none
                        }
                    }

                    .sc_sbar_menu_header{
                        background-color: var(--sbar_color_logo); 
                        height: 50px;
                        align-items: center;
                        color: var(--sub_menu_text_color); 
                        white-space:nowrap;
                        
                    }

                    #si_header_sbar_menu_icon{
                        display:flex;
                        align-items: center;
                    }
                    .sc_sbar_menu_area { 
                        height: 100%;
                        background-color: var(--sbar_color);
                        
                        
                    }

                    xxx#si_sbar_menu{
                        position: fixed;
                        xxtop: 55px;
                    }
                
                    .sc_sbar_menu_is_active{
                        background-color: var(--sbar_menu_selected);
                    }
                    
                    .sc_sbar_submenu_is_active_bullet{ 
                        font-weight:bolder;   
                        display: list-item;           
                        list-style-type: disc;        
                        list-style-position: outside;   
                        color: #d700f3; 
                        float: left;
                    }
                    
                    .sc_sbar_submenu_is_active_text{ 
                        font-weight:bolder;  
                        color: #fff; 
                    }

                    .sc_menu_item_arrow {
                        display: none;
                    }
                    
                    .sc_sidebar_menu_has_submenu>.sc_menu_item_arrow {
                        display: inline;
                    }

                    .menu-label {
                        font-size: 13px; 
                        color: var(--section_menu_text_color); 
                        margin-bottom: 0px !important;
                    }
                    
                    .menu-list>li>a {
                        color: var(--sub_menu_text_color); 
                        font-size: 15px;
                        white-space:nowrap;
                    }
                    
                    .menu-list>li>ul>li>a {
                        color: var(--sub_menu_text_color);
                        font-size: 13px;
                    }`
        }

        define_template_sidebar_html(){
            if( ! this._inp.sidebar_on ){ return '';}
            return `
                <!-- ## SIDEBAR ##   --> 
                <div id="si_sbar" class="sc_sbar mt-0"  >
                            <div class="sc_sbar_menu_header " >  
                                <!-- <a href="# " class="sc_sbar_close_button is-pulled-right">x</a> -->
                                <span>
                                    <img src="" id="si_sbar_log" width="112" height="28" alt="" class="p-3 ">
                                </span>
  
                            </div> 
                            <div class="sc_sbar_menu_area  "  >
                                
                                <aside class="menu pt-3 pl-3" id="si_sbar_menu">

                                    <!--  REFERENCE
                                        <p class="menu-label">General</p>
                                        <ul class="menu-list ">
                                            <li class=""><a href="#" class="sc_sbar_menu_item"><i class="fas fa-home "></i> Dashboard</a></li>
                                            <li><a href="#" class="sc_sbar_menu_item"><i class="fas fa-home "></i> Customers</a></li>
                                        </ul>
                                        <p class="menu-label">Administration</p>
                                        <ul class="menu-list">
                                            <li>
                                                <a href="#" class="sc_sbar_menu_item">
                                                    <span class="sc_sbar_menu_item_text">Team Settings</span> 
                                                    <span class="sc_menu_item_arrow"><i class="fas fa-chevron-right"></i></span>
                                                </a></li>
                                            <li>
                                                <a  href="#" class="sc_sbar_menu_item sc_sidebar_menu_has_submenu sc_sbar_menu_is_active"><i class="fas fa-home "></i> Manage Your Team <span
                                                        class="sc_menu_item_arrow"><i class="fas fa-chevron-right sck_sbar_submenu_icon"></i></span></a>
                                                <ul class="sc_sbar_submenu is-hidden"  >
                                                    <li><a  href="#" class="sc_sbar_menu_item "><span class="sck_submenu_item_bullet sc_sbar_submenu_is_active_bullet"></span><span class="sck_submenu_item_text sc_sbar_submenu_is_active_text">Members</span></a></li>
                                                    <li><a  href="#" class="sc_sbar_menu_item"><span class="sck_submenu_item_bullet  "></span><span class="sck_submenu_item_text  ">Plug</span></a></li>
                                                </ul>
                                            </li>
                                            <li><a href="#" class="sc_sbar_menu_item">Invitations</a></li>
                                        </ul> 
                                    -->
                                </aside>
                            </div>
                </div>
            `
        }
        
        define_template(){
            return super.define_template() + `
                <style>
                    ${ this.define_template_globals() }

                    ${ this.define_template_header_css() }
                    
                    ${ this.define_template_sidebar_css() }
                </style>

                ${ this.define_template_header_html() }
                ${ this.define_template_sidebar_html() }
                
                
            `};

        //***********************************************************************************************************
        //[Def_Menu]
        //    - Header_Menu
        //    - Sidebar_Menu
        //
        //[Renderer]
        //    - Render_Header 
        //    - Render_Sidebar_Full
        //        - Render_Sidebar_Mini 
        //
        //[Def_MenuAction]
        //    - Sidebar_MenuAction 
        //        - Sidebar_MenuAction_Slide_On_Top
        //        - Sidebar_MenuAction_AlwaysOff 
        //        - Sidebar_MenuAction_AlwaysOn
        //     - Header_MenuAction
        //
        //[Render_Content_Area]
        //    - Render_Content_Area_Sidebar_Push 
        //    - Render_Content_Area_Sidebar_Ontop
        //    - Render_Content_Area_Header
        //example: 
        constructor() {  

            super( {"logo_header_img_src":"", "logo_header_link":"", "logo_sidebar_img_src":"", "logo_sidebar_link":"", 
                    "header_menu_start":"", "header_height_px":55, "sbar_full_width_px":250, "mobile_width_breakpoint_px":768, 
                    "sbar_menu_list":"" ,  "header_on=bool":false, "sidebar_on=bool":false, "sidebar_minimised":true, "sbar_min_width_px":40,
                    "sbar_renderer":"full", "sbar_visibility":"always-on", "sbar_content_area":"push", 
                    "sbar_color": getComputedStyle(document.body).getPropertyValue('--background_cat1_color') ,
                    "header_renderer":"def", "header_visibility":"always-on", "header_content_area":"push", "header_color": 'green',
                    "sbar_active_menu_item":"", "header_active_menu_item":"", "sbar_disable_menu_list=array":"", "header_disable_menu_list":""
                     }, 
                    ["main_div_selector"]); 
            // debugger;
            var sbar_menu_options = { 
                                    "renderer":{    "mini": new Render_Menu_Sidebar_Mini(),
                                                "full":  new Render_Menu_Sidebar_Full() },
                                    "action":{  "always-on":  new Sidebar_MenuAction_AlwaysOn(),
                                                "always-off":  new Sidebar_MenuAction_AlwaysOff() },
                                    "content_area": {   "push": new Render_Content_Area_Sidebar_Push(),
                                                        "on-top": new Render_Content_Area_Sidebar_Ontop() }

                                    }

            var header_menu_options = { 
                                        "renderer":{ "def": new Render_Menu_Header() },
                                        "action":{ "always-on": new Header_MenuAction() },
                                        "content_area":{ "push": new Render_Content_Area_Header() } 
                                  }


            // debugger;

            this.header = null
            this.sidebar = null

            if( this._inp.sidebar_on ){
                this.log( `Creating sidebar for ${sbar_menu_options[ 'renderer'][this._inp.sbar_renderer ].constructor.name} , ${sbar_menu_options['action'][ this._inp.sbar_visibility ].constructor.name}, ${sbar_menu_options['content_area'][ this._inp.sbar_content_area].constructor.name } `)
           
                this.sidebar = new Sidebar_Menu(    this.shadowRoot, this._inp, 
                                                    sbar_menu_options[ 'renderer'][ this._inp.sbar_renderer ], 
                                                    sbar_menu_options['action'][ this._inp.sbar_visibility ], 
                                                    sbar_menu_options['content_area'][ this._inp.sbar_content_area ]
                                                    );
            }

            if( this._inp.header_on ){
                this.log( `Creating sidebar for ${header_menu_options[ 'renderer'][ this._inp.header_renderer ].constructor.name} , ${header_menu_options['action'][ this._inp.header_visibility ].constructor.name}, ${header_menu_options['content_area'][ this._inp.header_content_area].constructor.name } `)
                
                this.header = new Header_Menu(    this.shadowRoot, this._inp, 
                                                    header_menu_options[ 'renderer'][ this._inp.header_renderer ], 
                                                    header_menu_options['action'][ this._inp.header_visibility ], 
                                                    header_menu_options['content_area'][ this._inp.header_content_area ]
                                                    );

                // this.header = new Header_Menu(      this.shadowRoot, this._inp, 
                //                                     new Header_MenuAction(), 
                //                                     new Render_Menu_Header()  ,
                //                                     new Render_Content_Area_Header() 
                //                                     );
            }
             

        } 
        //************************************************************************************
        //Setup the defaults and events
        connectedCallback(){    
            
            if( this._inp.header_on){   this.header.connectedCallback(); }
            if( this._inp.sidebar_on ){ this.sidebar.connectedCallback() }

            if( this._inp.header_on){   this.header.register_linked_menu( this.sidebar );  }
            if( this._inp.sidebar_on ){ this.sidebar.register_linked_menu( this.header ) ; }

                
                
            

            
            
        }
 
 
    }

    window.customElements.define('wc-nav', WCNav);

