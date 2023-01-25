
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
                case "msgtoolong":
                    errorMessage = "Message too long";
                    break;
                case "nametoolong":
                    errorMessage = "Name too long";
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

var last_id = -1;
const btnLoadmore = document.getElementById('btn-loadmore');
const recentsHolder = document.getElementById('recents-holder');
document.addEventListener("DOMContentLoaded", function() {
    getRecents(-1);
});

btnLoadmore.addEventListener('click', function(e) {
    if(last_id === 0){
        btnLoadmore.disabled = true;
        return
    }else{
        btnLoadmore.disabled = true;
        btnLoadmore.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`;
        getRecents(last_id-1).then(()=>{
            btnLoadmore.disabled = false;
            if(last_id === 0) btnLoadmore.disabled = true;
            btnLoadmore.innerHTML = `Load More`; 
        }).catch(()=>{
            btnLoadmore.disabled = false;
            btnLoadmore.innerHTML = `Load More`; 
        });
    }

});


function getRecents(startID){
    return fetch('/recents?' + new URLSearchParams({startid: startID}), {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then((response)=>{
        console.log(response);
        if(response.ret && "data" in response){
            var data = response.data;
            last_id = data[0][0];
            for(var i = data.length-1; i >= 0; i--){
                var post_str = "Post#"+zeroPad(data[i][0], 5);
                recentsHolder.innerHTML += `<div class="card mb-1">
                    <div class="card-body">
                        <p class="card-text">${data[i][1]}</p>
                    </div>
                    <div class="card-footer">
                        <div class="row">
                            <small class="text-muted text-start col-6">${data[i][2]}</small>
                            <small class="text-muted text-end col-6">${post_str}</small>
                        </div>
                    </div>
                </div>`
            }
        }else if(response.ret && !("data" in response)){
            btnLoadmore.disabled = true;
            btnLoadmore.innerHTML = `Load More`; 
        }else{
            recentAlertMessage(`Error: Failed to load data`, "danger");
        }
    })
    .catch(error => {
        console.log(error);
        recentAlertMessage("Unexpected error occured, could not load data", "danger");
    });
}

const zeroPad = (num, places) => String(num).padStart(places, '0');