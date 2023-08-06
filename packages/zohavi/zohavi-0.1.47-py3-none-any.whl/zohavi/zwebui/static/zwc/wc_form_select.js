 
 
    import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
    import WCFormControl from  "/webui/static/zwc/wc_form_main.js" 
 

    // var wc_form_ref_instance = customElements.get('wc-form-main');
     

    // class WCInput extends wc_form_ref_instance { 
    export default class WCSelect extends WCFormControl { 
        define_template(){
            return super.define_template() + `   
            <div class="field">
                <label id="si_label" class="label">[placeholder::label]</label>
                <div id="si_control_format" class="  select"> 
                    <select id="si_field" class="sck_field " name="[placeholder::id]" >
                        <!-- fill the list here -->
                    </select>
                </div>
                ${ this._inp['message_err'] ? '<p id="si_help_message" class="help is-invisible">.</p>':'' }  
            </div>  
            `;
        }

        constructor(){
            super({  "label":"",  "message_err":"", "value":"", "list=json":"", 
                     "blank_entry":"", "item_select_get_data":"", "select_change_target":""}, ["id"]);  
              
            // this.init_input_text_defaults(); 
        } 
    
        //************************************************************************************
        //Setup the defaults and events
        connectedCallback(){     
             super.connectedCallback(); 
        }  

        //************************************************************************************
        //Update teh default settings per field once shadowdom is setup
        init_component(){
            this._fill_option_list( this._inp.value );
        }

        //******************************************************************
        //Run change event
        evt_dispatch_change(e){   
            console.log('sending change evet for SELECT ..')
            const event = new CustomEvent('change', { detail: {this:this, elt:e.path[0], value:e.path[0].value  }});
            this.dispatchEvent(event , { bubbles:true, component:true} );
        }


        //************************************************************************************
        //Fill out the option list
        _fill_option_list(){
            var $select_field_ref = this.shadowRoot.getElementById('si_field'); 
            var default_value = this._inp.value;
            // debugger;
            var option_item_str=''; 
            if(this._inp.blank_entry ){
                option_item_str +=   this._fill_option_list_get_option('',  this._inp.blank_entry, default_value);
            }
            for (var option_value in this._inp.list) {
                option_item_str +=   this._fill_option_list_get_option(option_value, this._inp.list[ option_value]  , default_value );   
            }

            $select_field_ref.innerHTML = option_item_str;  
        }

        _fill_option_list_get_option(value, option_text, default_value){
            // debugger;
            if( default_value == value ){
                return `<option value="${value}" selected>${ option_text }</option>`
            }
            return `<option value="${value}"  >${ option_text }</option>`
        }


        //************************************************************************************
        //Validation given cell element 
        validate( ){
            var input_field = this.shadowRoot.getElementById('si_field')
            var result;
            if(! ValidationHelper.validate( input_field.value , this._inp.validation )){ 
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

        get display_value(){
            // debugger;
            return this._inp.list[ this.value];
            // return this.value;
        }

        // //************************************************************************************
        // //get json data
        // get_data(){
        //     return  { id:this.id, value:this.value() }
        // }
        
        // value(){
        //     return this.shadowRoot.getElementById('si_field').value;
        // }
 
    }

 
    
    window.customElements.define('wc-select', WCSelect); 
