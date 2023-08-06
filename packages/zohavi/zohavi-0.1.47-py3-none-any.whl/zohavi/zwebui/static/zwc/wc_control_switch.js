(function() {
        const template = document.createElement('template');

        template.innerHTML = ` 
        <style>
            .text-success{ color: #17C666 !important; font-size: 1.3em;  }
            .text-danger{ color: #EA4D4D !important; font-size: 1.3em;  }
        </style>

        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">

          <i class="fas fa-toggle-on text-success key_process_status_cell key_status_on d-none   " ></i> 
          <i class="fas fa-toggle-off text-danger key_process_status_cell key_status_off d-none  "  '></i> 
          <i class="fas fa-spinner   fa-spin   key_status_running  d-none " ></i>  
          <span class="text-muted" id="wc_control_switch_status"></span>
        `;

        class WCControlSwitch extends HTMLElement { 
            constructor() {
                  super();

                  this.attachShadow({ mode: 'open' }); 
                  this.shadowRoot.appendChild(template.content.cloneNode(true)); 
            }

            //************************************************************************************
            //Setup the defaults and events
            connectedCallback(){ 
                this.set_default_labels( this.getAttribute('labels') );
                this.set_default_status( this.getAttribute('default') );
                this.render_control_status();
                //Go through all the events
                this.shadowRoot.querySelectorAll('.key_process_status_cell').forEach(item =>{
                    item.addEventListener( 'click',  ()=> this.clickEvent() );
                });
            }

            // //************************************************************************************
            // //set the current value
            // get value() { 
            //     return this._status ;
            // }

            //************************************************************************************
            //set the current value
            set value(new_status) {
                this.render_control_status( new_status );
                this.setAttribute('value', new_status); 
            }


            // //************************************************************************************
            // //set the current value
            // get ajax_data() { 
            //     return this.getAttribute('ajax_data' ); 
            // }

            // //************************************************************************************
            // //set the current value
            // set ajax_data(new_data) { 
            //     this.setAttribute('ajax_data', new_data); 
            // }


            //************************************************************************************
            //set default labels when running
            set_default_labels(attribute_value){
                var default_label = ";;";
                this.label_list = default_label.split(";");
                if( attribute_value ){
                    this.label_list = attribute_value.split(";");
                }
                if( this.label_list.length != 3){
                    throw 'Incorrect number of label elements [' + str(attribute_value) + '] set for tag: ' + this.tagName + '.  Need to have 3 elements separated by ";"';
                }
                this._label_on      = this.label_list[0];
                this._label_running = this.label_list[1];
                this._label_off     = this.label_list[2]; 
            }


            //************************************************************************************
            //Render switch
            render_control_status(new_status){
                if( new_status ){
                    this._status = new_status;
                }
                // debugger;
                //clear all statuses
                this.shadowRoot.querySelector('.key_status_on').style.display = 'none'; 
                this.shadowRoot.querySelector('.key_status_off').style.display = 'none'; 
                this.shadowRoot.querySelector('.key_status_running').style.display = 'none'; 
                this.shadowRoot.querySelector('#wc_control_switch_status').innerHTML = ''; 
                
                switch(this._status){
                    case 'on'   : 
                        this.shadowRoot.querySelector('.key_status_on').style.display = 'inline-block'; 
                        this.shadowRoot.querySelector('#wc_control_switch_status').innerHTML = this._label_on; 
                        break;
                    case 'running'   : 
                        this.shadowRoot.querySelector('.key_status_running').style.display = 'inline-block'; 
                        this.shadowRoot.querySelector('#wc_control_switch_status').innerHTML = this._label_running; 
                        break;
                    case 'off'   : 
                        this.shadowRoot.querySelector('.key_status_off').style.display = 'inline-block'; 
                        this.shadowRoot.querySelector('#wc_control_switch_status').innerHTML = this._label_off; 
                        break;
                    default:
                        throw 'Invalid status in function [render_control_status] : ' + this._status;

                }
            }

            //************************************************************************************
            //set default status
            set_default_status(attribute_value){
                this._status = 'off';    //assume default status is 'on'
                if( attribute_value ){
                    this._status = attribute_value;
                    if( ['on', 'running', 'off'].indexOf( attribute_value ) <0 ){
                        throw 'Incorrect status [' + attribute_value + '] set for tag: ' + this.tagName;
                    }
                } 
            }
            
            //************************************************************************************
            //Click event
            clickEvent(){ 
                var url_query = '';
                var url_data = {};
                var new_status; 
                var old_status = this._status;
                switch(this._status){
                    case 'on'       : 
                        url_query = this.getAttribute('ajax_url_stop'); 
                        new_status = 'off'; 
                        url_data = JSON.parse( this.getAttribute('ajax_data') ); 
                        break;
                    case 'running'  : throw 'still running' ;  break;
                    case 'off'      : 
                        url_query = this.getAttribute('ajax_url_start'); 
                        url_data = JSON.parse( this.getAttribute('ajax_data') ); 
                        new_status = 'on';  
                        break;
                    default         : throw 'incorrect status' ;  break;
                } 
 
                this.render_control_status('running');

                var obj_this = this;    //save the reference to global object - ajax will have own 'this' context

                $.ajax({
                            url: url_query,  
                            data: url_data,
                            type: 'POST',
                            success: function(response) { 
                                console.log(response); 
                                obj_this.render_control_status(new_status);
                                console.log('new status:', new_status)
                                obj_this.dispatchEvent(new CustomEvent('wc_control_switch_change_success', { detail: {'response':response, 'obj_this':obj_this, 'new_status': new_status }} ));
                            },
                            error: function(error) {        
                                Swal.fire('Error in process', '', 'error'); 
                                obj_this.render_control_status( old_status );
                                obj_this.dispatchEvent(new CustomEvent('wc_control_switch_change_fail', { detail: {'response':response, 'obj_this':obj_this, 'error': error }} ));
                            }
                    });  
            } 
 
        }

      window.customElements.define('wc-control-switch', WCControlSwitch);
})();