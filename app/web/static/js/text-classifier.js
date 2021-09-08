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
            loc = "/prodigy/";
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