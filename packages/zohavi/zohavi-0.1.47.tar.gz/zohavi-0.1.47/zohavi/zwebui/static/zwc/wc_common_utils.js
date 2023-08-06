
//*****************************************************************
// Callbacks from attributes which have a naming convention of
// selector->function name.  e.g. #web_component_id_main->callme
function wcc_attribute_callbacks(this_ref, attribute_name) {

    var attribute_name = this_ref.getAttribute( attribute_name );

    if( attribute_name ){
        var eventList = attribute_name.split( ";");
        eventList.forEach(element => {
            var tokens = element.split( "->");
            var element_ref = this_ref.getRootNode().querySelector( tokens[0] );

            if( element_ref ){
                var function_ref = tokens[1].replace("()", "");
                element_ref [ function_ref ]();  //Call the function!
            }else{
                throw( `Reference not found ${element_ref}`)
            }
            
        });
    }
    
}

//*****************************************************************
// Replace placeholder defaults.
// Traverse through dictionary, and replace all instances with same name
// from the template string
// function wcc_replace_defaults(dict_defaults, template) {

//    for( var key in dict_defaults ){
//        console.log(`key = ${key} -> ${dict_defaults[key]}`)
//    }
// }

function wcc_get_view_width(){
    return Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0); //cross browser get window width
}