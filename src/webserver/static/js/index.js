document.addEventListener('DOMContentLoaded', init);

const REQ_TIME = 5000;

function error_code_enum(){
    this.ERR_ZERO = 0;
    this.ERR_ONE = 1;
    this.ERR_TWO = 2;
    this.ERROR_MSG = {
        [this.ERR_ZERO]: "Loading....",
        [this.ERR_ONE]: "waiting",
        [this.ERR_TWO]: "processing"
    }
}

const error_codes = new error_code_enum();

const timer_control = {
    timer: {},
    current_url: ""
};

function init() {
    $('#submit_btn').click(submit_handler);
    $("#spinner").hide();
}

function submit_handler(event) {
    let url = $('#search').val();
    if (url === '' || url.includes(' ')) {
        alert('You need to enter a valid url first');
        return;
    }
    if(timer_control.current_url === url){
        alert('Url is already under processing');
        return;
    }
    $("#url_list").empty();
    $("#spinner").show();
    timer_control.current_url = url;
    timer_control.timer[url] = setInterval(() => submit_url(url), REQ_TIME);
}


async function submit_url(url) {
    try {
        if(timer_control.current_url !== url) { // if the user made a new search before the current url finishes
            clearInterval(timer_control.timer[url]);
            return;
        }

        let form_data = new FormData();
        form_data.append("url", url);
        let response = await fetch('/view', {
            method: "POST",
            body: form_data
        });

        if(!response.ok){
            let err_msg = `Server does not respond with a status 200 message, got status ${response.status} instead\n\n`;
            if(response.headers.get("content-type") === "text/html"){
                let response_text = await response.text();
                err_msg += "server sent back this:\n\n" + response_text;
            }
            throw new Error(err_msg);
        }


        let response_json = await response.json();
        let message = error_codes.ERROR_MSG[response_json.error];
        $("#spinner_text").html(message);
        if(response_json.error !== error_codes.ERR_ZERO){
            return;
        }

        await Promise.all(response_json.generatedUrls.map(async (element)=>{
             let result = await fetch( `//${element}`, {mode: 'no-cors'}).catch( e => {});
             $("#url_list").append(`<li class="list-group-item"><a ${(result) ? "": "class=\"red_link_text\""}  href=${(result) ? "/image/" + element: "#"}>${element}</a></li>`);
        }));

        if(response_json.generatedUrls.length === 0){
             $("#url_list").append(`<li class="list-group-item">Found no squatting urls</li>`);
        }

        $("#spinner").hide();

        timer_control.current_url = "";
        clearInterval(timer_control.timer[url]);
    } catch (err) {
	    clearInterval(timer_control.timer[url]);
	    $("#spinner").hide();
        $("#url_list").append(`<li class="list-group-item">Failed to parse</li>`);
        timer_control.current_url = '';
        alert(`Encounters this error: ${err.message}`);
    }
}
