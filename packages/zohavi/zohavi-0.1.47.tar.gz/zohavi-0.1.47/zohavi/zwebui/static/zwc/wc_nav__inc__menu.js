    import C_UTIL from '/webui/static/zjs/common_utils.js'; //

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //Abstract Base Class - Menu
    export class Def_Menu{
        constructor(wc_shadowRoot, wc_inp_data,  menu_renderer, menu_action_obj, ca_renderer){ //, menu_responsive_style){
            this.wc_shadowRoot = wc_shadowRoot;
            this.wc_inp_data = wc_inp_data;

            this.menu_action_obj = menu_action_obj
            this.menu_action_obj.register_menu_obj( this )

            this.menu_renderer = menu_renderer
            this.menu_renderer.register_menu_obj( this )
            
            this.ca_renderer = ca_renderer;
            this.ca_renderer.register_menu_obj( this )

            // this.menu_responsive_style = menu_responsive_style
            // this.menu_responsive_style.register_menu_obj(this)

            this.menu_visible = null
            this.menu_expanded = null
            // debugger
        }

        //******************************************************************************
        // Show the logo, the menu settings, and also the events, then render view
        connectedCallback(  ){
            this.menu_renderer.init_logo()
            this.menu_renderer.init_menus()
            this.init_events()
            this.menu_action_obj.init_view() 
        }

        //******************************************************************************
        init_events(){ throw 'Define concrete method - absrtact'; } 

        //******************************************************************************
        register_linked_menu(wc_linked_menu_obj){
            this.wc_linked_menu_obj = wc_linked_menu_obj
            this.menu_action_obj.init_view() 
        }

        //******************************************************************************
        //show the menu (appear)
        show(){ 
            this.log(`showing menu ${this.constructor.name} `)
            // console.log(`${ new Error().stack }`)
            this.menu_visible = true
            this.menu_action_obj.menu_action_show();
            this.ca_renderer.menu_show_render_content_area()
        }

        //******************************************************************************
        //Expand the menu - especially for minimized menu scenario
        expand(){
            this.log('expanding..')
            this.menu_expanded = true
            this.show()
        }

        //******************************************************************************
        //Minimise the menue 
        reduce(){
            this.log('minimising..')
            this.menu_expanded = false
            this.show()
        }

        //******************************************************************************
        //HIde the menu 
        hide(){
            this.log(`hiding menu ${this.constructor.name}`)
            this.menu_visible = false
            this.menu_action_obj.menu_action_hide();
            this.ca_renderer.menu_hide_render_content_area()
        }

        //******************************************************************************
        //Processing notification event that the linked menu had opened
        observer_linked_menu_opened(){ this.menu_action_obj.observer_menu_action_linked_menu_opened() }
        
        //******************************************************************************
        //Processing notification event that the linked menu had closed
        observer_linked_menu_closed(){ this.menu_action_obj.observer_menu_action_linked_menu_closed() }

        //******************************************************************************
        //Notify the linked menu object, that this menu has 'showed' or 'opened'
        notify_observer_linked_menu_opened(){ 
            if(this.wc_linked_menu_obj){ this.wc_linked_menu_obj.observer_linked_menu_opened() }
        }

        //******************************************************************************
        //Notify the linked menu object, that this menu has 'hide' or 'closed'
        notify_observer_linked_menu_closed(){ 
            if(this.wc_linked_menu_obj){ this.wc_linked_menu_obj.observer_linked_menu_closed() }
        }

        is_debug(){ return false; }
        // log(message){ if(this.is_debug()){ console.log(message)} }
        log(message){ C_UTIL.log( message, this.is_debug(), 3) }


    }


    

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //The sidebar menu style
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Sidebar_Menu extends Def_Menu{ 
 
        //**********************************************************************************************
        init_events(){  
            //Mediq query for the content area
            this.media_query = window.matchMedia(`(min-width: ${this.wc_inp_data.mobile_width_breakpoint_px}px)`) 

            //Link to window resize event
            if( this.wc_inp_data.sbar_menu_list != null ){ this.media_query.addListener(this.menu_action_obj.evt_window_resized.bind(this.menu_action_obj) ); } //make sure correct 'this' is passed

            //Specify how to handle click events for the menu items
            this.wc_shadowRoot.querySelectorAll('.sc_sidebar_menu_has_submenu').forEach(item =>{
                item.addEventListener( 'click',  (event)=> this.evt_click_menu_item_in_sbar(event) );
            });

            //Go through all the events
            if( this.menu_action_obj.is_expandable()){
                this.wc_shadowRoot.querySelector('#si_sbar').addEventListener( 'mouseover',  (event)=> this.evt_mouse_over(event) ); 
                this.wc_shadowRoot.querySelector('#si_sbar').addEventListener( 'mouseout',   (event)=> this.evt_mouse_out(event) );     
            }

            document.addEventListener('scroll', (event)=> this.evt_scroll(event) );
            
        }

        evt_scroll(event){
            // debugger;
            // console.log(  `ScrollTop = ${document.documentElement.scrollTop} , offset=${this.wc_shadowRoot.querySelector('#si_sbar_menu').offsetHeight}` )
            // debugger;
        }
        //******************************************************************** 
        //Mouse hoevered over the menu
        evt_mouse_over(event){ this.expand(); }
        evt_mouse_out(event){  this.reduce(); }

        //******************************************************************** 
        //Click the meun item in the sidebar
        evt_click_menu_item_in_sbar(event){
            var self = event.currentTarget;
            this.log(self);
            var parent = self.parentNode;
            var sub_menu = parent.querySelector("ul");
 
            if( sub_menu.classList.contains('is-hidden') ){
                sub_menu.classList.toggle('is-hidden');
                parent.querySelector('.sck_sbar_submenu_icon').classList.remove('fa-chevron-right');
                parent.querySelector('.sck_sbar_submenu_icon').classList.add('fa-chevron-down');
            }else{
                sub_menu.classList.toggle('is-hidden');
                parent.querySelector('.sck_sbar_submenu_icon').classList.remove('fa-chevron-down');
                parent.querySelector('.sck_sbar_submenu_icon').classList.add('fa-chevron-right');
            }
        }

        
    }

    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    //#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    export class Header_Menu extends Def_Menu{
 
        //**********************************************************************************************
        init_events(){  
            //Go through all the events
            this.wc_shadowRoot.querySelectorAll('.navbar-burger').forEach(item =>{
                item.addEventListener( 'click',  (event)=> this.click_hamburger_event(event) );
            });
        }

        //******************************************************************** 
        //Click the right main meun hamburger
        click_hamburger_event(event){
            this.log('clicked menu icon')
            var self = event.currentTarget; 
            const target = self.dataset.target;
            const $target = this.wc_shadowRoot.getElementById(target);
            // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
            self.classList.toggle('is-active');
            $target.classList.toggle('is-active');
        }

        //******************************************************************** 
        register_linked_menu(wc_linked_menu_obj){
            this.log('registered linked menu obj! ')
            super.register_linked_menu( wc_linked_menu_obj ) 
 
            var si_header_sbar_menu_icon =  this.wc_shadowRoot.getElementById('si_header_sbar_menu_icon') 
            si_header_sbar_menu_icon.addEventListener( 'click',  (event)=> this.side_menu_trigger(event) );
        }

        side_menu_trigger( ){
            // debugger;
            this.log( `menu visible ${this.wc_linked_menu_obj.menu_visible}`)
            if(  this.wc_linked_menu_obj.menu_visible ){
                this.log('hiding menu!')
                this.wc_linked_menu_obj.hide()
            }else{
                this.log('showing menu!')
                this.wc_linked_menu_obj.show()
            }
            
        }

    }
 