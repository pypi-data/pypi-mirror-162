    import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
    import WCMaster from  '/webui/static/zwc/wc_master.js' ;
    // import WCPanel from   '/webui/static/zwc/wc_panel.js' ;

       export default class WCTab extends WCMaster  { 
        define_template(){
            return super.define_template() + `
                    <div class=" tabs is-boxed pt-2">
                        <ul id="si_ul_item">
                        <!-- 
                            <li class="is-active" id="si_tab_li_env" data-target="i_env_config_panel">
                              <a href="#"  class="sck_tab_main_item" id="si_tab_env_href_overview"  >
                                <span class="icon is-small"><i class="fas fa-image" aria-hidden="true"></i></span>
                                <span>Overview</span>
                              </a>
                            </li> 
                        --> 
                      </ul>
                    </div>

            `
        }

        //************************************************************************************
        constructor( ) { 
            super( {}, ["id", "tabs=json"]);   
        }

        //************************************************************************************
        connectedCallback(){ 
            super.connectedCallback();      
            this.init_tab_click_event();
        }

        //************************************************************************************
        init_component(){
            var obj_this = this;
            // var tab_item_list= JSON.parse( this._inp.tabs ); 
            var tab_html = "";
            // console.log( tab_item_list );
            this._inp.tabs.forEach( function(tab_item, index){ 

                tab_html += obj_this._init_tab_items_generate_html(tab_item );
                // debugger;
                if( tab_item['status']=='active'  ){
                    var panel = document.querySelector( '#' + tab_item['target'] )
                    if( panel ){
                        // debugger;
                        panel.show();
                    }else{
                        throw( `#${m['target']} element has not been defined for tabs`)
                    }
                    
                }
                
            });

            var tab_item_list_elt = this.shadowRoot.querySelector('#si_ul_item');
            tab_item_list_elt.innerHTML = tab_html
        }


        //************************************************************************************
        _init_tab_items_generate_html( tab_item){
            var tab_html = "";
            tab_html += `<li class="${ 'status' in tab_item && tab_item['status']=='active' ? "is-active" : ""}" `
            tab_html += `    id="${tab_item['id']}" data-target="${tab_item['target']}">`
            tab_html += `    <a href="#"  class="sck_tab_item" id="${tab_item['id'] + '_href'}"  > `
            tab_html += `        <span class="icon is-small"><i class="${tab_item['icon']}" aria-hidden="true"></i></span>`
            tab_html += `        <span>${tab_item['label']}</span>`
            tab_html += `    </a>`
            tab_html += `</li>`

            return tab_html;
        }

        //************************************************************************************
        // manage tabs and the targets they send to
        init_tab_click_event(){ 
            var obj_this = this;

            this.shadowRoot.querySelectorAll('.sck_tab_item').forEach( function( element, index){
                element.addEventListener('click', function (e) { 
                    //go through and remove the active class from all tabs
                    e.path[0].closest('#si_ul_item').childNodes.forEach(function( element, index){
                    if( element.nodeName == 'LI' ){  //If this is an element node of a list element
                      if (element.classList.contains("is-active")) {
                        element.classList.remove('is-active');
                        // obj_this.shadowRoot.querySelector('')
                        console.log( `Hiding existint: ${element.dataset.target}`);
                        document.querySelector('#' + element.dataset.target).hide();
                        
                      }
                    }
                    } );
                
                    //show the clicked item
                    var new_tab_li = e.srcElement.closest('li');
                    new_tab_li.classList.add('is-active');
                    console.log( `Showing new : ${new_tab_li.dataset.target}`);
                    document.querySelector('#' + new_tab_li.dataset.target ).show();
                });

              });
        }

    }


    //
    class WCPanel extends WCMaster  { 
        define_template(){
            return super.define_template() + ` 
                    <div class="  is-hidden m-1" id="si_field">
                        <slot></slot>
                    </div>

            `
        } 

        constructor( ) {
            // super();  
            super( {}, ["id"]); 
            
        }

        init_component(){}
        
        hide(){
            this.shadowRoot.querySelector('#si_field').classList.add('is-hidden');

            //trigger event that panel is hidden
            const event = new CustomEvent('panel_disappear', { detail: {this:this  }} );
            this.dispatchEvent(event , { bubbles:true, component:true} ); 
        }

        show(){
            this.shadowRoot.querySelector('#si_field').classList.remove('is-hidden');

            //trigger event that panel is shown
            // console.log("trigger panel appear [0]:" + this.id )
            // console.log( this.id )
            const event = new CustomEvent('panel_appear', { detail: {this:this  }} );
            // this.dispatchEvent(event , { bubbles:true, component:true} ); 
            this.dispatchEvent(event , {bubbles:true,component:true } ); 
            // console.log("trigger panel appear [1]:" + this.id )
        }
    }

    // var ver = 1

    // console.log( "Version=" + ver )
    // console.log( 'adding wc-tab')
    window.customElements.define('wc-tab-panel', WCPanel);
    window.customElements.define('wc-tab', WCTab);
    // console.log( 'adding wc-tab-panel')
    

