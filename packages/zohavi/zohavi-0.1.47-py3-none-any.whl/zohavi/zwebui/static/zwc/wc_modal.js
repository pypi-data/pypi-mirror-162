    import C_UTIL from '/webui/static/zjs/common_utils.js'; //

    import WCFormControl from  "/webui/static/zwc/wc_form_main.js" 
    import WCCheckbox from "/webui/static/zwc/wc_form_checkbox.js"
    import WCFormInput from  "/webui/static/zwc/wc_form_input.js" 
    import WCFormHidden from  "/webui/static/zwc/wc_form_hidden.js" 
    import WCSelect from  "/webui/static/zwc/wc_form_select.js" 
    import {FieldChecker, 
            FieldChecker_Extractor_Dict} from '/webui/static/zjs/field_checker.js'


    //********************************************************************************
    class WCDispatcher{
        constructor( field_checker_obj ){
            field_checker_obj.check_required_fields();   //check that mandatory fields given
            this._inp = field_checker_obj.get_dict(); 
            // this._field_id = field_id;
        }
        get_html(){ throw 'Abstract - must be mplemented'}
        convert_int_to_ext_value(internal_value){  return internal_value; }
        // get_src(){ throw 'Abstract - must be mplemented'}
    }

   //********************************************************************************
    //Check fields for INPUT
    class WCDispatch_Input extends WCDispatcher{
        constructor(inp_obj, field_id){ 
            super( new FieldChecker( {"id":field_id, "label":"", "validation":"", "message_err":"", "value":""}, [], 
                   new FieldChecker_Extractor_Dict( inp_obj ) )  );   
        }
        get_html(json){
            var validation ="";
            if( this._inp.validation){ validation = JSON.stringify(this._inp.validation); }
            return `<wc-input-text id="${this._inp.id}" class="sck_grp_modal_field" 
                                    label="${this._inp.label}" validation='${ validation }' 
                                    message_err="${this._inp.message_err}" value='${this._inp.value}' >
                    </wc-input-text>`
        }
    }

    //********************************************************************************
    //Check fields for INPUT HIDDEN
    class WCDispatch_Hidden extends WCDispatcher{
        constructor(inp_obj, field_id){ 
            super( new FieldChecker( {"id":field_id, "label":"" , "value":""}, [], 
                   new FieldChecker_Extractor_Dict( inp_obj ) )  );   
        }
        get_html(json){
            var validation ="";
            if( this._inp.validation){ validation = JSON.stringify(this._inp.validation); }
            return `<wc-input-hidden id="${this._inp.id}" class="sck_grp_modal_field" 
                                    label="${this._inp.label}" value='${this._inp.value}' >
                    </wc-input-hidden>`
        }
    }

    //********************************************************************************
    //Check fields for INPUT
    class WCDispatch_Select extends WCDispatcher{
        constructor(inp_obj, field_id){ 
            super( new FieldChecker( {"id":field_id, "label":"", "validation":"", "message_err":"", "value":"", "list":""}, [], 
                   new FieldChecker_Extractor_Dict( inp_obj ) )  );
        }

        get_html(json){
            // debugger;
            var validation ="";
            if( this._inp.validation){ validation = JSON.stringify(this._inp.validation); }
            return `<wc-select id="${this._inp.id}" class="sck_grp_modal_field" 
                                    label="${this._inp.label}" validation='${ validation }' 
                                    message_err="${this._inp.message_err}" value='${this._inp.value}' list='${JSON.stringify(this._inp.list)}' >
                    </wc-select>`
        }

        convert_int_to_ext_value(internal_value){  
            if( this._inp.list && internal_value in this._inp.list){
                return this._inp.list[ internal_value ];
            }
            return internal_value;
            // return internal_value; 
        }
    }

    //********************************************************************************
    //Check fields for CHECKBOX
    class WCDispatch_Checkbox extends WCDispatcher{
        constructor(inp_obj, field_id){ 
            super( new FieldChecker( {"id":field_id,"label":"", "checkbox_label":"", "value=bool":""}, [], 
                   new FieldChecker_Extractor_Dict( inp_obj ) ) );
        }

        get_html(){
            return `<wc-input-checkbox id="${this._inp.id}" class="sck_grp_modal_field" checkbox_label="${this._inp.checkbox_label}" 
                                        label="${this._inp.label}" value="${this._inp.value}">
                    </wc-input-checkbox>`
        }
        // get_src(){
        //     return `<script type="module" src="/common/st/_def/commonui/static/_def/wc/wc_form_checkbox.js"></script>`
        // }
    }

    export default class WCModal extends WCFormControl { 
        define_template_globals(){
            return `:host{ 
                        --table_header_cell_color: var(--background_cat3_color);
                        --table_header_text_color: var(--light_text_color_cat1);

                        --table_cell_bg_key_color: var(--background_cat2_color);
                    }`
        }

        define_template(){
            var template_str = super.define_template() + `   
                        <style>
                                ${this.define_template_globals()}
                        </style>

                        <div class="modal" id="si_field">
                          <div class="modal-background"></div>
                          <div class="modal-card">
                            <header class="modal-card-head">
                              <p class="modal-card-title" id="si_modal_title">[placeholder::title]</p>
                              <button id="si_modal_close" class="delete" aria-label="close"></button>
                            </header>
                            <section class="modal-card-body" id="si_modal_contents">
                                <!-- content  -->   
                            </section>
                            <footer class="modal-card-foot">
                              <button id="si_modal_save" class="button is-success">Save</button>
                              <button id="si_modal_cancel" class="button">Cancel</button>
                            </footer>
                          </div>
                        </div>
                        <div id='si_web_component_scripts'>
                            
                        </div>
                        `
            return template_str;
        }
        
        //  fields =    [
        //                  {'type':'input',    'value':'abc', validation:{'abc'}, 'message_err':'abc', ''} ,
        //                  {'type':'checkbox', 'value':'abc', validation:{'abc'}, 'message_err':'abc', ''} ,
        //              ]
        //  buttons =   [
        //                  
        //              ]
        constructor(){
            super( {"title":"", "buttons=json":"[]"}, ["fields=json"]);  


            this.components = {
                                'input':   WCDispatch_Input ,
                                'hidden':   WCDispatch_Hidden ,
                                'select':   WCDispatch_Select ,
                                'checkbox': WCDispatch_Checkbox 
            }
        } 

        set fields(dict_obj ){ 
            this._inp.fields = dict_obj
            this.init_component();
        } 

        get fields( ){ 
            return this._inp.fields;
        } 

        get C_SAVE(){ return 'SAVE'; }
        get C_CANCEL(){ return 'CANCEL'; }
        get C_CLOSE(){ return 'CLOSE'; }

        connectedCallback(){      
            super.connectedCallback(); 

            this.shadowRoot.querySelector('#si_modal_close').addEventListener( 'click',  (event)=> this.evt_modal_close(event) );  
            this.shadowRoot.querySelector('#si_modal_cancel').addEventListener( 'click',  (event)=> this.evt_modal_cancel(event) );  
            this.shadowRoot.querySelector('#si_modal_save').addEventListener( 'click',  (event)=> this.evt_modal_save(event) );  
        } 

        //************************************************************************************
        //Update teh default settings per field once shadowdom is setup
        init_component(){
            var this_obj = this; 
            this.create_modal( this._inp.fields ); 

            
        }


        //************************************************************************************
        //Update teh default settings per field once shadowdom is setup
        create_modal(columns){ 
            var modal_str = "";
            var script_list_str = "";
            var this_obj = this;
            var field_id_count = 0;
            var field_id = "";

            columns.forEach( function( elt){
                field_id_count++;
                field_id = (elt.id?elt.id: elt.type +String(field_id_count) ); //get provided field id, or a unique one

                const field_obj = this_obj.components[ elt.type ]

                if( field_obj){
                    elt.field_dispatcher = new field_obj(elt, field_id );    
                }else{
                    throw `The object ${elt.type} not defined under supported components`
                }

                
                modal_str += elt.field_dispatcher.get_html(); 
            });
             
            this.shadowRoot.getElementById('si_modal_contents').innerHTML = modal_str
            // this.shadowRoot.getElementById('si_web_component_scripts').innerHTML = script_list_str
        }
        
        //************************************************************************************
        //show the modal
        show(data_rows, ref_data, callback_fn){
            var this_obj = this;
            this_obj._callback = callback_fn
            this_obj._callback_ref_data = ref_data
            // debugger;
            if( data_rows){
                data_rows.forEach( function(elt){

                    var col_field = C_UTIL.search_list_dict_key_value( this_obj._inp.fields, 'id' , elt.id  );  //find the original column ref
                    var node = this_obj.shadowRoot.getElementById( elt.id );
                    if(node){ 
                        node.value = elt.value 
                        node.setAttribute("value", elt.value )  //set attribute as well so you can see on html side
                        if( elt.validation ){ 
                            node.validation = elt.validation    //Get the over ride validation
                        }else{
                            node.validation = col_field.validation //get the default validation
                        }  //if validatio over ride then add
                    }
                });    
            }else{
                this_obj.shadowRoot.querySelectorAll( '.sck_grp_modal_field' ).forEach( function(elt){
                    elt.value = "";
                });
            }
            
            this.shadowRoot.getElementById('si_field').classList.add('is-active');
        }

        //************************************************************************************
        //clsoe the modal - no information is reset
        hide(){
            this.shadowRoot.getElementById('si_field').classList.remove('is-active');
        }
        
        //************************************************************************************
        //Close or cancel button pressed
        evt_modal_close(event){ 
            this.hide();
            if( this._callback ){ this._callback( this.C_CLOSE, this._callback_ref_data, null ) }
        }

        //************************************************************************************
        //Close or cancel button pressed
        evt_modal_cancel(event){ 
            // debugger
            this.hide();
            if( this._callback ){ this._callback( this.C_CANCEL, this._callback_ref_data, null ) }
        }

        //************************************************************************************
        //Close or cancel button pressed
        evt_modal_save(event){ 
            var data = []
            var validation_ok = true;
            this.shadowRoot.querySelectorAll('.sck_grp_modal_field').forEach( function(elt){
                // if( typeof elt.validation !== 'undefined'){ 
                validation_ok = validation_ok & elt.validate(); 
                data.push( elt.get_submit_data() );
            });

            if( validation_ok){
                var new_event = new CustomEvent( 'modal_save', { detail: {this:this, data:data} } ); 
                this.dispatchEvent(new_event , { bubbles:true, component:true} ); 

                if( this._callback ){ this._callback( this.C_SAVE, this._callback_ref_data, data ) }
                this.hide();    //Hide afterwards
            }
            
            
        }


        get_field_display_value(field_name, internal_value){
            for( var element in this._inp.fields ){

                if( this._inp.fields[ element].id === field_name){
                    return this._inp.fields[ element].field_dispatcher.convert_int_to_ext_value(internal_value);
                }

            }
            return internal_value;
        }

        is_debug(){ return false; } 

    }

    window.customElements.define('wc-modal', WCModal);


    
