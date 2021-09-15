const randomStr = (length = 16) => {
    return Math.random().toString(16).substr(2, length);
};

const getCookie = (name) => {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim().split('=');
        if (c[0] === name) {
            return c[1];
        }
    }
    return "";
}

if (getCookie("p_session") == "") {
    document.cookie = "p_session="+randomStr();
}

var prodigy_session_id = getCookie("p_session")

if ($(location).attr('hash') == "") {
    window.location.hash = "home";
}

if ($(location).attr('hash') == "kibana") {
    window.location.hash = "home";
}

function navigateToFrame() {
    var loc = "";
    var name = "";
    switch(window.location.hash) {
        case "#home":
            name = "Home"
            loc = "home.html"
            break;    
        case "#kibana":
            name = "Kibana"
            loc = "/kibana/";
            break;
        case "#prodigy":
            name = "Model Training"
            loc = "/prodigy/?session="+getCookie("p_session");
            break;
        case "#training-log":
            name = "Training Log"
            loc = "training-log.html";
            break;
    }

    $("#main-frame").attr("src", loc);
    $("#frame-title").html(name);

    $(".nav-link").removeClass("active");
    $("a[href='"+window.location.hash+"']").first().addClass("active");
}

$(document).ready(function() {
    navigateToFrame();
});

$(window).on('hashchange', function() {
    navigateToFrame();
});

$(".nav-link").click(function(){
    navigateToFrame();
})

if (!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    $("#favicon").attr("href","/static/img/blur_lm.png");
}