$(document).ready(function () {
    $("#submitbutton").on("click", handleFormSubmit);
 });

function handleFormSubmit(evt) {
    evt.preventDefault();
    $.ajax({
        type: "POST",
        url: "/userinput",
        data: $('#userinput').serialize(),
        dataType: "json",
        success: function( data ) {
        var image = data.img_file;
        console.log(image);
        $("#plot").attr("src", data.img_file);
        $('#number').text(data.iterations);
        $('#score').text(data.best_score);
        $('#route').text(data.route);
  }
});

}