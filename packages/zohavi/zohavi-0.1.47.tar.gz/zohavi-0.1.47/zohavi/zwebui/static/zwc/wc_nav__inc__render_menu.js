    import C_UTIL from '/webui/static/zjs/common_utils.js'; //

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    // Base class on how to show the menu items logo, paint the menus
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Def_Render_Menu{
        register_menu_obj( menu_obj ){
            this.menu_obj = menu_obj 
        } 

        init_logo() { throw 'abstract - needs implementation'; }
        init_menus(){  throw 'abstract - needs implementation'; }

        get_menu_width() { throw `abstract - need to implement [${this.constructor.name}` }
        get_menu_left()  { throw `abstract - need to implement [${this.constructor.name}` }
        get_ca_left_expanded() { throw `abstract - need to implement [${this.constructor.name}` }
        get_ca_left_reduced()  { throw `abstract - need to implement [${this.constructor.name}` }
        get_class_width(){ throw `abstract - need to implement [${this.constructor.name}` }
        get_content_area_visible_classname(){ throw `abstract - need to implement [${this.constructor.name}` }

        is_debug(){ return false; }
        log(message){ C_UTIL.log( message, this.is_debug(), 3) }
 
    }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Render_Menu_Sidebar_Full extends Def_Render_Menu{
        //**********************************************************************************************
        // Initialize the logo details
        init_logo() { 

            if( this.menu_obj.wc_inp_data.logo_header_img_src ){
                this.menu_obj.wc_shadowRoot.querySelector('#si_sbar_log').src = this.menu_obj.wc_inp_data.logo_header_img_src ;
            }else{
                this.menu_obj.wc_shadowRoot.querySelector('.sc_sbar_menu_header').classList.add('is-hidden')
            }
            
        }

        //**********************************************************************************************
        init_menus(){ 
            this.render_sidebar( ) 

            // debugger;
            //this.menu_obj.wc_shadowRoot.querySelector('#si_sbar_menu').style.top = this.menu_obj.wc_shadowRoot.querySelector('.sc_sbar').offsetParent.offsetTop + "px"
            
            // this.menu_obj.wc_shadowRoot
            
        }

        //**********************************************************************************************
        //Render all the menu items
        render_sidebar( ){
            var $sbar_menu= this.menu_obj.wc_shadowRoot.querySelector('#si_sbar_menu');
            var menu_config = JSON.parse( this.menu_obj.wc_inp_data.sbar_menu_list );  
            if( typeof menu_config == 'undefined' || menu_config == null ){ 
                debugger;
                throw `Could not parse JSON for element ` ;
                return;
            }

            var menu_items_str = this.sidebar_full_item_renderer(menu_config)
            
            $sbar_menu.innerHTML = menu_items_str;
        }

        //**********************************************************************************************
        //Render each of the menu items
        sidebar_full_item_renderer(menu_config){
            var this_obj = this;
            var menu_items_str = "";
            menu_config.forEach( function(section, index){
                
                if( section["section"] !== undefined ){ menu_items_str += `<p class="menu-label">${section["section"]}</p>`;     }
                
                menu_items_str += `<ul class="menu-list " >`; 

                console.log( `Disable All ${ JSON.stringify(this_obj.menu_obj.wc_inp_data.sbar_disable_menu_list )}`)

                section["menus"].forEach( function( menu, index){
                    console.log( `checking ${menu['id']}`)
                    if( ! this_obj.menu_obj.wc_inp_data.sbar_disable_menu_list.includes( menu['id'] ) ){    //skip if not in the disable list
                        console.log( ` ${menu['id']} ok`)
                        menu_items_str += this_obj._sidebar_full_item_renderer_menu(this_obj, menu )
                    }
                    
                });

                menu_items_str += '</ul>';
            });
            return menu_items_str;
        }

        //**********************************************************************************************
        //Render each of the menu items
        _sidebar_full_item_renderer_menu(this_obj, menu){
            var icon_str = "";
            var menu_active_class = ""; 
            var menu_items_str = "";
             
            "icon" in menu && menu["icon"] ? icon_str = `<i class="${menu["icon"]} sck_sbar_icon"></i>` : icon_str = "";

            menu_active_class = ""; 
            if( menu["active"] == "true" || this_obj.menu_obj.wc_inp_data.sbar_active_menu_item == menu["id"] ){
                menu_active_class = 'sc_sbar_menu_is_active';
            }
            
            if( "sub_menu" in menu){
                menu_items_str += this_obj._sidebar_full_item_renderer_menuitem_with_submenu(this_obj, menu, icon_str, menu_active_class )
            }else{
                menu_items_str += `<li id="${menu["id"]}"><a href="${menu["link"]}" class="sc_sbar_menu_item ${menu_active_class}">` +
                               `${icon_str} <span class="sck_menu_item_text">${menu["title"]}</span> </a>`;
            }
            menu_items_str += '</li>'
            return menu_items_str;
        }

        //**********************************************************************************************
        _sidebar_full_item_renderer_menuitem_with_submenu(this_obj, menu, icon_str, menu_active_class ){
            var menu_items_str = "";
            var menu_sub_item_str = "";
            var sub_menu_active = false;
            menu["sub_menu"].forEach( function( sub_menu, index){

                if( ! this_obj.menu_obj.wc_inp_data.sbar_disable_menu_list.includes( sub_menu['id'] ) ){    //skip if not in the disable list

                    menu_sub_item_str += `<li id="${sub_menu["id"]}"><a  href="${sub_menu["link"]}" class="sc_sbar_menu_item ">`;
                    
                    if( sub_menu["active"] == "true"  || this_obj.menu_obj.wc_inp_data.sbar_active_menu_item == sub_menu["id"]  ){
                        sub_menu_active = true;
                        menu_sub_item_str += `<span class="sck_submenu_item_bullet sc_sbar_submenu_is_active_bullet"></span>` +
                                            `<span class="sck_submenu_item_text sc_sbar_submenu_is_active_text">`;
                    }else{
                        menu_sub_item_str += `<span class="sck_submenu_item_bullet"></span>` +
                                            `<span class="sck_submenu_item_text">`;
                    }                                              
                    menu_sub_item_str += `${sub_menu["title"]}</span></a></li>`;
                }
            });
            
            menu_items_str += `<li><a href="${menu["link"]}" class="sc_sbar_menu_item sck_menu_item_text ${menu_active_class} mr-0 pr-1" style="display: inline-block;">`
            menu_items_str += `          ${icon_str} ${menu["title"]} </a>`;
            menu_items_str += `     <a href="#" class="sc_sidebar_menu_has_submenu ml-0 pl-1" style="display: inline;">`
            menu_items_str += `             <span class="sc_menu_item_arrow">`
            menu_items_str += `                     <i class="fas ${ sub_menu_active ? 'fa-chevron-down':'fa-chevron-right'}  sck_sbar_submenu_icon"></i></span></a>`;
            menu_items_str += `<ul class="sc_sbar_submenu ${ sub_menu_active ?'':'is-hidden'} " >`; //if sub-menu active then dont show as hidden
            menu_items_str += menu_sub_item_str;
            menu_items_str += '</ul>';

            return menu_items_str;
        }

        get_menu_width(){ return this.menu_obj.wc_inp_data.sbar_full_width_px; }
        get_menu_left(){  return 0; }
        // get_ca_left_expanded() { return this.menu_obj.wc_inp_data.sbar_full_width_px;  }
        get_ca_left_expanded() { return 0;  }
        get_ca_left_reduced() { return 0; } 
        // get_content_area_visible_classname(){ return 'sc_push_navbar_with_full_sbar_visible'; }

    }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //Class to show the minimised menu option - this extends from the standard sidebar
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Render_Menu_Sidebar_Mini extends Render_Menu_Sidebar_Full{
        //**********************************************************************************************
        // Initialize the logo details
        init_menus(){  
            this.render_sidebar( this.sidebar_full_item_renderer ) 

            var si_sbar = this.menu_obj.wc_shadowRoot.querySelector('#si_sbar')
            si_sbar.style.width = this.menu_obj.menu_renderer.get_menu_width() + "px"

            //Put the icons for the menu items on the right handside, so that when the menu is minised one can see icons
            this.menu_obj.wc_shadowRoot.querySelectorAll('.sck_sbar_icon').forEach( function(elt){
                elt.classList.add('is-pulled-right')
            });
  
            // console.log(`render_side_bar_mini left ${this.menu_obj.menu_responsive_style.get_menu_left()}`)
            //Set the left side of the menu depending on the responsive style
            si_sbar.style.left = this.menu_obj.menu_renderer.get_menu_left()  + "px";
        }

        get_menu_width(){ return this.menu_obj.wc_inp_data.sbar_full_width_px; }
        get_menu_expanded_left(){  return 0; }
        get_menu_left(){  
            if( this.menu_obj.menu_expanded ){
                this.log( 'expanded - hence return 0');
                return 0;   
            }
            this.log( `not expended: ${this.menu_obj.wc_inp_data.sbar_min_width_px - this.menu_obj.wc_inp_data.sbar_full_width_px}`)
            return (this.menu_obj.wc_inp_data.sbar_min_width_px - this.menu_obj.wc_inp_data.sbar_full_width_px);
        }
        get_ca_left_expanded() { 
            if( this.menu_obj.menu_expanded ){
                return this.menu_obj.wc_inp_data.sbar_full_width_px;     
            }
            return this.menu_obj.wc_inp_data.sbar_min_width_px; 
        }
        get_ca_left_reduced() {  return 0; }
        // get_content_area_visible_classname(){ 
        //     if( this.menu_obj.menu_expanded ){
        //         return 'sc_push_navbar_with_full_sbar_visible'; 
        //     }
        //     return 'sc_push_navbar_with_min_sbar_visible'; 
        // }
    }



    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Render_Menu_Header extends Def_Render_Menu{
        //**********************************************************************************************
        // Initialize the logo details
        init_logo() { 
            this.menu_obj.wc_shadowRoot.querySelector('#si_logo_header_link').href = this.menu_obj.wc_inp_data.logo_header_link 

            if( this.menu_obj.wc_inp_data.logo_header_img_src ){
                this.menu_obj.wc_shadowRoot.querySelector('#si_logo_header_img').src = this.menu_obj.wc_inp_data.logo_header_img_src    
            }else{
                this.menu_obj.wc_shadowRoot.querySelector('#si_logo_header_img').src = 'https://bulma.io/images/bulma-logo.png'
            }
            
        }

        //**********************************************************************************************
        init_menus(){
            var $menu_item = this.menu_obj.wc_shadowRoot.querySelector('#si_navbar_menu_start');
            var menustart_config = JSON.parse( this.menu_obj.wc_inp_data.header_menu_start );

            var menu_items_str = "";
            for (var key of Object.keys(menustart_config)){
                var value = menustart_config[key] ;
                if( typeof value == "object") {
                    menu_items_str += `<div class="navbar-item has-dropdown is-hoverable">`
                    menu_items_str += `<a class="navbar-link">${key}</a>`
                    menu_items_str += `<div class="navbar-dropdown">`
                    for (var subkey of Object.keys( value[0] )){
                        menu_items_str += `<a class="navbar-item" href="${value[0][subkey]}">${subkey}</a>`
                    }
                    menu_items_str += `</div>`
                    menu_items_str += `</div>`

                }else{
                    menu_items_str += `<a class="navbar-item" href="${value}">${key}</a>`
                }
            }
            $menu_item.innerHTML = menu_items_str;
        }

        get_content_area_visible_classname(){ 
            this.log( `expand status = ${this.menu_obj.wc_linked_menu_obj.menu_expanded}`)
            if( this.menu_obj.wc_linked_menu_obj.menu_expanded == true){
                return 'sc_push_navbar_with_full_sbar_visible'; 
            }else if( this.menu_obj.wc_linked_menu_obj.menu_expanded == false){
                return 'sc_push_navbar_with_min_sbar_visible';
            }
            //If 'undefined'
            return 'sc_push_navbar_with_full_sbar_visible';     
        }
    }
