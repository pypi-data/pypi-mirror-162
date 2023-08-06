(function() { 
  
    // var wc_form_ref_instance = customElements.get('wc-form-main');
 
    class WCSidePanel extends HTMLElement { 

        define_template(){
            return `
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.2/css/all.min.css"
                integrity="sha512-HK5fgLBL+xu6dm/Ii3z4xhlSUyZgTT9tuc/hSrtw6uzJOvgRr2a9jyxxT1ely+B+xFAmJKVSTbpM/CuL7qxO8w=="
                crossorigin="anonymous" />
            <article id="si_panel" class="panel is-success">
                <!-- -->
                <a href="#" class="panel-block is-active">
                    <span class="panel-icon"><i class="fas fa-book" aria-hidden="true"></i></span>
                    Name</a>
                <a class="panel-block">
                <span class="panel-icon"><i class="fas fa-book" aria-hidden="true"></i></span>
                Database</a>
            </article>`;
        }

        constructor(){
            super();  
            
            this.template = document.createElement('template');
            this.template.innerHTML = this.define_template(); 
            
            // this.init_template( this.template );

            this.attachShadow({ mode: 'open' }); 
            this.shadowRoot.appendChild( this.template.content.cloneNode(true)); 

            this._active_panel_item = null;

            // this.init_defaults();
            // this.check_attributes( [  "label", "placeholder", "validation", "message_err"], []);
        } 
        connectedCallback(){
            this._panel_menu_config = JSON.parse( this.getAttribute('panel_menu_list'))
            this.render_panel_menus( this._panel_menu_config );
            this.init_show_active_panel(this._panel_menu_config);

            this.shadowRoot.querySelectorAll('.panel-block').forEach(item =>{
                item.addEventListener( 'click',  (event)=> this.evt_panel_item_click(event) ); 
            });
        }

        //*************************************************************
        //show the active panel on startup   
        init_show_active_panel( panel_menu_config){
            var $target_panel_area;
            var obj_this = this;
            panel_menu_config.forEach( function(menu_item, index){ 
                $target_panel_area = document.getElementById( menu_item["target"] );
                if( $target_panel_area){
                    if( menu_item["active"]== "true"){ 
                        $target_panel_area.classList.remove('is-hidden');
                        obj_this._active_panel_item = $target_panel_area;
                    }else{
                        $target_panel_area.classList.add('is-hidden');
                    }
                } 
            });
        }
        //***************************************************************
        //Setup the panel configuratoins based on panel_menu_list atribute
        render_panel_menus(panel_menu_config){
            var $panel_menu= this.shadowRoot.querySelector('#si_panel');
            
            if( typeof panel_menu_config == 'undefined'){ return; }

            var menu_item_str = '';
            panel_menu_config.forEach( (menu_item) => { 
                menu_item_str += `<a href="#" id="si_panel_item_${menu_item["target"]}" 
                                    class="panel-block ${menu_item["active"] == "true"?"is-active has-text-success":""}" 
                                    data-target="${menu_item["target"]}">${ this.render_panel_text( menu_item) }</a>`
            });
            $panel_menu.innerHTML = menu_item_str;

            return panel_menu_config;
        }

        
        //***************************************************************
        //update the label
        re_render_panel_text(key, updated_keys){
            // console.log(`repainting ${key}  => ${ JSON.stringify( updated_keys) }`)
            this._panel_menu_config.some( (menu_item) => {
                if( menu_item["target"]== key ){
                    for( const [key, value] of Object.entries( updated_keys) ){
                        // console.log( `key = ${key} item = ${value}`)
                        menu_item[ key ] = value;
                    } 

                    var link = this.shadowRoot.getElementById("si_panel_item_" + menu_item["target"])
                    // debugger;
                    link.innerHTML = this.render_panel_text( menu_item )

                    return;
                }
            });
        }        


        //***************************************************************
        //update the label
        render_panel_text(menu_item){
            var link_text = `<span class="panel-icon"><i class="fas ${menu_item["icon"]}" aria-hidden="true"></i></span>`
            var label = menu_item["label"]
            if( menu_item[ "modified"] ){ label += " <span class='has-text-info'> [modified]</span>" }
            if( menu_item[ "validation"] == true ){ label += " <span class='has-text-success'> ok</span>" }
            if( menu_item[ "validation"] == false ){ label += " <span class='has-text-danger'> not ok</span>" }
            return link_text + "<span>" + label + "</span>";
        } 

        //***********************************************
        // Panel item was clicked
        evt_panel_item_click(e){
            var clicked_field = e.path[0].closest("a")
            console.log("clicked :" + clicked_field.id + ":" + clicked_field.dataset["target"] )
            // if(e.path[0].id){  debugger; }
            var $panel_items = this.shadowRoot.querySelectorAll('.panel-block');
            $panel_items.forEach( function(item, index){
                item.classList.remove("is-active", "has-text-success");
            });

            clicked_field.classList.add("is-active", "has-text-success" );

            if( this._active_panel_item ){
                this._active_panel_item.classList.add('is-hidden');
            }
            this._active_panel_item = document.getElementById( clicked_field.dataset["target"] )
            if( this._active_panel_item ){
                this._active_panel_item.classList.remove('is-hidden');
            }
        }
    }
    
    window.customElements.define('wc-side-panel', WCSidePanel);

})();

