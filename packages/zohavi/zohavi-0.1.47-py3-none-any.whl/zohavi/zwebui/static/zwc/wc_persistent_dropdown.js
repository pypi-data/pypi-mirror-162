
(function() {
        const delete_icon = '<i class="fas fa-trash-alt"></i>';
        const template = document.createElement('template');

        template.innerHTML = ` 
            <link rel="stylesheet" href="/webui/static/zcss/common_style.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
            <input type="text" autocomplete="off" list="id_mv_filter_fieldname_list" class="form-control key_form_input" id="id_mv_filter_fieldname">
            <datalist id="id_mv_filter_fieldname_list"> 
            </datalist>  
            <a href="#" class="mr-1 key_select_items_edit" ><i>edit</i></a>

            <!-- Modal -->
             <div class="modal fade key_modal_list_elements text-left" id="id_modal_list_elements" >   
              <div class="modal-dialog modal-dialog-centered modal-sm" role="document"> 
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title" id="exampleModalLabel">Edit elements</h5>
                    <button type="button" class="close key_dialog_close_box" data-dismiss="modal" aria-label="Close">
                      <span aria-hidden="true">&times;</span>
                    </button>
                  </div>
                  <div class="modal-body">
                    <table class="key_display_select_items_table table table-hover table-sm">
                    </table>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-primary key_select_elt_edit_save" >Save</button>
                    <button type="button" class="btn btn-secondary key_select_elt_edit_cancel" data-dismiss="modal">Cancel</button>
                  </div>
                </div>
              </div>
            </div>
        `;

        class WCPersistentDropdown extends HTMLElement { 
            constructor() {
                super();

                this.attachShadow({ mode: 'open' }); 
                this.shadowRoot.appendChild(template.content.cloneNode(true)); 
            }

            get value() {
              return this.getAttribute('value');
            }

            //************************************************************************************
            //Setup the defaults and events
            connectedCallback(){ 
                console.log('started editable persistent dropdown..')
                this._send_data = { 'config_section': this.getAttribute('config_section') , 
                                    'config_area': this.getAttribute('config_area') , 
                                    'config_sub_area': this.getAttribute('config_sub_area') ,
                                    'filter_1':this.getAttribute('filter_1') , 
                                    'filter_2':this.getAttribute('filter_2') }
                this.load_initial_entries();
              
                //on change when a new entry added to main text box
                this.shadowRoot.querySelectorAll('#id_mv_filter_fieldname').forEach(item =>{
                    item.addEventListener( 'change',  () => this.new_entry_in_search_box()  );
                });
    
                //click on edit the list of items in dropdown to open up modal dialogbox
                this.shadowRoot.querySelectorAll('.key_select_items_edit').forEach(item =>{
                    item.addEventListener( 'click',  () => this.open_modal_box()  );
                });

                //close the modal dialbo by clicking on save
                this.shadowRoot.querySelectorAll('.key_select_elt_edit_save').forEach(item =>{
                    item.addEventListener( 'click',  () => this.save_changes()  );
                });

                //close the modal dialbo by clicking on cancel
                this.shadowRoot.querySelectorAll('.key_select_elt_edit_cancel').forEach(item =>{
                    item.addEventListener( 'click',  () => this.close_modal_box()  );
                });

                //close the modal dialbo by clicking on close button at top right
                this.shadowRoot.querySelectorAll('.key_dialog_close_box').forEach(item =>{
                    item.addEventListener( 'click',  () => this.close_modal_box()  );
                });

                
                this._list_items = []  
            }

            //************************************************************************************
            // Load initial entries
            load_initial_entries(){  

                //Load the records from database
                var obj_this = this;    //keep reference of class, below will have callback where original this will be lost
                fetch(obj_this.getAttribute('ajax_url_get'), {
                  method: 'POST',  
                  body: JSON.stringify( obj_this._send_data ) ,
                  headers:new Headers({'content-type': 'application/json'})
                }).then(res => res.json())
                .then(function(response){
                    //save the records to the dropdown list
                    var option_item_str = ''
                    response['data']['value'].forEach(function(item, index){
                        if(item){
                            obj_this._list_items.push( item );  //keep local copy.
                            option_item_str = option_item_str + '<option value="'+  item + '"></option>' 
                        } 
                    });
                    obj_this.shadowRoot.querySelector('#id_mv_filter_fieldname_list').innerHTML = option_item_str;
                })
                .catch(error => console.error('Error:', error));
            }
            

            //************************************************************************************
            //A new value was typed into the dropdown input box
            new_entry_in_search_box  ( ){ 
                var obj_this = this;
                var new_item = obj_this.shadowRoot.querySelector('#id_mv_filter_fieldname').value ; //get new entry value
                obj_this.setAttribute('value', new_item);

                if( ! this._list_items.includes( new_item) ){
                    //add the item to the dropdown list 
                    var new_option_item_html = '<option value="'+new_item + '"></option>';  
                    var option_item_str = obj_this.shadowRoot.querySelector('#id_mv_filter_fieldname_list').innerHTML + new_option_item_html
                    obj_this.shadowRoot.querySelector('#id_mv_filter_fieldname_list').innerHTML = option_item_str 

                    //Update this to the database
                    this._list_items.push(new_item );   //Keep local array updated
                    obj_this._send_data['value'] = this._list_items
                    fetch(obj_this.getAttribute('ajax_url_update'), {
                      method: 'POST',  
                      body:  JSON.stringify( obj_this._send_data ) ,
                      headers:new Headers({'content-type': 'application/json'})
                    });  
                }
            };


            //************************************************************************************
            //show list out the elements which are editable
            render_list_of_items(remove_item){
                var table_obj = this.shadowRoot.querySelector(".key_display_select_items_table");   //get short reference only
                table_obj.innerHTML = "";       //clear table.
                var table_row_str = ""
 
                if( remove_item){       //iten to be removed  - this means the delete row item was clicked
                    this._list_items.splice(remove_item, 1);    //arg of '1' means only one item to be removevd
                } 

                this._list_items.forEach( function(value, index, array){ //render the table - below items are referred to in 'process_row_item_click' function
                    table_row_str = table_row_str + 
                                        '<tr class="key_select_items_table_row">' +
                                                    '<td class="key_select_item_table_item_value">' +  value + '</td>' +
                                                    '<td> <a href="#" class="key_remove_select_elt" id="item_'+ index + '">' +
                                                       delete_icon + '</a></td>' +
                                              '</tr>';
                });
                table_obj.innerHTML = table_row_str;
            }

            //************************************************************************************
            //show the popup and list out the elements which are editable
            open_modal_box(){ 
                //Show the modal dialog box and then grey out everything else.
                this.shadowRoot.querySelector("#id_modal_list_elements").style.display = "block";
                this.shadowRoot.querySelector("#id_modal_list_elements").style.backgroundColor = "rgba(0,0,0,0.4)" 
                this.shadowRoot.querySelector("#id_modal_list_elements").classList.add('show') 
                
                //Get a reference to the the render_list_of_items function with the linkage to the current "this" object which refers
                //to the whole class.
                this._fn_render_list_of_items = this.render_list_of_items.bind(this); 
                this._fn_render_list_of_items(null);    //call function to list out items, but dont remove any items (hence null)
                this._fn_process_row_item_click = this.process_row_item_click.bind(this);    
                document.addEventListener('click', this._fn_process_row_item_click);   //add the event to measure any clikc.
            }

            //*********************************************************************************
            //A record in dialog box was clicked to be removed.
            process_row_item_click(e){
                if( e.path[1].innerHTML == delete_icon){
                        //e.path[0] == the clicked element html tag.  e.path[1] contains the parent of that item.
                        //The HTML of the row item is:
                        //<td> <a href="#" class="key_remove_select_elt" id="item_0"><i class="fas fa-trash-alt"></i></a></td>
                        //Hence, e.path[0] will be <i class="fas fa-trash-alt"></i>
                        //e.path[1] == <a href="#" class="key_remove_select_elt" id="item_0">
                        //Notice, the id of that tag is "item_0", so from the 5th character we get the index number.  That is passed
                        //to the function to repaint all the records on the table.
                        this._fn_render_list_of_items( e.path[1].id.substr(5) ); 
                 }
            }

            //*********************************************************************************
            //Save changes from the dialog box to remove any items
            save_changes(){ 
                //Send updates to database
                this._send_data['value'] = this._list_items     //get the full dataset to send
                fetch(this.getAttribute('ajax_url_update'), {
                  method: 'POST',  
                  body:  JSON.stringify( this._send_data ) ,
                  headers:new Headers({'content-type': 'application/json'})
                }); 

                this.close_modal_box();     

                //Update the options list with the new entries
                var option_item_str = '';
                this._list_items.forEach( function(value, index, array){
                    option_item_str = option_item_str + '<option value="'+  value + '"></option>' 
                }); 
                this.shadowRoot.querySelector('#id_mv_filter_fieldname_list').innerHTML = option_item_str;
            }

            //*********************************************************************************
            //Close the modal box - data will be still there.  It'll be reset on open.
            close_modal_box(  ){ 
                this.shadowRoot.querySelector("#id_modal_list_elements").style.display = "none"; 
            }
 
        }

      window.customElements.define('wc-persistent-dropdown', WCPersistentDropdown);
})();