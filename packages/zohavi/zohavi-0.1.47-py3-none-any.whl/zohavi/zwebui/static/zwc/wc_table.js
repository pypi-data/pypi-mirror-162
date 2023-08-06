    
    import C_UTIL, {C_UI, C_AJAX } from '/webui/static/zjs/common_utils.js'; //
    // import {C_UI, C_AJAX} from '/webui/static/zjs/common_utils.js'; //

    import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
    import WCFormControl from  "/webui/static/zwc/wc_form_main.js" 
    import WCModal from  "/webui/static/zwc/wc_modal.js" 
    import WCButton from  "/webui/static/zwc/wc_form_button.js" 
    
    
    import  ajv7  from  "/webui/static/zjs/ajv7.js" 
 



 
    export default class WCTable extends WCFormControl { 
        define_template_globals(){
            return `:host{ 
                        --table_header_cell_color: var(--background_cat3_color);
                        --table_header_text_color: var(--light_text_color_cat1);

                        --table_cell_bg_key_color: var(--background_cat2_color);
                    }`
        }

        define_template(){
            var add_button_html = ""
            var template_str = ""
            if( this._inp.add_row ){
                add_button_html = `<div class="container mt-2 mb-2 level-right">
                                        <div class="level-item has-text-centered"> 
                                            <p class="control "> 
                                                <wc-button id="si_add_row" label="[placeholder::add_row]" active_class="is-success" > </wc-button>  
                                            </p>  
                                        </div>
                                    </div>`;
            }else{
                add_button_html = ""
            }

            template_str = super.define_template() + `   
                        <style>
                                ${this.define_template_globals()}

                                .sc_cell_validation_failed{  
                                    background-image: linear-gradient(225deg, red, red 10px, transparent 10px, transparent);
                                    color: red; 
                                }

                                .sc_cell_bg_key_color{
                                    background-color: var(--table_cell_bg_key_color);
                                    color: var(--light_text_color_cat1);
                                    font-weight: bold;
                                }
                                .sc_cell_disabled{
                                    background-color: grey
                                }

                                .table thead th{ /*over ride bulma setting */
                                    background-color: var(--table_header_cell_color);
                                    color: var(--table_header_text_color);
                                }
                        </style>

                        <div class="container">
                            ${ add_button_html }

                            <table id="si_field" class="table is-bordered is-striped is-hoverable is-fullwidth">
                                <thead id="si_thead"  >
                                  <!--
                                      <tr>
                                        <th width="20%" class="sc_table_header">Env</th>
                                        <th width="60%" class="sc_table_header">URL</th>
                                        <th width="20%" class="sc_table_header">Port</th>
                                      </tr>
                                  -->
                                </thead>
                                <tbody id="si_tbody">
                                    <!--
                                        <tr>
                                            <td  > Dev </td>
                                            <td class="sck_validation " data-validation="required|is_url" data-validation_msg="Must include a URL"  contenteditable> </td>
                                            <td class="sck_validation "  data-validation="required|num_gte:1000|num_lte:9999" data-validation_msg="Must include a 4 digit port number"  contenteditable> </td>
                                        </tr>
                                    -->
                                </tbody>
                            </table>
                        </div>` +
            this.define_template_modal();

            return template_str;
        }

        define_template_modal(){
            return ` <wc-modal id="si_modal" title="Edit"
                                fields='[]'> 
                    </wc-modal>`;
               
        }
                    // columns='[
                    //       {"col_label":"Name", "key":"ck_env_name" },
                    //       {"col_label":"Description", "key":"ck_env_desc" },
                    //       {"col_label":"Code", "key":"ck_env_code" },
                    //       {"col_label":"Action", "key":"ck_env_action" }
                    // ]'

                    // data='[ {"row_no":1, "data-id":"1",   
                    //                               "row":[  {"key":"ck_env_name", "value":"Dev", "data-value":"dev", "data-id":"1",     
                    //                               "cell_key_color":"true"},
                    //                               {"key":"ck_env_desc", "value":"Development"},
                    //                               {"key":"ck_env_code", "value":"dev"},
                    //                               {"key":"ck_env_action", 
                    //                                          "icons":[ {"icon":"fa-edit", "class_key":"ck_env_edit", "data-value":"1"},
                    //                                                    {"icon":"fa-trash", "class_key":"ck_env_delete", "data-value":"1"}] }
                    //                             ] },
                    //         {"row_no":2, "data-id":"2", 
                    //                               "row":[  {"key":"ck_env_name", "value":"Dev", "data-value":"dev", "data-id":"2" ,    
                    //                               "cell_key_color":"true"},
                    //                               {"key":"ck_env_desc", "value":"Development"},
                    //                               {"key":"ck_env_code", "value":"dev"},
                    //                               {"key":"ck_env_action", 
                    //                                          "icons":[ {"icon":"fa-edit", "class_key":"ck_env_edit", "data-value":"2"},
                    //                                                    {"icon":"fa-trash", "class_key":"ck_env_delete", "data-value":"2"}] }
                    //                             ] },
                    //         {"row_no":3, "data-id":"3", 
                    //                               "row":[  {"key":"ck_env_name", "value":"Dev", "data-value":"dev", "data-id":"3"},
                    //                               {"key":"ck_env_desc", "value":"Development"},
                    //                               {"key":"ck_env_code", "value":"dev"},
                    //                               {"key":"ck_env_action", 
                    //                                          "icons":[ {"icon_class":"fas fa-edit", "class_key":"ck_env_edit", "data-value":"3"},
                    //                                                    {"icon_class":"fas fa-trash", "class_key":"ck_env_delete", "data-value":"3"}] }
                    //                             ] }
                    //       ]'

        constructor(){
            super( {"add_row":"", "data=json":"[]", "field_params=json":"", 
                    "submit_on_add":"",  "submit_on_edit":"", "submit_on_del":"", "submit_hidden_data=json":"",
                    "popup_messages=json":"",
                    "action_icons=json":'{"edit":"fas fa-edit","delete":"fas fa-trash"}'}, ["columns=json", "id"]);   
            // debugger;
            this.ajv = new ajv7()
        } 

        connectedCallback(){     
            // this.log('hello world')
             super.connectedCallback(); 

             this.validate_schema_submit_hidden_data()
             this.validate_schema_popup_messages()
             this.validate_schema_columns()
             this.validate_schema_column_params()
             this.validate_schema_data()
        } 

        

        //************************************************************************************
        //Update teh default settings per field once shadowdom is setup
        init_component(){
            var this_obj = this;
            this.log('initing')
            this.init_data()
            this.init_modal(this._inp.columns);

            this.create_table( this._inp.columns );
            // this.init_table_data(this._inp.data)
            this.init_table_data(this._inp.columns, this._inp.data)
            
            this._modal_ref = this.shadowRoot.querySelector('#si_modal')

            var add_row_elt = this.shadowRoot.querySelector('#si_add_row')
            if( add_row_elt){
                add_row_elt.addEventListener('click', this.evt_add_row_clicked.bind(this) );
            }
            // this.init_modal( this._inp.columns);
        }

        init_data(){
            this._inp.data.forEach( function(item, index){
                item['data-row_no'] = index;
            });
        }
        //************************************************************************************
        init_modal(columns){
            var this_obj = this;
            var field_list = []
            // debugger;
            for( var col_index in columns){
                const elt = columns[col_index ]
                if( elt.editable == "true" || elt.hidden == "true"){
                    var field_data = {}
                    field_data.type = this_obj._init_modal_get_field_type(elt)
                    field_data.label = elt.col_label;
                    field_data.id = elt.id;
                    field_data.validation = elt.validation;

                    if( "field_params" in elt){  //If there are further parameters - e.g. lookup fields
                        // debugger;
                        for( var param_field in elt.field_params){
                            const param_name = elt.field_params[ param_field ]
                            field_data[ param_field ] = this._inp.field_params[ param_name  ]
                        }
                    }
                    field_list.push( field_data );
                }
            };
            this.shadowRoot.querySelector('#si_modal').fields = field_list;
        }

        //************************************************************************************
        _init_modal_get_field_type(elt){
            if( elt.hidden  == "true" ){ return 'hidden'; }
            return ( typeof elt.type  === 'undefined' ? 'input': elt.type );    
        }
        
        

        //************************************************************************************
        //Delete row from table
        delete_row(row_no){
            // debugger
            var curr_data_row = this._inp.data[ row_no ]

            var table_row = this.shadowRoot.querySelector(`tr[data-row_no='${row_no}']`)
            table_row.parentNode.removeChild(table_row);
            
            // this.submit_data( this._inp.submit_on_del, curr_data_row )
            this.submit_data(   this._inp.submit_on_del, curr_data_row, 
                                this._inp.popup_messages.del_success, 
                                this._inp.popup_messages.del_fail) 
        }

        //************************************************************************************
        //Add events to table cells
        add_table_row_item_events(){
            this.shadowRoot.querySelectorAll('.sc_icon_clickable').forEach(item =>{
                item.addEventListener( 'click',  (event)=> this.evt_icon_clicked(event) );  
            });
            
        }
        
        //************************************************************************************
        //Add events to table cells
        evt_add_row_clicked(event){
            this._modal_ref.show( null, null, this.callback_row_add.bind(this) );
        }
        //************************************************************************************
        //Add events to table cells
        evt_icon_clicked(event){ 
            // this.log('clicked')
            // debugger;
            if( event.path[1].dataset['action'] == 'edit' ){
                this.edit_row_entry( event.path[1].dataset['row_no'] )
                
            }else if( event.path[1].dataset['action'] == 'delete' ){
                this.delete_row( event.path[1].dataset['row_no'] )
            }

            var new_event = new CustomEvent( 'table_icon_click', { detail: {this:this, 
                                                                            elt:event.path[1], 
                                                                            id:event.path[1].dataset['id'], 
                                                                            value:event.path[1].dataset['value'],
                                                                            row_no:event.path[1].dataset['row_no'],  }}); 
            this.dispatchEvent(new_event , { bubbles:true, component:true} ); 
        }

        
        //************************************************************************************
        //edit row number (zero index entry)
        edit_row_entry(row_no){
            var curr_data_row = this._inp.data[ row_no ]
            // debugger;
            this._modal_ref.show( curr_data_row, {'row_no':row_no}, this.callback_row_edited.bind(this) );
            this.log( 'showed modal')
            
        }

        //************************************************************************************
        submit_data( url, data, success_message, fail_message, callback){
            var this_ref = this
            C_AJAX.ajax_post( url, data, 
                function(success_data){
                    if( success_message  ){ C_UI.popup_success( success_message ); }
                    if( callback ){ callback( success_data ) }
                    this_ref.trigger_custom_event( success_data, 'submit_success');
                    
                },
                function(fail_data){
                    if( fail_message  ){ C_UI.popup_fail( fail_message ); } 
                    if( callback ){ callback( fail_data ) }
                    this_ref.trigger_custom_event( fail_data, 'submit_failed');
                } );
        }

        //** 
        _submit_data_callback_row_add( ret_data){
            if( ret_data.success ){  //If return successfully
                var new_data = [];
                this._inp.columns.forEach(  function( col){
                    var item = {}
                    var db_field_name;
                    item.id = col.id

                    for (const [key, schema_data] of Object.entries( ret_data.schema )) {
                        if( item.id in schema_data.fields){
                            db_field_name = schema_data.fields[ item.id ].field_db;
                        }
                    }

                    item.value = ret_data.data[0][ db_field_name ]
                    new_data.push( item );
                });

                this._callback_row_add_update_table(new_data);
                this._callback_row_add_update_data_twin(new_data);
                this.add_table_row_item_events()
            }
        }

        //************************************************************************************
        callback_row_add(action,  ref_data,  new_data){
            // debugger;
            // this.log()
            var full_data = new_data;
            if( this._inp.submit_hidden_data){ full_data = new_data.concat( this._inp.submit_hidden_data ) }
            console.log('adding')
            console.log( JSON.stringify( full_data) )
            if( action == this._modal_ref.C_SAVE){ 

                if( this._inp.submit_on_add ){
                    console.log('submit_on_add')
                    // debugger;
                    // this.submit_data( this._inp.submit_on_add, full_data
                    this.submit_data(   this._inp.submit_on_edit, full_data, 
                                        this._inp.popup_messages.add_success, this._inp.popup_messages.add_fail, 
                                        this._submit_data_callback_row_add.bind( this) )
                }
                
            }
        }

        //************************************************************************************
        _callback_row_add_update_data_twin(submit_data){
            //Update the internal data records
            var inp_new_data_temp = []
            submit_data.forEach( function(elt){
                
                var new_data_rec = {}
                new_data_rec['id'] = elt.id
                new_data_rec['value'] = elt.value
                if( 'data-value' in elt ){
                    new_data_rec['data-value'] = elt['data-value']    
                }
                inp_new_data_temp.push( new_data_rec )
            });
            this._inp.data.push( inp_new_data_temp )
        }
        //************************************************************************************
        _callback_row_add_update_table(submit_data){
            var table_str = "";
            var tbody_ref = this.shadowRoot.getElementById('si_tbody')
            var new_row_no = tbody_ref.childNodes.length
            //Update the table row
            table_str += this.init_table_data_row( this._inp.columns, submit_data, 'id', new_row_no )
            tbody_ref.innerHTML = tbody_ref.innerHTML + table_str;
            tbody_ref.childNodes[ new_row_no ].querySelector('.sc_icon_clickable').addEventListener( 'click',  (event)=> this.evt_icon_clicked(event) ); 
        }

        //************************************************************************************
        //edit row number (zero index entry)
        callback_row_edited(action, ref_data, new_data){
            var this_obj = this;
            var full_data = new_data;
            if( this._inp.submit_hidden_data){ full_data = new_data.concat( this._inp.submit_hidden_data ) }
             
            if(action == this._modal_ref.C_SAVE ){
                console.log( JSON.stringify( full_data) )

                if( this._inp.submit_on_edit ){
                    console.log('submit_on_edit')
                    // debugger;
                    this.submit_data(   this._inp.submit_on_edit, full_data,
                                        this._inp.popup_messages.edit_success, 
                                        this._inp.popup_messages.edit_fail )
                }

                // var row_elt = this.shadowRoot.querySelectorAll('tr.sck_data_row')[ ref_data['row_no'] ]
                var row_elt = this.shadowRoot.querySelector(`tr[data-row_no='${ ref_data['row_no'] }']` ) //find table row entry
                // 
                for( const elt_key in full_data){ //loop through and udpate values
                    var data_item = full_data[ elt_key ]
                    var inp_data_fields = this._inp.data[  ref_data['row_no']  ] 
                     
                    for( const input_data_key  in inp_data_fields){
                        if( inp_data_fields[ input_data_key ].id == full_data[ elt_key ].id ){
                            inp_data_fields[ input_data_key ].value = full_data[ elt_key ].value 
                        }
                    };
                    
                    var html_elt = row_elt.querySelector('.' + data_item.id )  
                    if(html_elt){   //If this is a default hidden field from [submit_hidden_data] tehre may not be an html element
                        html_elt.innerHTML = data_item.display_value;
                        html_elt.dataset['value'] = data_item.value;
                    }
                    
                };
                
            }
        }
        


        //************************************************************************************
        //Add attribute element
        add_attribute(search_attribute_name, attribute_data_obj, write_attrib_name){
            if( search_attribute_name in attribute_data_obj){
                var new_attrib_name = ( write_attrib_name ? write_attrib_name : search_attribute_name )
                return `${new_attrib_name}='${attribute_data_obj[search_attribute_name]}' `
            }
            return "";
        }

        //************************************************************************************
        add_table_attrb_class_list( attrib_data_obj, class_key_list, additional_class_list){
            var class_str = ""
            class_key_list.forEach( function(elt){
                if( elt in attrib_data_obj     ){ class_str += attrib_data_obj[ elt ] + " "; }
            });

            if( additional_class_list){
                additional_class_list.forEach( function(class_item){ class_str += class_item + " "; });    
            }
            
            return 'class ="' + class_str +'" '
        }

        //************************************************************************************
        init_table_data(cols, data){
            var table_str = ""; 
            var this_obj = this;
            // debugger
            data.forEach( function( data_row, row_no ){
                table_str += this_obj.init_table_data_row( this_obj._inp.columns, data_row, 'id', row_no )
            });
            this.shadowRoot.getElementById('si_tbody').innerHTML = table_str; 
            this.add_table_row_item_events()
        }

        
        //************************************************************************************
        init_table_data_row(cols, row_data, key_field_name, row_no){
            var this_obj = this;
            var row_str = "";

            row_str += `<tr `;
            row_str += this_obj.add_table_attrb_class_list( row_data, ['class'],  ['has-text-centered', 'sck_data_row'] )
            row_str += `data-row_no="${row_no}" `
            // row_str += this_obj.add_attribute( 'data-row_no', row_data )  
            // debugger;
            
            row_str += ">"
            cols.forEach( function( col){
                var data_cell = C_UTIL.search_list_dict_key_value( row_data, key_field_name , col[ 'id' ] );
                
                row_str += `<td `
                row_str += this_obj.add_attribute( 'width', col )
                row_str += `data-row_no="${row_no}" `
                
                if( col['hidden'] ){  row_str += ' style="display:none;" ' }
                if( data_cell ){  //in case this is a static cell - 
                    if( 'data-value' in data_cell){ row_str += `data-value="${ data_cell['data-value'] }"`
                    }else{  row_str += `data-value="${ data_cell['value']}"` }    

                    row_str += this_obj.add_attribute( 'validation', data_cell, 'data-validation' )

                    row_str += this_obj.add_table_attrb_class_list( data_cell, [ key_field_name ] ) 
                }

                // if( 'validation')


                //set background color
                if(  String( col['key_field']).toLowerCase() == 'true'){ row_str += `class="sc_cell_bg_key_color" ` }
                row_str += '>'

                if( col['type'] == 'actions'){
                    row_str += this_obj._init_table_cell_add_actions( col,  row_no );
                }else if( data_cell ){
                    row_str += this_obj.shadowRoot.querySelector('#si_modal').get_field_display_value(data_cell.id,data_cell.value)
                } 
                row_str += '</td>'
            });

            row_str += `</tr>`;

            return row_str;
        }

        //************************************************************************************
        // Add any icon elements in a table cell
        //example: "icons":[ {"icon_class":"fa-edit", "class_key":"ck_env_edit", "data-value":"3"},
        //                   {"icon_class":"fa-trash", "class_key":"ck_env_delete", "data-value":"3"}] }
        _init_table_cell_add_actions( col_entry, row_no ){
            var cell_str = "";
            var this_obj = this;
            // debugger;
            col_entry.actions.forEach( function(action_item ){

                // var icon_class = search_list_dict_key_value( this_obj._inp.action_icons, 'action', action_item )

                cell_str += `<a href="#" ` 
                cell_str += `data-action="${action_item}" ` 
                cell_str += `data-row_no="${row_no}" `
                cell_str += `class="sc_icon_clickable" >`
                cell_str += `<i class="${ this_obj._inp.action_icons[ action_item ] }"></i>`
                cell_str += `</a>`
                // debugger
            });
            
            return cell_str; 
        }



        //************************************************************************************
        //Update teh default settings per field once shadowdom is setup
        create_table(columns){
            var table_str = "<tr>"; 
            var this_obj = this;
            columns.forEach( function( elt){
                table_str += `<th `;
                table_str += this_obj.add_table_attrb_class_list( elt, ['class', 'id'] )
                table_str += this_obj.add_attribute( 'width', elt );

                if( elt['hidden'] ){  table_str += ' style="display:none;" ' }

                table_str += `>${elt.col_label}</th>`; 
            });
            table_str += `</tr>`;
            if(columns){ 
                this.shadowRoot.getElementById('si_thead').innerHTML = table_str; 
            }else{ 
                this.shadowRoot.getElementById('si_thead').innerHTML = ""; 
            }
        }


        //************************************************************************************
        // columns='[
        //              {"col_label":"ID", "id":"si_env_id", "editable":"false", "hidden":"true","key_field":"true"},
        //              {"col_label":"Name", "id":"si_env_name", "editable":"true"},
        //              {"col_label":"Description", "id":"si_env_desc", "editable":"true" },
        //              {"col_label":"Code", "id":"si_env_code", "editable":"true", "validation":{"text_min_len":4}  },
        //              {"col_label":"Action", "id":"si_env_action", "type":"actions", "data-key":"ck_env_edit", "actions":["edit","delete"] }
        //   ]'
        validate_schema_columns(){
            const schema = {
                type: "array",
                items: {
                            type: "object",
                            properties:{
                                            col_label   : {type: "string"},
                                            id          : {type: "string"},
                                            editable    : { "$ref": "#/definitions/bool_type"},
                                            hidden      : { "$ref": "#/definitions/bool_type"},
                                            type        : { type: "string", enum: ["input", "hidden", "select", "checkbox", "actions"] },
                                            "data-key"  : {type: "string"},
                                            actions     : { type: "array", items: {  type: "string"  } },
                                            key_field   : { "$ref": "#/definitions/bool_type"},
                                            field_params       : { type: "object", properties:{  list: { type: "string"} } },
                                            validation : {
                                                            type            : "object",
                                                            properties:{
                                                                            text_min_len    : {type: "number"},
                                                                            text_max_len    : {type: "number"},
                                                                            text_num_gte    : {type: "number"},
                                                                            text_num_lte    : {type: "number"},
                                                                            required        : { "$ref": "#/definitions/bool_type"} }
                                            }
                                        },
                            required: ["col_label", "id"]
                        },
                definitions: {
                    bool_type: {    type: "string",
                                    enum: ["false","true"] }
                }
            } 
            this.validate_schema( 'columns', this._inp.columns, schema )
        }

        //************************************************************************************
        // param='{
        //    "file_type_list":{"log":"Log", "base":"Base Directory", "app":"App Directory",  "def":"Library Directory", "resdef":"Resource  Directory"}
        //}'

        validate_schema_column_params(){
            const schema = {
                type: "object",
                properties: {}
            }
            this.validate_schema( 'field_params', this._inp.field_params, schema )
        }

        //************************************************************************************
        // data='[ [    {"id":"si_env_id", "value":"1" },
        //              {"id":"si_env_name", "value":"Dev", "data-value":"1" },
        //              {"id":"si_env_desc", "value":"Development"},
        //              {"id":"si_env_code", "value":"dev"}  ] ]
        validate_schema_data(){
            const schema = {
                type: "array",
                items: {
                            type: "array",
                            items: {
                                        type: "object",
                                        properties:{
                                            id          : {type: "string"},
                                            value       : {},
                                            "data-value": {type: "string"}
                                        },
                                        required: ["id", "value"]
                                    }
                        }
            }

            this.validate_schema( 'data', this._inp.data, schema )
        }
        //************************************************************************************
        // submit_hidden_data='{"id":"si_env_id", "value":"{{env_data.id}}" }' 
        validate_schema_submit_hidden_data(){
            const schema = {
                type: "object",
                properties: {
                  id    : {type: "string"},
                  value : {type: "string"}
                },
                required: ["id", "value"],
                additionalProperties: false
              }
            this.validate_schema( 'submit_hidden_data', this._inp.submit_hidden_data, schema )
        }

        //************************************************************************************
        // popup_messages='{    "add_success":"added", "add_fail":"failed to add", 
        //                      "edit_success":"edited", "edit_fail":"failed to edit", 
        //                      "del_success":"deleted", "del_fail":"failed to delete" }'
        validate_schema_popup_messages(){
            const schema = {
                type: "object",
                properties: {
                    add_success     : {type: "string"},
                    add_fail        : {type: "string"},
                    edit_success    : {type: "string"},
                    edit_fail       : {type: "string"},
                    del_success     : {type: "string"},
                    del_fail        : {type: "string"}

                },
                required: ["add_success", "add_fail","edit_success", "edit_fail", "del_success", "del_fail"],
                additionalProperties: false
              }
            this.validate_schema( 'popup_messages', this._inp.popup_messages, schema )
        }

        //************************************************************************************
        // check schema
        validate_schema( attribute_name, attribute_value, schema){
            if(attribute_value){
                const validate = this.ajv.compile(schema)
                const valid = validate( attribute_value )
                if (!valid){
                    // debugger;
                    throw `Failed validation of json for ${this._inp.id} '${attribute_name}':: [${ JSON.stringify(validate.errors)}]`;
                }
            }
            return true;
        }

        is_debug(){ return false; } 

    }

    window.customElements.define('wc-table', WCTable);
