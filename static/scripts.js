
const responseForm = document.getElementById('responseForm');
const responseResult = document.getElementById('responseResult');

var loading = false;

responseForm.addEventListener('submit', function(e) {
    // Prevent default behavior:
    e.preventDefault();

    if(loading){
        alertMessage(`Request already in progress`, "warning");
        return
    }
    loading = true;
    setLoading(true);

    fetch('/', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            "message": responseForm.elements["responseText"].value,
            "name": responseForm.elements["uname"].value
        })
    })
    .then(response =>{
        if(response.status === 429) throw "429error";
        return response.json();
    })
    .then((response)=>{
        if(response.ret){
            alertMessage(`Success! Post Number: ${response.post_num}`, "success");
            responseForm.elements["responseText"].value = "";
            responseForm.elements["uname"].value = "";
        }else{
            errorMessage = "";
            switch(response.error) {
                case "nomsg":
                    errorMessage = "No message was provided";
                    break;
                case "dbwrite":
                    errorMessage = "Failed when writing to database";
                    break;
                case "makeimage":
                    errorMessage = "Failed when making image";
                    break;
                case "uploadfail":
                    errorMessage = "Upload to Instagram Failed";
                    break;
                default:
                    errorMessage = "Unexpected error occured";
            }

            alertMessage(`Error: ${errorMessage}`, "danger");
        }
        loading = false;
        setLoading(false);
    })
    .catch(error => {
        if(error === "429error"){
            alertMessage("Too many requests, try again later", "danger");
        }else{
            alertMessage("Unexpected error occured, try again later", "danger");
        }

        loading = false;
        setLoading(false);
    });
});


const alertHolder = document.getElementById('alert-holder');
const alertMessage = (message, type) => {
    alertHolder.innerHTML += `<div class="alert alert-${type} alert-dismissible" role="alert"> ${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button> </div>`
}

const recentAlertHolder = document.getElementById('recents-alert-holder');
const recentAlertMessage = (message, type) => {
    recentAlertHolder.innerHTML += `<div class="alert alert-${type} alert-dismissible" role="alert"> ${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button> </div>`
}

const btnSubmit = document.getElementById('btn-submit');
const setLoading = (loading) => {
    if(loading){
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Posting...`;
    }else{
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = `Post`; 
    }
}

const recentsHolder = document.getElementById('recents-holder');
document.addEventListener("DOMContentLoaded", function() {

    getRecents(-1);

    
});


function getRecents(startID){
    fetch('/recents?' + new URLSearchParams({startid: startID}), {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then((response)=>{
        if(response.ret){
            var data = response.data;
            for(var i = 0; i < data.length; i++){
                console.log(data[i]);
            }
        }else{
            recentAlertMessage(`Error: Failed to load data`, "danger");
        }
    })
    .catch(error => {
        recentAlertMessage("Unexpected error occured, could not load data : " + error, "danger");
    });
}