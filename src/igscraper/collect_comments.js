window.acc_arr = [];
window.comments= [];
window.waiting_time = 500;//ms
window.iteration = 0;
function finish() {
    return window.comments;
}
var c = async () => {
    window.iteration+=1;
    console.log("--------")
    console.log(document.querySelectorAll(".eo2As .gElp9").length)
    window.acc_arr.push(document.querySelectorAll(".eo2As .gElp9").length);
    for(node of document.querySelectorAll(".eo2As .gElp9")){
        window.comments.push({
            "comment": node.innerText,
            "html": node.innerHTML
            })
        node.remove();
    }
    var button = await document.querySelectorAll("span[aria-label='Load more comments']")[0] 
    if(!button){
       return false 
    }
    button.click();
    return true
}
async function main() {
    var prev_n_comments = document.querySelectorAll(".eo2As .gElp9").length
    status = await c()
    if(status==="false" & window.acc_arr.length > 1){
        // either button not exists bc there's 13 or less comments OR it failed because button didn't load
        var n_last_collected = 5
        if(window.acc_arr.length >= n_last_collected){
            var sum_last_n_collected = window.acc_arr
                                             .slice(window.length-1-n_last_collected)
                                             .reduce((a,v) => a+v) 
        }
        else{ 
            var sum_last_n_collected =  -1
        }

        if(sum_last_n_collected !== 0){
            setTimeout(main, window.waiting_time)
        }
        else{
            setTimeout(finish, window.waiting_time)
        }
        return true
    }
    else{
        setTimeout(main, window.waiting_time)
        return true
    }
}
main()
