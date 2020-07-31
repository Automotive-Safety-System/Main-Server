let deleteBtns;
deleteBtns = document.querySelectorAll(".delete-observer");
let observerUsername;
for (let i = 0; i < deleteBtns.length; i++) {
    const deleteBtn = deleteBtns[i];
    deleteBtn.onclick = function(e) {
        console.log("Delete event: ", e);
        const observerDeleteButtonDataId = e.target.dataset.id;
        var pieces = observerDeleteButtonDataId.split("-")
        observerUsername = pieces[pieces.length - 1]
        console.log(observerUsername)
        fetch('/dashboard/observer/'+ observerUsername + '/delete',{
            method: 'DELETE'
        }).then(function() {
            console.log('Parent?', e.target);
            const item = document.getElementById("observer-" + observerUsername)
            item.remove();
        }).catch(function(e) {
            console.error(e);
        });
    };
}

deleteBtns = document.querySelectorAll(".delete-observer-request");
let requestUsername;
for (let i = 0; i < deleteBtns.length; i++) {
    const deleteBtn = deleteBtns[i];
    deleteBtn.onclick = function(e) {
        console.log("Delete event: ", e);
        const observerRequestDeleteButtonDataId = e.target.dataset.id;
        var pieces = observerRequestDeleteButtonDataId.split("-")
        requestUsername = pieces[pieces.length - 1]
        console.log(requestUsername)
        fetch('/dashboard/observer/request/'+ requestUsername + '/delete',{
            method: 'DELETE'
        }).then(function() {
            console.log('Parent?', e.target);
            const item = document.getElementById("observer-request-" + requestUsername)
            item.remove();
        }).catch(function(e) {
            console.error(e);
        });
    };
}

let acceptBtns = document.querySelectorAll(".accept-observer-request");
for (let i = 0; i < acceptBtns.length; i++) {
    const acceptBtn = acceptBtns[i];
    acceptBtn.onclick = function(e) {
        console.log("Accept event: ", e);
        const observerRequestAccpetButtonDataId = e.target.dataset.id;
        var pieces = observerRequestAccpetButtonDataId.split("-")
        requestUsername = pieces[pieces.length - 1]
        console.log(requestUsername)
        fetch('/dashboard/observer/request/'+ requestUsername + '/accept',{
            method: 'POST'
        }).then(function() {
            console.log('Parent?', e.target);
            const item = document.getElementById("observer-request-" + requestUsername)
            item.remove();
        }).catch(function(e) {
            console.error(e);
        });
    };
}
