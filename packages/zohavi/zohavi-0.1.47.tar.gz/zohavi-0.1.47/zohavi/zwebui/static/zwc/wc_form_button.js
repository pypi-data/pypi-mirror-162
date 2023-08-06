//**************************************************************************************************************
// Used to abstract and simplify button ajax submission for forms where you can specify the submit and the cancel 
// actions so as not to repeat the code.
//
//  Usage: 
//      <wc-form-button
//          buttons='  {label:"Save" , id:"si_btn_save", action:"/submit/action", callback:"abcfunc()", 
//                      visible:"false" [default:true], enabled:"false" [default:true]} active_class:"is-primary" deactive_class:"[disabled]" 
//                      size: "is-small"}
//      </wc-form-button>
//
//
//**************************************************************************************************************
    import {C_UI, C_AJAX} from '/webui/static/zjs/common_utils.js'; //
    import WCMaster from  '/webui/static/zwc/wc_master.js' ;



     export default class WCButton extends WCMaster  { 
        define_template(){

            return super.define_template() + `   
                <button id="si_field" class="button [placeholder::size]">[placeholder::label]</button> 
            `
        }

        //*********************************************************************************************************************
        // CONSTRUCTOR
        constructor() {
            super( {    action:"", active_class:"is-primary", deactive_class:"[disabled]", 
                        size: "is-small", submit_data_selector:"", 
                        popup_message_submit_success:"", 
                        popup_message_submit_fail:""
                    }, 
                    ["label"]);  

            this.init_button();
            this._debug = true 
        }

        //************************************************************************************
        //Setup the defaults and events
        connectedCallback(){     
            super.connectedCallback(); 
            var this_ref = this
            // debugger;
            //send out the button click
            this.shadowRoot.querySelector('#si_field').addEventListener('click', function( event ){

                if( this_ref._inp.action ){   //send submit
                    this_ref.submit_data(event);
                }

                //finally send out own event if required
                const custom_event = new CustomEvent( 'wc_click', { detail: {this:this_ref }});
                this_ref.dispatchEvent(custom_event , { bubbles:true, component:true } ); 
            });
            
        }

        init_component(){
            
        }

        //************************************************************************************
        validate_attributes(){
            if( this._inp.submit_data_selector && ! this._inp.action ){   //send submit
                throw `Input Attribute error: Provided "submit_data_selector" but must be paired with "action" to see where to submit to` 
            }

            if( !this._inp.submit_data_selector && this._inp.action ){   //send submit
                throw `Input Attribute error: Provided "action" but must be paired with "submit_data_selector" to see what to validate`
            }
        }

        //************************************************************************************
        //Fill out the option list
        submit_data(e){ 
            var this_ref = this
            var read_to_submit = false  
            
            if( this_ref._inp.submit_data_selector ){
                var data = C_UI.get_validated_wc_form_data(  this._inp.submit_data_selector ) 
                if( data ){  read_to_submit = true; }
            }else{
                read_to_submit = true;
            }
            
            // debugger;
            // var data = C_UI.get_validated_wc_form_data(  this._inp.submit_data_selector ) 
            if( read_to_submit ){  
                this._inp.action = this._inp.action  //get latest action setting
                this_ref.log( 'submitt to url : ' + this._inp.action + '::' + JSON.stringify( data ) );

                C_AJAX.ajax_post(this_ref._inp.action, data, 
                                function(success_data){
                                    if( this_ref._inp.popup_message_submit_success  ){
                                        C_UI.popup_success( this_ref._inp.popup_message_submit_success );
                                    }
                                    this_ref.trigger_custom_event( success_data, 'submit_success');
                                },
                                function(fail_data){
                                    console.log( `Failed to submit::`)
                                    console.log( JSON.stringify(fail_data) )
                                    if( this_ref._inp.popup_message_submit_fail  ){
                                        var field_err = this_ref.failed_submit_render_error_field_message( fail_data , this_ref._inp.submit_data_selector)
                                        C_UI.popup_fail( this_ref._inp.popup_message_submit_fail +":\n" + field_err );
                                    }
                                    this_ref.trigger_custom_event( fail_data, 'submit_failed');
                                } );
            }else{
                this_ref.trigger_custom_event( data, 'validation_failed');
                throw "***validation failed**"
            }
        }
        
         

        
        //************************************************************************************
        //Process error message from submit_data
        failed_submit_render_error_field_message(failed_data, field_selector ){
            // var this_ref = this;
            var err_msg = ""
            failed_data.result.validations.forEach( function(validation_check ){
               if( !validation_check.success ){
                   err_msg += ( err_msg ? ", " + validation_check.err_msg : validation_check.err_msg )
                   document.querySelectorAll( field_selector ).forEach( function(item ){
                       if( item.id == validation_check.web_field_name ){
                        item.update_form_validation_status('fail')
                        return  //break out of loop 
                       }
                   });
                //    document.querySelector(this._inp.submit_data_selector'#update_form_validation_status').update_form_validation_status('fail')
               }
            });

            return err_msg
        }


        //************************************************************************************
        //Fill out the option list
        init_button(){ 
            var btn_ref = this.shadowRoot.getElementById('si_field');
            btn_ref.classList.add( this._inp.active_class )
        }
    }

    window.customElements.define('wc-button', WCButton); 