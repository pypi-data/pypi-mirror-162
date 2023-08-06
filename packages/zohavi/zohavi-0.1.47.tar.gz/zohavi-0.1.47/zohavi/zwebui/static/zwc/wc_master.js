
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
        this.process_attributes(optional_attrib_dict, mandatory_attrib_list)

        

        this._debug = false 
        

        this.template = document.createElement('template');
        this.template.innerHTML = this.define_template(); 
        this.init_template( this.template );
        this.attachShadow({ mode: 'open' }); 
        this.shadowRoot.appendChild( this.template.content.cloneNode(true)); 
    }

    //************************************************************************************
    process_attributes(optional_attrib_dict, mandatory_attrib_list){
        this.field_checker = new FieldChecker( optional_attrib_dict, mandatory_attrib_list, new FieldChecker_Extractor_WC(this) )
        this.field_checker.check_required_fields();   //check that mandatory fields given

        this._orig_inp = this.field_checker.get_dict(); 
        this._inp = Object.assign({}, this._orig_inp ); 
        
        // this.validate_attributes()  //furtehr validation on fields
    }
    
    //************************************************************************************
    convert_field(field_name, value){
        return this.field_checker.convert_field( field_name, value )
    }

    //************************************************************************************
    //Add validation
    // validate_attributes(){
    // }

    //************************************************************************************
    //Setup the defaults and events
    connectedCallback( ){      
        this.shadowRoot.querySelectorAll('#si_field').forEach(item =>{ 
            item.addEventListener( 'change',  (event)=> this.field_event_dispatch(event, 'change') );
            item.addEventListener( 'click',  (event)=> this.field_event_dispatch(event, 'click') );
        });

        // this.log('initing components')
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

 