// (function() {

// console.log('tryingt to load : ' + ( typeof validation_helper_js_loaded) );
//  if( typeof validation_helper_js_loaded === 'undefined'){
    
    // console.log('loading now now.. ');
 
     export default class ValidationHelper {
        // DEBUG = true

        static log(message, debug){
            if( true ){  console.log(message) }
        }

        static validate(value, requirement_list, debug = false){ 
            // debugger;
            ValidationHelper.log('VALIDATING: [' + value + ']  [' + JSON.stringify( requirement_list) + ']') 
            if(!requirement_list){ return true; }   //no validation if no validation provided  

            // var req_list_obj = JSON.parse( requirement_list )
            var req_list_obj =  requirement_list  
            var validation_success = true;

            if( 'optional' in req_list_obj && req_list_obj['optional'] && value =="" ) return true //if optional and blank, skip
            if( 'required' in req_list_obj && !req_list_obj['required'] && value =="" ) return true //if optional and blank, skip

            // debugger;

            for (var rule_name of Object.keys(req_list_obj) ) {
                //loop through each input and check the validation 
                if(  rule_name != "optional"){ 
                    var param = req_list_obj[ rule_name ];         
                    ValidationHelper.log( `checking: [${rule_name}] : [${param}]=?=[${value}]`, debug)
                    // debugger; 
                    if(  Object.getOwnPropertyNames(ValidationHelper).includes( "validate_"+rule_name  ) ){  //see if method existls
                        if( ! ValidationHelper["validate_"+rule_name](  value , param) ){ 
                            validation_success = false;
                           ValidationHelper.log( ' failed 1', debug)
                            return false; //return on first failure
                        }
                    }else{
                        throw `No such validation rules called ${rule_name} nor validation function ${"validate_"+rule_name}`
                    }
                    
                } 
            }
            ValidationHelper.log( ' ret 1:'+ validation_success, debug)
                         
            return validation_success
        }

        static validate_helper_message(requirement_list){ 
            if(!requirement_list){ return ""; }
            // var req_list_obj = JSON.parse( requirement_list )
            var req_list_obj =   requirement_list  
            var message_str = "";
            for (var rule_name of Object.keys(req_list_obj) ) {
                //loop through each input and check the validation 
                if(  rule_name != "optional"){ 
                    var param = req_list_obj[ rule_name ];    
                    message_str += ValidationHelper["validate_"+rule_name](  null , param, true)  ;

                } 
            }
            return message_str;
        }
    





        //**********************************************************
        // Static (to enable WCFormControl[""] access ) to match RE
        static validate_is_varaible_with_min_len(input_val, len, get_message ){
            if( get_message){
                return `Must be at least ${len} characters long.`;
            }
 
            var re = new RegExp( /^[a-zA-Z]+[a-zA-Z0-9_]+$/i )
            return re.test(input_val) & (input_val.length >= parseInt(len))
        }

        //**********************************************************
        // Static (to enable WCFormControl[""] access ) to match RE
        static validate_match_pattern(input_val, param, get_message){
            if( get_message){
                return `Must match pattern ${param}.`;
            }
            return new RegExp(param).test( input_val) ;
        }
        //**********************************************************
        // Static (to enable WCFormControl[""] access ) to match RE
        static validate_is_unix_path(input_val, param=null, get_message){
            if( get_message){
                return `Must be a valid unix style path with a trailing foward slash:'/' `;
            }

            var re = new RegExp( /^(?:\/?[_\.a-zA-Z0-9]+)+\/$/i )
            // debugger;
            return re.test(input_val)
        }
        
        //**********************************************************
        // Static (to enable WCFormControl[""] access ) to match RE
        static validate_is_unix_file(input_val, param=null,get_message){
            if( get_message){
                return `Must be a valid unix style file with an optional path`;
            }

            var re = new RegExp( /^(?:(?:\/?[_\.a-zA-Z0-9]+)+\/)?[_\.a-zA-Z0-9]+$/i )
            return re.test(input_val)
        }

        //**********************************************************
        // check if email or not
        static validate_is_email(input_val, param=null,get_message){
            if( get_message){
                return `Must be a valid email address`;
            }

            return new RegExp(
              /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
            ).test( input_val) ;
        }
        
        //**********************************************************
        // check if url or not
        static validate_is_url(input_val, param=null,get_message){
            if( get_message){
                return `Must be a valid URL path string`;
            }

            var re = new RegExp ( /(https?:\/\/)?[\w\-~]+(\.[\w\-~]+)+(\/[\w\-~]*)*(#[\w\-]*)?(\?.*)?/i );
            return re.test( input_val );
        }

        //**********************************************************
        // check if url or not
        static validate_is_ip(input_val, param=null,get_message){
            if( get_message){
                return `Must be a valid IP address`;
            }

            var re = new RegExp ( /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/i );
            return re.test( input_val );
        }
    
        //**********************************************************
        // check if number is numeric
        static validate_is_numeric(input_val, param=null,get_message){
            if( get_message){
                return `Must be a positive number`;
            }

            return !isNaN( input_val ) && input_val.length > 0; 
        }
    
        //**********************************************************
        // check if number is greater than a min
        static validate_num_gte(input_val, min, get_message){
            if( get_message){
                return `Must be a number which is greater than or equal to ${min}`;
            }

            return ValidationHelper.validate_is_numeric(input_val) && parseInt( input_val ) >= parseInt(min);  
        }
    
        //**********************************************************
        // check if number is less than equal to a mx
        static validate_num_lte(input_val, max, get_message){
            if( get_message){
                return `Must be a number which is less than or equal to ${max}`;
            }

            return ValidationHelper.validate_is_numeric(input_val) && parseInt( input_val ) <= parseInt(max);
        }
    
    
        //**********************************************************
        // check if text is a min len
        static validate_text_min_len(input_val, min, get_message){
            if( get_message){
                return `Must be a text which is at least ${min} characters long`;
            }

            return input_val.length >= parseInt(min);   
        }
    
        static validate_text_max_len(input_val, max, get_message){
            if( get_message){
                return `Must be a text which is at most ${min} characters long`;
            }

            return input_val.length <= parseInt(max);
        }
    
        //**********************************************************
        // check if non-blank
        static validate_required(input_val, param=null,get_message){
            if( get_message){
                return `Cannot be blank`;
            }

            if(!input_val) return false
            return input_val.length && input_val.length > 0;
        }
    }

// }
// })();