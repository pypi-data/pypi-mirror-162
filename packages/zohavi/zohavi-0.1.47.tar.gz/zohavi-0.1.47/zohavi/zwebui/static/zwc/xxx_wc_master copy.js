
// module WCMaster{ 
import C_UTIL from '/webui/static/zjs/common_utils.js'; // 
import {FieldChecker, 
        FieldChecker_Extractor_WC} from '/webui/static/zjs/field_checker.js'

 export default class WCMaster extends HTMLElement { 
    define_template(){
        //<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css">
            return `

                    <link rel="stylesheet" href="/webui/static/zcss/main.css">

                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.2/css/all.min.css"
                    integrity="sha512-HK5fgLBL+xu6dm/Ii3z4xhlSUyZgTT9tuc/hSrtw6uzJOvgRr2a9jyxxT1ely+B+xFAmJKVSTbpM/CuL7qxO8w=="
                    crossorigin="anonymous" />
            `
    } 

    constructor(optional_attrib_dict, mandatory_attrib_list){
        super(); 
        // console.log('constructor for wc_master....')
        
        // this.check_required_fields( this.getAttributeNames(), optional_attrib_dict, mandatory_attrib_list, this.constructor.name );   //check that mandatory fields given
        // this.capture_defaults( optional_attrib_dict, mandatory_attrib_list );   //Save default param values to _def;
        
        this.field_checker = new FieldChecker( optional_attrib_dict, mandatory_attrib_list, new FieldChecker_Extractor_WC(this) )
        this.field_checker.check_required_fields();   //check that mandatory fields given
        this._orig_inp = this.field_checker.get_dict(); 
        this._inp = Object.assign({}, this._orig_inp ); 
 

        this._debug = false 
        

        this.template = document.createElement('template');
        this.template.innerHTML = this.define_template(); 
        this.init_template( this.template );
        this.attachShadow({ mode: 'open' }); 
        this.shadowRoot.appendChild( this.template.content.cloneNode(true)); 
    }

    
    convert_field(field_name, value){
        return this.field_checker.convert_field( field_name, value )
    }

    //************************************************************************************
    //Setup the defaults and events
    connectedCallback( ){      
        this.shadowRoot.querySelectorAll('#si_field').forEach(item =>{ 
            item.addEventListener( 'change',  (event)=> this.field_event_dispatch(event, 'change') );
            item.addEventListener( 'click',  (event)=> this.field_event_dispatch(event, 'click') );
        });

        this.log('initing components')
        this.init_component();
 
    } 

    init_component(){
        throw(`init_component from ${this.constructor.name} not defined `);
        //do nothing, to be overridden
    }

    

    //************************************************************************************
    //Update all the deafult values from _def field
    init_template(template_name){ 
        for( var key in this._orig_inp ){ 
            template_name.innerHTML = template_name.innerHTML.replaceAll( `[placeholder::${key}]` , this._orig_inp[key]);
        } 
    }

    

    //************************************************************************************
    //Log out to console
    parse_json(str){
        // C_UTIL.log( message, this._debug, 3);
        var local_str =   str.replace(/,\s*\}*$/, "\}");
        return JSON.parse( local_str );
    }


    //************************************************************************************
    //Send events
    field_event_dispatch(e, event_type){ 
        // console.log('dispatching.. ' + event_type )
        var value = this.shadowRoot.getElementById('si_field').value;
        const event = new CustomEvent( event_type, { detail: {this:this, elt:e.path[0], value:value  }});
        this.dispatchEvent(event , { bubbles:true, component:true} ); 
    }

    //************************************************************************************
    //Send events
    trigger_custom_event(data, event_type){ 
        console.log('trigger.. ' + event_type )
        var value = this.shadowRoot.getElementById('si_field').value;
        const event = new CustomEvent( event_type, { detail: {this:this, data:data, value:value  }});
        this.dispatchEvent(event , { bubbles:true, component:true } ); 
    }




    is_debug(){ return false; } 
    //************************************************************************************
    //Log out to console
    log(message){ C_UTIL.log( message, this.is_debug(), 3) }

    //************************************************************************************
    //Log out to console
    log_obj(obj){
        this.log( JSON.stringify( obj) );
    }
}


// module.exports = WCMaster;
// }


// //************************************************************************************
    // capture_defaults( optional_attrib_dict, mandatory_attrib_list ){
    //     var ref_this = this;
    //     ref_this._orig_inp = {}
    //     var field_name = null

    //     for( var key in optional_attrib_dict ){
    //         field_name = ref_this._get_input_field(key)
    //         ref_this._orig_inp[field_name] =    ref_this._get_input_value(key, ref_this.getAttribute( field_name )) || ref_this._get_input_value(key, optional_attrib_dict[ key ])

    //         ref_this.log( `key = ${key}:: fieldname = ${field_name} ==> ${ ref_this._orig_inp[field_name] } ## ${ref_this._get_input_value(key, optional_attrib_dict[ key ])}`)

    //         // if( field_name =='header_on'){ debugger; }
    //         // ref_this._orig_inp[field_name] =   ref_this.getAttribute( field_name ) || optional_attrib_dict[ field_name ]
    //     }

    //     if( mandatory_attrib_list){
    //         mandatory_attrib_list.forEach( function(item){
    //             field_name = ref_this._get_input_field(item) 
    //             ref_this._orig_inp[field_name] =    ref_this._get_input_value(item, ref_this.getAttribute( field_name )) || ""
    //         });    
    //     }
    //     // debugger;
    //     ref_this._inp = Object.assign({}, ref_this._orig_inp ); 
        
         
    // }


    // _get_input_field(field){
    //     return field.split("=")[0]
    // }

    // //***********************************************************************************************
    // //Get the input value and convert to specified type
    // _get_input_value(field, orig_value){
    //     var token = field.split("=")
    //     var field_name = token[0]
    //     var field_type = token[1]
    //     var ret_value = orig_value;

    //     // if( field_name =='header_on'){ debugger; }
    //     switch(field_type){
    //         case 'bool': 
    //             ret_value = ( orig_value == 'true' ||orig_value == true ? true :false ); 
    //             break;
    //         case 'int': 
    //             ret_value =  parseInt(orig_value); 
    //             break;
    //         case 'json': 
    //             ret_value =  C_UTIL.is_json( orig_value)

    //             if( !ret_value ){   JSON.parse( orig_value); }  //Have it fail and throw exception
    //             break;
    //     }
    //     return ret_value;
    // }

    // _check_input_field_exists(field_list, target_field_name){
    //     var item_found = false;
    //     var obj_this = this;
    //     field_list.every( function(field){
    //         if( obj_this._get_input_field(field) == target_field_name ){ 
    //             item_found = true; 
    //             return false;   //break the loop
    //         }
    //         return true;        //continue with looping
    //     });
    //     return item_found;
    // }
    // //************************************************************************************
    // //check the attributes that are passed in the web component
    // check_required_fields(data_list, optional_fields_dict, required_field_list, field_name){ 
    //     var invalid_list = [];
    //     var missing_list = []
    //     var obj_this = this;
    //     var optional_fieldname_list = Object.keys(optional_fields_dict)

    //     if(optional_fieldname_list){
    //         data_list.forEach( function(item){
    //             if( ! obj_this._check_input_field_exists(optional_fieldname_list, item) ) { 
    //                 invalid_list.push( item ) 
    //             }
    //         }); 
    //     }
        
    //     if( data_list){ 
    //         required_field_list.forEach( function(attrib_item ){ 
    //             if( ! obj_this._check_input_field_exists(data_list, obj_this._get_input_field(attrib_item)) ){ 
    //                 missing_list.push(attrib_item )
    //             }
    //         });
    //     }
    //     if( missing_list.length>0){ throw `Missing required fields for ${field_name} : ${missing_list.join(",")} and/or Invalid fields: ${invalid_list.join(",")}` }
    // }