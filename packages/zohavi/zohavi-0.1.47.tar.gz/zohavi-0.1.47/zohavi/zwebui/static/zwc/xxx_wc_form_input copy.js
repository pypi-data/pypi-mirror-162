 
 
    import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
    import WCFormControl from  "/webui/static/zwc/wc_form_main.js" 
    
 

    // var wc_form_ref_instance = customElements.get('wc-form-main');
     

    // class WCInput extends wc_form_ref_instance { 
    export default class WCInput extends WCFormControl { 
        define_template(){
            var template_str = super.define_template() + `   
                        <div class="field">
                            <label id="si_label" class="label">[placeholder::label]</label>
                            <div id="si_control_format" class="control  ${ this._inp['icon_left']?'has-icons-left':''} 
                                                                        ${ this._inp['icon_right']?'has-icons-right':''} ">
                                <input  id="si_field" class="sck_field input" name="[placeholder::id]" class="input " 
                                        type="text" placeholder="[placeholder::placeholder]" value="[placeholder::value]" 
                                        validation_ref=[placeholder::validation]> `
            if( this._inp['icon_left']){
                template_str += `<span  id="si_icon_start" class="icon is-small is-left">
                                    <i class="fas [placeholder::fa_icon_start]"></i>
                                </span>`
            }

            if( this._inp['icon_right']){
                template_str += `<span id="si_icon_end" class="icon is-small is-right">
                                    <i class="fas [placeholder::fa_icon_end]"></i>
                                </span>`  
            }
                    
            template_str += `</div>`

            template_str += `<p id="si_help_message" class="help is-invisible">${this._inp['message_err']}</p>`
            
            template_str += `</div>`;
            return template_str;
        }

        constructor(){
            super( {"label":"", "placeholder":"", "validation=json":"", "message_err":"", "value":"", "icon_left":"", "icon_right":""}, ["id"]); 
        } 
    
        //************************************************************************************
        //Setup the defaults and events
        connectedCallback(){     
             super.connectedCallback(); 
        }  

        init_component(){

        }

        //************************************************************************************
        //Update teh default settings per field once shadowdom is setup
        init_input_text_defaults(){
            if(!this._inp.fa_icon_start ){
                this.shadowRoot.getElementById("si_control_format").classList.remove("has-icons-left");
                this.shadowRoot.getElementById("si_icon_start").classList.add("is-hidden");
            }
            if(!this._inp.fa_icon_end ){
                this.shadowRoot.getElementById("si_control_format").classList.remove("has-icons-right");
                this.shadowRoot.getElementById("si_icon_end").classList.add("is-hidden");
            }  
        }

        //************************************************************************************
        //Validation given cell element 
        validate( ){
            var input_field = this.shadowRoot.getElementById('si_field')
            var result;
            // debugger;
            if(! ValidationHelper.validate( input_field.value , this._inp.validation , true)){ 
                this.update_form_validation_status("fail"); 
                result = false
            }
            else{
                this.update_form_validation_status("success");
                result = true
            }
            //notify that validation was done
            const event = new CustomEvent('validated', { detail: {this:this, elt:input_field, value:input_field.value, validation_result:result  }});
            this.dispatchEvent(event , { bubbles:true, component:true} ); 
            return result;
        
        } 
 
    }

 
    
    window.customElements.define('wc-input-text', WCInput); 
