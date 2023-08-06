 
    // import('/common/st/_def/commonui/static/_def/js/transformation_helper.js'); //
    import WCMaster from  '/webui/static/zwc/wc_master.js' ;

    export  default class WCPanel extends WCMaster  { 
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
            console.log("trigger panel appear [0]:" + this.id )
            // console.log( this.id )
            const event = new CustomEvent('panel_appear', { detail: {this:this  }} );
            // this.dispatchEvent(event , { bubbles:true, component:true} ); 
            this.dispatchEvent(event , {bubbles:true,component:true } ); 
            console.log("trigger panel appear [1]:" + this.id )
        }

    }

 
    window.customElements.define('wc-tab-panel', WCPanel);