import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
import WCMaster from  '/webui/static/zwc/wc_master.js' ;


export default class WCGroup extends WCMaster  { 
    define_template(){
        return super.define_template() + ` 
                <div class="container">

                    <div class="m-3 ${ this._inp['bordered']?'box':''} p-3" id="si_field">
                        <slot>
                        </slot>

                        <div class="align_elt_right"> 
                            <p class="control "> 
                                <wc-button id="sci_site_save" label="[placeholder::label_save]" 
                                    action="[placeholder::action]" 
                                    submit_data_selector="[placeholder::submit_data_selector]" 
                                    popup_message_submit_success="[placeholder::popup_message_submit_success]"
                                    popup_message_submit_fail="[placeholder::popup_message_submit_fail]"
                                ></wc-button> 
                                <wc-button id="sci_site_cancel" label="[placeholder::label_cancel]" active_class="none" > </wc-button>   
                            </p>  
                        </div> 
                    </div>   

                </div>`
    } 

    constructor( ) {
        console.log('construct group')
        
        super( {"bordered=bool":true, "popup_message_submit_success":"Saved", "popup_message_submit_fail":"Save failed",
                "action":"", "submit_data_selector":"","label_cancel":"Cance", "label_save":"Save" },
               ["id"]); 
    }

    connectedCallback(){     
        console.log('construct callback group')
        
        super.connectedCallback(); 
        this.shadowRoot.querySelector('#sci_site_cancel').addEventListener('wc_click', this.evt_cancel_clicked.bind(this) );
        this.shadowRoot.querySelector('#sci_site_save').addEventListener('wc_click', this.evt_save_clicked.bind(this) );
        
    }

    process_attributes(optional_attrib_dict, mandatory_attrib_list){   //override master function
        super.process_attributes(optional_attrib_dict, mandatory_attrib_list);

        //make sure the search is just within this group
        this._inp.submit_data_selector = "#" + this.id + " " + this._inp.submit_data_selector 
    }


    //####################################################################################################################
    evt_cancel_clicked( event ){
        this._init_values.forEach( function(item){
            item.elt.value = item.orig_value;
        });
    }

    //####################################################################################################################
    evt_save_clicked( event ){
        this._init_values.forEach( function(item){
            item.orig_value = item.elt.value;
        } );
    }
     
    //####################################################################################################################
    init_component(){
        console.log('construct init component group')
        this._init_values = []
        this.get_init_values(  this.childNodes );
    }

    //####################################################################################################################
    get_init_values( child_node_list){
        var this_obj = this;

        // debugger;
        // this.childNodes.
        child_node_list.forEach( function(node){
            if( node.childNodes ){
                this_obj.get_init_values(node.childNodes )
            }
            //  node.ELEMENT_NODE  && node.hasAttribute('value')
            // debugger;
            if( node.classList  &&  node.classList.contains(  this_obj._inp.submit_data_selector)  ){ 
                // console.log( `## ${node.id} [${node.tagName}]=> ${node.value}`)
                // debugger;
                this_obj._init_values.push( { "elt":node, "orig_value":node.value })

                // if(node.value){
                //     this_obj._init_values.push( { "elt":node, "orig_value":node.value })
                // }else{
                //     this_obj._init_values.push( { "elt":node, "orig_value":node.getAttribute('value') })
                // }
                
            }
        });

        // this_obj._init_values.forEach( function(node){
        //     console.log( `elt:${node.elt.id} orig_value:${node.orig_value }`  );
        // });


    }
    
    //####################################################################################################################
    hide(){
        this.shadowRoot.querySelector('#si_field').classList.add('is-hidden');
        const event = new CustomEvent('group_disappear', { detail: {this:this  }} );
        this.dispatchEvent(event , { bubbles:true, component:true} ); 
    }

    show(){
        this.shadowRoot.querySelector('#si_field').classList.remove('is-hidden');

        console.log("trigger group appear [0]:" + this.id )
        const event = new CustomEvent('group_appear', { detail: {this:this  }} );
        this.dispatchEvent(event , {bubbles:true,component:true } ); 
        console.log("trigger group appear [1]:" + this.id )
    }
}

window.customElements.define('wc-group', WCGroup); 



