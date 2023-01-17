
const responseForm = document.getElementById('responseForm');
const responseResult = document.getElementById('responseResult');

responseForm.addEventListener('submit', function(e) {
    // Prevent default behavior:
    e.preventDefault();

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
    .then(response => response.json())
    .then((response)=>{
        console.log(JSON.stringify(response));
        responseForm.elements["responseText"].value = "";
        responseForm.elements["uname"].value = "";
    })
    .catch(() => getResultSpace.innerHTML = "Server error");

});