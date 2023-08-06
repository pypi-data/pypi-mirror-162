import C_UTIL from '/webui/static/zjs/common_utils.js'; //


class FieldChecker_Extractor{
    constructor(){}
    get_all_fields(){ throw 'abstract';}
    get_field(){ throw 'abstract';}
}

export  class FieldChecker_Extractor_WC extends FieldChecker_Extractor{
    constructor(wc_obj){
        super()
        this._source = wc_obj 
    }
    get_all_fields(){ 
        return this._source.getAttributeNames()
    }

    get_field(field_name){
        return this._source.getAttribute(field_name)
    }

}

export  class FieldChecker_Extractor_Dict extends FieldChecker_Extractor{
	constructor(dict_obj){
        super()
        this._source = dict_obj 
	}
    get_all_fields(){
        return Object.keys(this._source);
    }

    get_field(field_name){
        return this._source[ field_name ]
    }
}

 
//Check if all fields in the given option dictionary entries and required fields are valid.
export  class FieldChecker  { 

    constructor(optional_attrib_dict, mandatory_attrib_list, field_extractor_obj ){


    	// this._opt_dict  = optional_attrib_dict
    	// this._reqd_list = mandatory_attrib_list
        this._field_extractor = field_extractor_obj

        this._opt_dict = this._extract_optional_field_schema( optional_attrib_dict )
        this._reqd_list = this._extract_required_field_schema( mandatory_attrib_list )
    }

    _extract_required_field_schema(field_schema_list){
        var schema_dict = {}
        // debugger;
        for( var field_name_index in field_schema_list){
            var field_schame = this._extract_field_schema_from_field_name( field_schema_list[ field_name_index ]   )
            schema_dict[ field_schame.name ] = field_schame
        }
        // this.log_obj( schema_dict )
        return schema_dict

    }

    _extract_optional_field_schema(field_schema_dict){
        var schema_dict = {}
        // debugger;
        for( var field_name in field_schema_dict){
            var field_schame = this._extract_field_schema_from_field_name( field_name  )
            schema_dict[ field_schame.name ] = field_schame
            schema_dict[ field_schame.name  ].def_value = field_schema_dict[ field_name  ] 
        }
        return schema_dict
        // debugger;
    }

    _extract_field_schema_from_field_name(raw_field_name){
        const field_name_token = raw_field_name.split("=")
        var field_schema = {}
        field_schema.raw_name = raw_field_name
        field_schema.name = field_name_token[0]
        field_schema.type = 'var'
        if( field_name_token.length > 1){
            field_schema.type = field_name_token[1]
        }
        return field_schema;
    }

    //************************************************************************************
    //check the attributes that are passed in the web component
    check_required_fields(){ 
        var invalid_list = [];
        var missing_list = []
        var obj_this = this;
        var actual_field_list = this._field_extractor.get_all_fields()
        var optional_fieldname_list = Object.keys(this._opt_dict)
        // debugger;
        if(optional_fieldname_list){    //Check optional fields
            actual_field_list.forEach( function(item){
                if( ! obj_this._check_input_field_exists(optional_fieldname_list, item) ) { 
                    invalid_list.push( item ) 
                }
            }); 
        }
        
        if( actual_field_list){   //Check mandatory fields
            // this._reqd_list.forEach( function(attrib_item ){ 
            for( var field_name in this._reqd_list ){
                if( ! obj_this._check_input_field_exists(actual_field_list,  field_name ) ){ 
                    missing_list.push(field_name )
                }
            };
        }
        // debugger;
        if( missing_list.length>0){ throw `Missing required fields  [${missing_list.join(",")}] and/or Invalid fields: ${invalid_list.join(",")}` }
        return true;
    }



	//************************************************************************************
    _check_input_field_exists(field_list, target_field_name){
        var item_found = false;
        var obj_this = this;
        field_list.every( function(field){
            if(  field == target_field_name ){ 
                item_found = true; 
                return false;   //break the loop
            }
            return true;        //continue with looping
        });
        return item_found;
    }   



    convert_field(field_name , value){
        if( field_name in this._opt_dict){
            return this._get_input_value(field_name,  this._opt_dict[field_name].type, value )
        }else if( field_name in this._reqd_list){
            return this._get_input_value(field_name, this._reqd_list[field_name].type, value )
        }   
        return value;
        // throw `Field ${field_name} not found in FieldChecker Opt_list [${ JSON.stringify( Object.keys(this._opt_dict) ) }] and required list [${ JSON.stringify( Object.keys(this._reqd_list) ) }]`
    }

    //************************************************************************************
    get_dict(){
        var this_obj = this;
        var data_obj = {}
        // var field_name = null

        // this._opt_dict.forEach( function(field){
        for( var field_name in this._opt_dict){
            // field_name = this_obj._get_input_field(key)
            const field = this._opt_dict[ field_name ]
            const value = this_obj._field_extractor.get_field( field.name ) || field.def_value;
            data_obj[field.name] = this_obj._get_input_value(field.name,  field.type, value)
            this_obj.log( `key = ${field.name}:: fieldname = ${field.raw_name} ==> ${ data_obj[field.name] } `)

            // if( field_name =='header_on'){ debugger; }
            // this_obj._orig_inp[field_name] =   this_obj.getAttribute( field_name ) || optional_attrib_dict[ field_name ]
        };

        if( this._reqd_list){
            // this._reqd_list.forEach( function(field){
            for( var field_name in this._reqd_list){
                // field_name = this_obj._get_input_field(item) 
                const field = this._reqd_list[ field_name ]
                const value = this_obj._field_extractor.get_field( field.name ) || "";
                data_obj[field.name ] =    this_obj._get_input_value(field.name,  field.type, value);
            };    
        }
        // debugger
        return data_obj;
        // debugger;
        // this_obj._inp = Object.assign({}, this_obj._orig_inp ); 
         
    }


    
    //***********************************************************************************************
    //Get the input value and convert to specified type
    _get_input_value(field_name, type, orig_value){
        var ret_value = orig_value;

        // if( field_name =='header_on'){ debugger; }
        switch(type){
            case 'bool': 
                ret_value = ( orig_value == 'True' || orig_value == 'true' ||orig_value == true ? true :false ); 
                break;
            case 'int': 
                ret_value =  parseInt(orig_value); 
                break;
            case 'array': 
                ret_value =  orig_value.split(','); 
                break;
            case 'json': 
                if(orig_value){
                    if( typeof orig_value === "object" ){
                        ret_value = orig_value
                    }else{
                        var temp_value = orig_value.replaceAll('`', '\\"')
                        ret_value = C_UTIL.is_json( temp_value)
                        if( !ret_value ){  
                            try{ //Error message
                                JSON.parse(temp_value) 
                            } catch(e){ 
                                const err_message = e.message 
                                // <<err_message.search("position ")>>
                                // err_message.substr(39)
                                // parseInt( err_message.substr(39) )

                                // temp_value.substr(400,43) + "<<" + temp_value.substr(444,1) + ">>" + temp_value.substr(445,50)
                                

                                throw `Conversion failed: [${err_message} ] of field [${field_name}] to type [${type}] of ${temp_value}`; 
                            }

                            
                        }  
                    }
                }
                
                break;
        }
        return ret_value;
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


    // //************************************************************************************
    // //check the attributes that are passed in the web component
    // xxx_check_required_fields(){ 
    //     var invalid_list = [];
    //     var missing_list = []
    //     var obj_this = this;
    //     var actual_field_list = this._field_extractor.get_all_fields()
    //     var optional_fieldname_list = Object.keys(this._opt_dict)
    //     // debugger;
    //     if(optional_fieldname_list){    //Check optional fields
    //         actual_field_list.forEach( function(item){
    //             if( ! obj_this._check_input_field_exists(optional_fieldname_list, item) ) { 
    //                 invalid_list.push( item ) 
    //             }
    //         }); 
    //     }
        
    //     if( actual_field_list){   //Check mandatory fields
    //         this._reqd_list.forEach( function(attrib_item ){ 
    //             if( ! obj_this._check_input_field_exists(actual_field_list, obj_this._get_input_field(attrib_item)) ){ 
    //                 missing_list.push(attrib_item )
    //             }
    //         });
    //     }
    //     if( missing_list.length>0){ throw `Missing required fields  [${missing_list.join(",")}] and/or Invalid fields: ${invalid_list.join(",")}` }
    //     return true;
    // }

    // //***********************************************************************************************
    // //Get the input value and convert to specified type
    // xxxx_get_input_value(field, orig_value){
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
    //             if(orig_value){
    //                 var temp_value = orig_value.replaceAll('`', '\\"')
    //                 ret_value = C_UTIL.is_json( temp_value)
    //                 if( !ret_value ){  throw `Conversion of field [${field_name}] to type [${field_type}] of ${temp_value} failed`; }  //Have it fail and throw exception                    

    //             }
                
    //             break;
    //     }
    //     return ret_value;
    // }



        // get_field_function( func_name){
    //  this._get_field_fn = func_name;
    // }

    // register_input_data( ){

    // }
    // //************************************************************************************
    // xxxx_check_input_field_exists(field_list, target_field_name){
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
    // _get_input_field(field){
    //     return field.split("=")[0]
    // }



    // //************************************************************************************
    // xxxx_get_dict(){
    //     var this_obj = this;
    //     var data_obj = {}
    //     var field_name = null

    //     for( var key in this._opt_dict ){
    //         field_name = this_obj._get_input_field(key)
    //         data_obj[field_name] =    this_obj._get_input_value(key, this._field_extractor.get_field( field_name )) || this_obj._get_input_value(key, this_obj._opt_dict[ key ])

    //         this_obj.log( `key = ${key}:: fieldname = ${field_name} ==> ${ data_obj[field_name] } ## ${this_obj._get_input_value(key, this_obj._opt_dict[ key ])}`)

    //         // if( field_name =='header_on'){ debugger; }
    //         // this_obj._orig_inp[field_name] =   this_obj.getAttribute( field_name ) || optional_attrib_dict[ field_name ]
    //     }

    //     if( this._reqd_list){
    //         this._reqd_list.forEach( function(item){
    //             field_name = this_obj._get_input_field(item) 
    //             data_obj[field_name] =    this_obj._get_input_value(item, this_obj._field_extractor.get_field( field_name )) || ""
    //         });    
    //     }
    //     return data_obj;
    //     // debugger;
    //     // this_obj._inp = Object.assign({}, this_obj._orig_inp ); 
         
    // }