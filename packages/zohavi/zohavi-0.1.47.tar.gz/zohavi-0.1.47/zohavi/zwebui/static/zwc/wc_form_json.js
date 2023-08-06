
    import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
    import WCFormControl from  "/webui/static/zwc/wc_form_main.js" 
 
    // var imported = document.createElement('script');
    // imported.src = "https://cdnjs.cloudflare.com/ajax/libs/ajv/8.1.0/ajv7.bundle.js";
    // // imported.src = "https://cdnjs.cloudflare.com/ajax/libs/ajv/8.1.0/ajv7.min.js";
    // // imported.src = "https://cdnjs.cloudflare.com/ajax/libs/ajv/6.12.2/ajv.min.js";
    // document.head.appendChild(imported);

    // import {  Ajv } from  "https://cdnjs.cloudflare.com/ajax/libs/ajv/8.1.0/ajv7.bundle.js" 
    import  ajv7  from  "/webui/static/zjs/ajv7.js" 
 
    

    //************************************************************************************
    //
    class WCJson extends WCFormControl { 
        define_template(){
            var template_str = super.define_template() + `   
                        <div class="field">
                            <table class="table  is-bordered is-fullwidth " id="si_field">
                                <thead>
                                    <tr>
                                        <th style="width:5%"><abbr title="[placeholder::title]">#</abbr></th>
                                        <th colspan=2>[placeholder::title]</th>
                                    </tr>
                                </thead>
                                <tbody class="sck_json_config_top_level">

                                </tbody>
                            </table>
                        </div>`;
            return template_str;
        }

        constructor(){
            super( {"title":"", "schema=json":"", "data=json":""}, ["id"]); 

        } 
    
        //************************************************************************************
        // 
        connectedCallback(){     
             super.connectedCallback(); 

             // debugger;
             this.ajv = new ajv7( { allErrors: true  } ); 

             

             this.load_table( this._inp.schema, this._inp.data );
        }  

        //************************************************************************************
        //
        _init_table(){
            
            // debugger;
            if( this._schema_obj ){
                const validate = this.ajv.compile( this._schema_obj )
                if( this._data_obj ){  
                    var valid = validate(this._data_obj)

                    console.log( `laoded: ${JSON.stringify( valid) }`)
                    valid=true;
                    if(! valid){
                        throw JSON.stringify( validate.errors) 
                    }else{
                        this._build_table ( this._schema_obj, this._data_obj );
                    }
                }
            }
        }

        //************************************************************************************
        //
        _build_table(schema, data ){  
            var tbl_str = this._build_table_node(  new BulletNumber("1") ,  schema.properties, data, schema) 
            this.shadowRoot.querySelector('.sck_json_config_top_level').innerHTML = tbl_str;
            this._set_events_for_table();
        }

        //************************************************************************************
        //
        _set_events_for_table(){
            this.shadowRoot.querySelectorAll('.sck_expand_json_tab').forEach( function(elt, index){
                elt.addEventListener('click', function (e) {  
                    var table_ref_class = e.path[2].querySelector('.sck_expand_json_data > .table').classList
                    if( table_ref_class.contains('is-hidden') ){
                        table_ref_class.remove('is-hidden')
                        e.path[0].innerText = "-"
                    }else{
                        table_ref_class.add('is-hidden')
                        e.path[0].innerText = "+"
                    }
                    return false;
                });
            });
        }

        //**************************************************************************************
        _get_sub_schema_def(path, schema_root){
            var path_list = path.split('/');
            var sub_schema = schema_root
            if( path_list[0] == '#'){
              // debugger;
              for( var path_item of path_list.slice(1)){
                  sub_schema = sub_schema[ path_item ]
              }  
            }else{ throw 'Unrecognised path'  }
            // debugger;
            return sub_schema;

        }

        //**************************************************************************************
        _build_table_node( bullet,  schema, data, schema_root){
            // debugger;
            var tab_str = ""
            var this_ref = this; 

            var schema_elt_type = "";
            var curr_schema = null

            for( var key in data){
                schema_elt_type = "";
                curr_schema = schema[key]
                if( '$ref' in curr_schema)      { curr_schema = this._get_sub_schema_def( curr_schema.$ref, schema_root ) }
                

                if( 'type' in curr_schema)       {  schema_elt_type = curr_schema.type }
                else if( 'anyOf' in curr_schema)      {  schema_elt_type = curr_schema.anyOf }
                else if( 'enum' in curr_schema) { schema_elt_type = 'enum' }
                else{ debugger; throw `Property type elet in schema[${key}] not found: ${ JSON.stringify( curr_schema ) } ` }

                if( schema_elt_type =="object"){
                    tab_str += this._build_table_node_object(   bullet, key, curr_schema, data , schema_root   ); 
                }else if( schema_elt_type =="array"){ 
                    tab_str += this._build_table_node_array(   bullet  , key,  curr_schema , data , schema_root   ); 
                }else if( ['string', 'integer', 'enum'].includes( schema_elt_type ) ){ 
                    tab_str += this._build_table_node_element(   bullet  , key,  curr_schema, data ,  schema_elt_type   ); 
                }else if( Array.isArray( schema_elt_type ) ){  //Is an AnyOf object
                    tab_str += this._build_table_node_element(   bullet  , key,  curr_schema, data ,  this._get_field_type(data[key] )   ); 
                }else{
                    debugger;
                    throw `Unrecognised type ${schema_elt_type} at location=${key}`
                }
            }
            return tab_str;
        }

        _get_field_type(field){
            if (typeof field === 'string' || field instanceof String){
                return 'string';
            }else if (typeof field === 'number' || field instanceof Number){
                return 'integer';
            }else if (typeof field === 'boolean' || field instanceof Boolean){
                return 'boolean';
            }else{
                throw `Unkown element type of field=${field} => type=${typeof field} `
            }
        }

        
 

        //**************************************************************************************
        _build_table_node_element( bullet  , key, sub_schema, data, schema_elt_type ){
          var tab_str = `<tr>`
          tab_str += `  <th style="width:5%">${bullet.get()}</th>`
          tab_str += `  <td style="width:10%" >${  key }</td>`
          // tab_str += `  <td  ><input type="text" value="${ data[key] }"></td>`
          if( ['string', 'integer', 'boolean'].includes( schema_elt_type ) ){ 
            tab_str += `  <td class="ck_json_config_item" data-elt_type="elt-input">`
            tab_str += `          <wc-input-text id="" class=" sck_grp_env_config ck_json_config_item" value="${ data[key] }" `
            tab_str += `          validation='{"required":true}' data-key="${key}" ></wc-input-text></td>`
          }else if ( schema_elt_type == 'enum' ){
            var json_list = {}
            sub_schema.enum.forEach( function( elt, index){ json_list[ elt ] = elt; });
            tab_str += `  <td class="ck_json_config_item" data-elt_type="elt-select">`
            tab_str += `         <wc-select id="" class=" sck_grp_env_config ck_json_config_item" label="" `
            tab_str += `                    list='${JSON.stringify(json_list)}' data-key="${key}"></wc-select> `
          }else{
            throw `Do not recognize type ${schema_elt_type} in schema[${key}] not found`
          }
          tab_str += `</tr>`

          bullet.increment() 

          return tab_str;
        }

        //**************************************************************************************
        _build_table_node_object(bullet, key, sub_schema, data, schema_root){
            bullet.indent()
            tab_str += `<tr>`
            tab_str += `    <th >${bullet.get()}</th>`
            tab_str += `    <td  >${key}</td>` 
            tab_str += `    <td>`
            tab_str += `        <table class="table is-fullwidth  ">`
            tab_str += `            <tbody>`
            tab_str += this._build_table_node(  new BulletNumber( bullet.get() ) , sub_schema.properties, data[key] , schema_root  );
            tab_str += `            </tbody>`
            tab_str += `        </table>`
            tab_str += `    </td>`
            tab_str += `</tr>`
            bullet.outdent()
            return tab_str;
        }

        //**************************************************************************************
        _build_table_node_array(bullet, key, sub_schema, data, schema_root){
            var tab_str ="";
            tab_str += `<tr><th style="width:5%">${bullet.get()}</th>`
            tab_str += `    <td style="width:10%" >${key}[<a href="javascript:void(0);" class='sck_expand_json_tab'>+</a>]`
            tab_str += `        <br>(${ Object.keys(data[key]).length })</td>` 
            tab_str += `    <td class='sck_expand_json_data ck_json_config_item' data-elt_type="array" data-key="${key}">`
            tab_str += `          <table class="table  is-hidden is-fullwidth"><tbody>`
            var index = 0;
            bullet.indent()
            for( var data_item in data[key] ){
                tab_str += `            <tr><td class="is-vcentered " style="border-width:0; width:5%">[${index}]</td></tr>`
                tab_str += `            <tr><td  style="border-width:0">`
                tab_str += `                    <table class="table  is-fullwidth ck_json_config_item_arry_elt">`
                tab_str += `                        <tbody>`
                tab_str += this._build_table_node(   new BulletNumber( bullet.get()) , 
                                                sub_schema.items.properties, data[key][data_item], schema_root )
                tab_str += `                        </tbody>`
                tab_str += `                    </table>`
                tab_str += `                 </td></tr>` 
                index++;
            }
            bullet.outdent()

            tab_str += `            </tbody></table></td></tr>`
            return tab_str;
        }

        //************************************************************************************
        //
        load_table(schema, data){
            this.schema = schema
            this.data = data
            this._init_table()
        }

        //************************************************************************************
        //
        set schema(value_schema ){
            this.setAttribute("schema", value_schema)
            var input_value = value_schema
            if (typeof input_value === 'string' || input_value instanceof String){
                input_value = JSON.parse( input_value )
            }
            this._schema_obj = input_value
        }

        //************************************************************************************
        //
        set data(value_data ){
            this.setAttribute("data", value_data)
            var input_value = value_data
            if (typeof input_value === 'string' || input_value instanceof String){
                input_value = JSON.parse( input_value )
            }
            this._data_obj = input_value
        }


        //************************************************************************************
        //
        get_json_config(){
            var json_config = this._get_sub_json_config( this.shadowRoot.querySelectorAll('tbody.sck_json_config_top_level >tr > td.ck_json_config_item') )
            return json_config
        }


        //************************************************************************************
        //
        _get_sub_json_config(main_elt_list){
          var json_sub_config = {}
          var obj_this = this

            main_elt_list.forEach( function (elt){

              if( elt.dataset["elt_type"] == 'elt-input'){
                json_sub_config[ elt.childNodes[1].dataset["key"]   ] = elt.childNodes[1].value
              }else if( elt.dataset["elt_type"] == 'elt-select'){
                json_sub_config[ elt.childNodes[1].dataset["key"]   ] = elt.childNodes[1].value
              }else if( elt.dataset["elt_type"] == 'array'){

                json_sub_config[ elt.dataset["key"]   ] = [] 
                elt.querySelectorAll(':scope > table > tbody > tr > td > table.ck_json_config_item_arry_elt').forEach( function(arr_elt){
                  json_sub_config[ elt.dataset["key"]   ].push( obj_this._get_sub_json_config( arr_elt.querySelectorAll( ':scope > tbody > tr > td.ck_json_config_item') ) )
                });
                
              }
              //console.log( elt.dataset["type"] )
            }); 
          // console.log( json_sub_config )
          return json_sub_config
        }
 
    }

    //************************************************************************************
    // 
    class BulletNumber{

        constructor( start_bullet ){   //"1.1"
            this.bullet = start_bullet.split(".").map( function(item){ return parseInt(item); })
            // this.bullet =  
            this.index = this.bullet.length -1
        } 
        indent(){
            if( this.bullet.length >= (this.index+1)){
                this.bullet.push(1); //Add another item in there
            }
            this.index = this.bullet.length - 1; //point to the last item
            return this.get()
        }
        outdent(){
            if(this.index > 0){ this.index--; }
            return this.get()
        }
        increment(){
            this.bullet[ this.index ] ++;
            return this.get()
        }

        decrement(){
            this.bullet[ this.index ] --;
            return this.get()
        }

        get(){
            return this.bullet.map( function(item){ return item.toString(); }).join(".");
        }
    }
    
    window.customElements.define('wc-json', WCJson); 