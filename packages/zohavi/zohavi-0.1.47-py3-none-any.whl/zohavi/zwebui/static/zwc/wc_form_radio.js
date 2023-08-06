
    import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
    import WCFormControl from  "/webui/static/zwc/wc_form_main.js" 
 

    // var wc_form_ref_instance = customElements.get('wc-form-main');
    

    export default class WCRadioButton extends WCFormControl { 
        define_template(){
            return  ` 
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.2/css/all.min.css"
                integrity="sha512-HK5fgLBL+xu6dm/Ii3z4xhlSUyZgTT9tuc/hSrtw6uzJOvgRr2a9jyxxT1ely+B+xFAmJKVSTbpM/CuL7qxO8w=="
                crossorigin="anonymous" />
    
            <div  class="field">
                <label class="label">[placeholder::label]</label>
                <div id="si_field" class="control">
                    <!--
                
                        <label class="radio">
                            <input type="radio" class="sck_field" name="[placeholder::name]">
                            Yes
                        </label>
                    <label class="radio">
                        <input type="radio" class="sck_field" name="[placeholder::name]" checked>
                        No
                    </label>
                    -->
                </div>
                <p id="si_help_message" class="help is-invisible">.</p>  
            </div>
                
            `;
        }

        constructor(){
            super( {"label":"", "radio_list=json":"", "render":"horizontal"}, ["id"]); 

            // super();  
            
            // this.template = document.createElement('template');
            // this.template.innerHTML = this.define_template(); 
            
            // this.init_template( this.template );

            // this.attachShadow({ mode: 'open' }); 
            // this.shadowRoot.appendChild( this.template.content.cloneNode(true)); 

            // this.init_radio_defaults();
            // this.check_attributes( [  "label_list"], ["id"]);
        } 
    
        //************************************************************************************
        //Setup the defaults and events
        connectedCallback(){     
             super.connectedCallback(); 
        }  

        //************************************************************************************
        //Setup radio button values
        init_component(){
            var this_obj = this;
            var $radio_group= this_obj.shadowRoot.getElementById('si_field'); 
            var radio_default =  this_obj._inp.value ; 

            // this.log( radio_config )
            if( ! this_obj._inp.radio_list ){ return }
            // debugger;
            var radio_item_str='';
            this_obj._inp.radio_list.forEach( function(radio_item, index){ 
                radio_item_str +=   `<label class="radio" ${radio_item["disabled"]=="true"?"disabled":""}>
                                        <input type="radio" name="si_radio_group" class="sck_field"  
                                        ${radio_item["value"]?'value="' + radio_item["value"] +'"':""} `

                if( radio_item["checked"]=="true" || radio_default == radio_item["value"] ){
                    radio_item_str +=  "checked"
                }
                radio_item_str +=   `${radio_item["disabled"]=="true"?"disabled":""} 
                                        >
                                        ${radio_item["label"]}
                                    </label>`
                if( this_obj._inp.render == "vertical"){
                    radio_item_str += '<br>'
                }
            });
            $radio_group.innerHTML = radio_item_str;
        }

        //************************************************************************
        //Over ride validation function from parent to do nothing
        evt_validate_on_value_change(e){
            return;
        }

        get value(){
            var value = undefined;
            this.shadowRoot.querySelectorAll(".sck_field").forEach( item => {
                if( item.checked ){ value = item.value;}
            }); 
            return value;
        }

        set value(new_value ){ 
            this.shadowRoot.querySelectorAll(".sck_field").forEach( item => {
                if( item.value == new_value ){ 
                    item.checked = true 
                }else{
                    item.checked = false
                }
            });  
            // this.shadowRoot.getElementById('si_field').checked = new_value;            
            // this.shadowRoot.getElementById('si_field').setAttribute("checked", new_value); 
            // this.setAttribute("value", new_value)
            this._inp.value = new_value
        }
        // value(){
        //     var value = undefined;
        //     this.shadowRoot.querySelectorAll(".sck_field").forEach( item => {
        //         if( item.checked ){ value = item.value;}
        //     });
        //     // console.log('nothing checked'); 
        //     return value;
        // }
        //************************************************************************
        //Over ride validation function to dispatch event
        evt_dispatch_change(e){
            // console.log('child over ride');
            // var value = '';
            // this.shadowRoot.querySelectorAll(".sck_field").forEach( function(item){
            //     if( item.checked ){ value = item.value;}
            // });
            const event = new CustomEvent('change', { detail: {this:this,value:this.value  }});
            this.dispatchEvent(event , { bubbles:true, component:true} );
            // debugger;
        }


         
    }

     
    window.customElements.define('wc-radio-button', WCRadioButton); 
