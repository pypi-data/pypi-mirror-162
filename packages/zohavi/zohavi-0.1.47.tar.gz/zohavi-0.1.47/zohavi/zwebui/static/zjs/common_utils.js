var imported = document.createElement('script');
imported.src = '//cdn.jsdelivr.net/npm/sweetalert2@11';
document.head.appendChild(imported);





  export class C_AJAX{


    // static x_call_json(url, dict_data, updating_message, success_message, fail_message, success_func=null, fail_func=null, debug=false){ 
    //     if(debug){ console.log("calling :"+ url + " with data [" + JSON.stringify( dict_data )  + "]") }
    //     C_AJAX._call( url, 'json', JSON.stringify( dict_data ), updating_message, success_message, fail_message, success_func , fail_func , debug )
    // }

    // static x_call_dict(url, dict_data, updating_message, success_message, fail_message, success_func=null, fail_func=null, debug=false){ 
    //     console.log('hello world:' + debug)
    //     if(debug){ console.log("calling :"+ url + " with data [" + JSON.stringify( dict_data )  + "]")}
    //     C_AJAX._call( url, 'dict', dict_data, updating_message, success_message, fail_message, success_func , fail_func , debug )
    // }

    // static _x_call(url,content_type, data, updating_message, success_message, fail_message, success_func=null, fail_func=null, debug=false){ 
    //     var data_content_type = 'application/x-www-form-urlencoded; charset=UTF-8'
    //     if( content_type =='json' ){ data_content_type = "application/json" }
    //     // if( updating_message) { G_Modal.modal_updating_status_show(updating_message); }
    //     $.ajax({
    //               url: url , 
    //               // data: {'data': JSON.stringify( dict_data ) },
    //               data:  data ,
    //               type: 'POST',
    //               contentType: data_content_type,
    //               processData: false,
    //               success: function(response) {  
    //                 if(debug){ console.log("Ret data:", response);   }
    //                 // if( success_message) { G_Modal.modal_updating_status_complete(true,   success_message); }
    //                 if(success_func){ success_func(response) }
    //               },
    //               error: function(response) { 
    //                 // if( fail_message) { G_Modal.modal_updating_status_complete(false , fail_message); }
    //                 if(debug){ console.log("Ret error:", response);   } 
    //                 if(fail_func){ fail_func(response) } 
    //               }
    //     });
    // }

    static ajax_post(url, dict_data, success_func=null, fail_func=null, debug=false){ 
            var this_ref = this
            // console.log( 'hello world' );
            var json_data = JSON.stringify( dict_data ) 
            
            console.log( 'submitt to url : ' + url+ '::' + JSON.stringify( json_data ) );
            fetch(  url , { 
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body:  json_data
            })
            .then(function(response){    
                if(response.ok){ return response.json(); }
                else{
                  return response.json().then( response => { 
                    let err = Error( response.error  );
                    err.respose_obj = response
                    throw err
                  } ); 
                }
                
            }).then(function( data ){  
              if( success_func){   
                try{
                   success_func( data );
                }catch( error){
                  // debugger;
                  console.log( `Error in succ func: ${ error.message}` ) ;
                } 
              }  
            }).catch( function(error_data){ 
              console.log('error!!!')
              if( fail_func){  fail_func(error_data.respose_obj); }
            });
               
        }
}


export class C_UI{
  
  //************************************************************************************
  //scroll to top of a field
  static scroll_to_field( selector_field_top, selector_focus_field){
      $('html, body').animate({scrollTop:  $(selector_field_top ).offset().top - $('.pc-header').height() });
      $().focus( selector_focus_field );
  }
  
  //************************************************************************************
  //scroll to top of a field
  static get_validated_wc_form_data( selector_search_field){
    var data = []

    var validation_ok = true; 
    var elt_list = document.querySelectorAll( selector_search_field );

    if( elt_list && elt_list.length > 0 ){
      elt_list.forEach( function( element, index){ 
        var result = element.validate();
        validation_ok = validation_ok & result;
        data.push( element.get_submit_data()  )
      });
  
      console.log( `validation complete - ${validation_ok}` );
      console.log( data );
    }else{
      console.warn( `Could not find elements with querySelector for [${selector_search_field}] to validate form data`)
    }
    

    if(validation_ok){ return data; }
    return null;
  }

  //************************************************************************************
  //scroll to top of a field
  static popup_success(message){
    Swal.fire({ icon: 'success', title: message , showConfirmButton: false, timer: 1500 },
            function (isConfirm) {
                if (isConfirm) {
                    return true;
                }
            }  );
  }

  //************************************************************************************
  //scroll to top of a field
  static popup_fail(message){
    Swal.fire({ icon: 'error', title: message , showConfirmButton: false, timer: 7500 },
            function (isConfirm) {
                if (isConfirm) {
                    return true;
                }
            }  );
  }

  //************************************************************************************
  // use the schema to update fields on to screen
  static map_db_data_to_screen_fields_single( class_selector, schema_dict, db_data){ 


      document.querySelectorAll( class_selector ).forEach( function( element, index){ 
        if( schema_dict.hasOwnProperty( element.id ) ){ 
          var schame_field_info = schema_dict[ element.id  ]  
          if( db_data[0].hasOwnProperty( schame_field_info.field_db ) ){ 
            element.value = db_data[0][ schame_field_info.field_db ]
          }else{
            console.log(`cannot find: ${ JSON.stringify( schame_field_info) }`);
          }
        }else{
          console.log(`cannot find sreen field: ${ element.id }`);
        }
      }); 

      
  }



  //************************************************************************************
  // manage tabs and the targets they send to
  static manage_tabs(class_tab_selector){
    //".sck_tab_main_item"
    document.querySelectorAll(class_tab_selector).forEach( function( element, index){
        element.addEventListener('click', function (e) { 
          //go through and remove the active class from all tabs
          e.path[0].closest('.sck_tab_items').childNodes.forEach(function( element, index){
            if( element.nodeName == 'LI' ){  //If this is an element node of a list element
              if (element.classList.contains("is-active")) {
                element.classList.remove("is-active");
                document.querySelector('#' + element.dataset.target).classList.add("is-hidden")
              }
            }
          } );

          // console.log(e.srcElement.nodeName)

          var new_tab_li = e.srcElement.closest('li');
          new_tab_li.classList.add("is-active");
          console.log( new_tab_li )
          document.querySelector('#' + new_tab_li.dataset.target ).classList.remove("is-hidden")
          

        });

      });
  }

  //******************************************************************************************
  //Set visible status
  static set_visible(selector, visible_status ){
    document.querySelectorAll(selector ).forEach( function(element, index){
      if( visible_status){ element.classList.remove('is-invisible');   }
      else{ element.classList.add('is-invisible');  }
    }); 
  }

  //******************************************************************************************
  //Set visible status
  static set_hidden(selector, hidden_status ){
    document.querySelectorAll(selector ).forEach( function(element, index){
      if( hidden_status){ element.classList.remove('is-hidden');   }
      else{ element.classList.add('is-hidden');  }
    }); 
  }

}

export default class  C_UTIL{
  // static _degug_on = false;

  static set_debug(status){
    this._degug_on = status
  }
  static is_str_true(str){
    if( ['true', 'True', 't', 'T'].indexOf(str) >= 0 ){
      return true;
    }
    return false;
  }


  static log(message, debug_on , parent_index = 2){
      if( debug_on ){
          var stk = new Error().stack
          var callee = stk.split("\n")[ parent_index ].trim()
          var tokens = callee.split(" ")
          if( tokens.length >2 ){
              var filename_tokens = tokens[tokens.length-1].split("/") 
              var func = tokens[1]
          }else{
              // debugger;
              var filename_tokens = tokens[1].split("/")  
              var func = ""
          }
          // debugger
          console.log( "%c" + func +  "(" + filename_tokens[ filename_tokens.length -1 ] + ":\n%c" + message , "color:blue", "color:black") ; 
      }
  } 

  static is_json(str) {
    var json_obj = "";
    try {
        json_obj = JSON.parse(str);
    } catch (e) {
        return false;
    }
    return json_obj;
  }

  //************************************************************************************
  static search_list_dict_key_value( dict, key, value){
      var ret_value = null;
      if(!dict){ return ret_value; }

      dict.every( function( elt){
          if( elt[ key ] == value ){ ret_value = elt; return false }
          return true;
      });
      return ret_value;
  }
}

export class C_FRM{
  
  // //************************************************************************************
  // static x_get_form_data_to_json(form_ref){
  //     var unindexed_array = form_ref.serializeArray();
  //     var indexed_array = {};

  //     $.map(unindexed_array, function(n, i){
  //         indexed_array[n['name']] = n['value'];
  //     }); 
  //     return indexed_array;
  // } 

  static get_fields_to_dict(elements, key_field, val_field){
    var dict_form_data = {};

    elements.each( function(index){
        // console.log( 'count:'+index +":"+ this.name  );
        dict_form_data[  this[ key_field]   ] = this[ val_field] ;
    });
    return dict_form_data;
    // console.log( json_form_data );
  }
}