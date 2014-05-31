

$(".btn-group.checks-type li").on("click", function( event ) {
    var btn = $(this);
    if (!btn.hasClass("active") && !btn.hasClass("disabled"))
    {
	$(".checks-type button").html(btn.find("a").html() + " <span class=\"caret\"></span>");
	$($(".btn-group.checks-type li.active").data("target")).collapse("hide");
	$(".btn-group.checks-type li.active").removeClass("active");
	btn.addClass("active");
	$(btn.data("target")).collapse("show");
    }
} )

