 
    // import('/common/st/_def/commonui/static/_def/js/transformation_helper.js'); //
    import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
    import WCMaster from  '/webui/static/zwc/wc_master.js' ;



     export default class WCFormControl extends WCMaster  { 
        define_template(){
            return super.define_template() + `
                    <style>

                        .sc_disabled_background {
                            xxx-background-color: grey !important; 
                            border: none;
                        }
                    </style>

            `
        }

        constructor(optional_attrib_dict, mandatory_attrib_list) {
            // super();  
            super( optional_attrib_dict, mandatory_attrib_list) 
            
        }

        

        //************************************************************************************
        //Setup the defaults and events
        connectedCallback( ){   
            super.connectedCallback();   
            this.update_form_validation_status( this._inp.state ) 
            // if( validate_on_change == false ){
            //     debugger;
            // }
            
            // this.shadowRoot.querySelectorAll('input').forEach(item =>{
            this.shadowRoot.querySelectorAll('#si_field').forEach(item =>{
                item.addEventListener( 'change',  (event)=> this.evt_validate_on_value_change(event) ); 
                item.addEventListener( 'change',  (event)=> this.evt_dispatch_change(event) );
            });

            //setup defaults
            if( this.getAttributeNames().indexOf("disabled") >= 0){
                this.field_disable(true)
            }
        } 

        // //************************************************************************************
        // //Setup the defaults and events
        // set_def_field_attributes(){
        //     if( this.getAttributeNames().indexOf("disabled") >= 0){
        //         this.field_disable(true)
        //     }
        // }

        //************************************************************************************
        //Setup the defaults and events
        field_disable(status){
            if( status ){
                this.shadowRoot.getElementById("si_field").disabled = true
                this.shadowRoot.getElementById("si_label").classList.add("has-text-grey")
                this.shadowRoot.getElementById("si_field").classList.add("sc_disabled_background")
            }else{
                this.shadowRoot.getElementById("si_field").disabled = false
                this.shadowRoot.getElementById("si_label").classList.remove("has-text-grey")
            }
            
        }


        

           

        //************************************************************************************
        //Update the validation statis
        update_form_validation_status(new_state){
            // console.log('adding : ' + new_state)
            if( new_state == "success"){
                this.add_help_message( "is-success", this._inp.message_suc );
            }else if( new_state ==  "fail"){ 
                var message = this._inp.message_err;
                if(!message){  message = ValidationHelper.validate_helper_message( this._inp.validation ); }

                this.add_help_message( "is-danger", message );
            }else{
                this.clear_help_message();
            }
        }

        //************************************************************************************
        //Add help message
        add_help_message(message_formatter, message){
            this.clear_help_message(); 
            this.shadowRoot.getElementById("si_field").classList.add(message_formatter);
            var help_msg_elt = this.shadowRoot.getElementById("si_help_message")

            if( help_msg_elt && message){
                help_msg_elt.classList.remove("is-invisible"); 
                help_msg_elt.classList.add(message_formatter); 
                help_msg_elt.innerHTML =  message; 
                
            }
        }

        //************************************************************************************
        //clear help message
        clear_help_message( ){
            this.shadowRoot.getElementById("si_field").classList.remove("is-danger", "is-success");
            var $si_help_msg = this.shadowRoot.getElementById("si_help_message");
            // if( typeof $si_help_msg != 'undefined'){
            if(  $si_help_msg  ){
                this.log('updating help message ')
                $si_help_msg.classList.add("is-invisible"); 
                $si_help_msg.classList.remove("is-danger", "is-success"); 
                // $si_help_msg.innerHTML =   "."
            }
        }
        
        field_editable(status){  
            this.shadowRoot.getElementById('si_field').disabled =true;
            this.shadowRoot.getElementById('si_label').classList.add('has-text-grey')
            if(status){
                this.shadowRoot.getElementById('si_field').disabled =false ;
                this.shadowRoot.getElementById('si_label').classList.remove('has-text-grey')
            }  
        }



        //************************************************************************************
        //Validation - dummy function
        validate(){
            this.log(  this.constructor.name +  " " + (new Error()).stack.match(/at (\S+)/g)[0].slice(3) + " not defined")
            
            return true;
        } 

        value(){
            this.log(  this.constructor.name +  " " + (new Error()).stack.match(/at (\S+)/g)[0].slice(3) + " not defined")
            return "";
        }

        //******************************************************************
        //Run validation on the field based on "validation" attribute
        evt_validate_on_value_change(e){ 
            // console.log("validating")
            // debugger
            this.transform( e.path[0] ); // transform first
            var result = this.validate(  e.path[0].value , this._inp.validation  ); // then validate

            // var value = this.shadowRoot.getElementById('si_field').value;
            const event = new CustomEvent('validated', { detail: {this:this, elt:e.path[0], value:e.path[0].value, validation_result:result  }});
            this.dispatchEvent(event , { bubbles:true, component:true} );
        }

        //******************************************************************
        //Run validation on the field based on "validation" attribute
        evt_dispatch_change(e){   
            console.log('sending change evet..')
            const event = new CustomEvent('change', { detail: {this:this, elt:e.path[0], value:e.path[0].value  }});
            this.dispatchEvent(event , { bubbles:true, component:true} );
        }

        //************************************************************************************
        //get json data of the value of the form fields.  This is for data to be submitted to forms
        get_submit_data(){
            var value = this.value;
            if(!value){ value = ""; }
            var ret_value = { "id":this.id, "value":value, "display_value":this.display_value } //, "orig_id":orig_id}
            this.log( "returning: " + JSON.stringify( ret_value ))
            return  ret_value
        }
     
        // //************************************************************************************
        // //get data to be displayed to user, default is same as submission data but can be overriden.
        // get_display_data(){
        //     return this.get_submit_data()
        // }


        //Transform the fields
        transform(field){
            var transformation_list = this._inp.transform;
            if( ! transformation_list){ return; }
            //loop through each input and check the validation
            transformation_list.split('|').every( rule_name => {
                field.value = TransformHelper["transform_"+rule_name](  field.value ); 
            } ); 
        }

        get value(){
            // console.log('##getting value:' + this.shadowRoot.getElementById('si_field').value)
            return this.shadowRoot.getElementById('si_field').value;
        }

        set value(value ){  
            if( ! this.hasAttribute("const") ){
                this.shadowRoot.getElementById('si_field').value = value;
                this.shadowRoot.getElementById('si_field').setAttribute("value", value); 
                this.setAttribute("value", value)
                this._inp.value = value
            }
        }

        get display_value(){
            return this.value;
        }
        set display_value(value){
            this.value = value
            this.setAttribute('display_value', value);
            this._inp.display_value = value
        }
        

        get validation(){
            return this._inp.validation
        }

        set validation( value ){  
            var validation_value = this.convert_field( 'validation', value )
            var elt = this.shadowRoot.getElementById('si_field')

            elt.setAttribute('validation_ref', validation_value);
            this.setAttribute('validation', validation_value);
            this._inp.validation = validation_value
        }

    }
    window.customElements.define('wc-form-main', WCFormControl);



    
// })();
// 