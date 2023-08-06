
    import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
    import WCFormControl from  "/webui/static/zwc/wc_form_main.js" 
 

    // var wc_form_ref_instance = customElements.get('wc-form-main');
    

    export default class WCCheckbox extends WCFormControl { 
        define_template(){
            return  super.define_template() + ` 
    
            <div  class="field">
                <label class="label">[placeholder::label]</label>
                <div id="si_control_format" class="control"> 
                    <label class="checkbox">
                        <input id="si_field" type="checkbox" class="sck_field" name="[placeholder::name]">
                            [placeholder::checkbox_label]
                    </label>  
                </div>
                <p id="si_help_message" class="help is-invisible">.</p>  
            </div>
                
            `;
        }

        constructor(){
            super( {"label":"", "checkbox_label":"", "value=bool":"", "target_when_on":"", "target_when_off":""}, ["id"]); 

            // this.init_defaults();
            // console.log('init checkbox')
            // console.log('create checkbox')
            // this.debug=true 
        } 


        //************************************************************************************
        //Update teh default settings per field once shadowdom is setup
        init_component(){
            // if( this.getAttribute('value') ){
            this.value = this._inp.value;
            // } 

            if( this._inp.target_when_on || this._inp.target_when_off ){
                this.shadowRoot.querySelector('#si_field').addEventListener( 'change',  (event)=> this.evt_toggle_target(event) );
            } 

            this.render_panels();
            
        }

        evt_toggle_target(event){
            this.render_panels()
        }

        render_panels(){
            const elt_when_on  = document.getElementById(this._inp.target_when_on )
            const elt_when_off = document.getElementById(this._inp.target_when_off )
            // debugger;
            if( this.value ){
                    if( elt_when_on ){ elt_when_on.show(); } 
                    if( elt_when_off){ elt_when_off.hide(); } 
            }

            if( !this.value  ){
                    if( elt_when_off) { elt_when_off.show(); }
                    if( elt_when_on){ elt_when_on.hide(); }
            }

            if( this._inp.target_when_on && !elt_when_on){      //could not find the element
                console.warn( `Could not find elt id:${this._inp.target_when_on} from checkbox [${this.id}]`)
                // debugger;
            }

            if( this._inp.target_when_off && !elt_when_off){      //could not find the element
                console.warn( `Could not find elt id:${this._inp.target_when_on} from checkbox [${this.id}]`)
            }

        }

    
        //************************************************************************************
        //Setup the defaults and events
        connectedCallback(){     
             super.connectedCallback(); 
        }

        get value(){
            // console.log('##getting value:' + this.shadowRoot.getElementById('si_field').value)
            return this.shadowRoot.getElementById('si_field').checked;
        }

        set value(new_value ){  
            this.shadowRoot.getElementById('si_field').checked = new_value;            
            this.shadowRoot.getElementById('si_field').setAttribute("checked", new_value); 
            this.setAttribute("value", new_value)
            this._inp.value = new_value
            this.render_panels()
        }

         
    }

     
    window.customElements.define('wc-checkbox', WCCheckbox); 
