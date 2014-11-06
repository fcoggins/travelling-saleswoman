$(document).ready(function () {

var cities = [];
var markers = [];
var iterator = 0;
var map;

google.maps.event.addDomListener(window, 'load', initialize);
$("#userinput").on("submit", handleFormSubmit);
$("#drop").on("click", get_cities_data);

function initialize(){

            var mapOptions = {
                center: { lat: 39.8282, lng: -98.5795},
                zoom: 4,
                mapTypeId: google.maps.MapTypeId.TERRAIN,
                disableDefaultUI: true
            };

            map = new google.maps.Map(document.getElementById('map-canvas'),
                mapOptions);
        }

function addMarker() {
          markers.push(new google.maps.Marker({
            position: cities[iterator],
            map: map,
            draggable: false,
            animation: google.maps.Animation.DROP
          }));
          iterator++;
        }

function drop() {
  for (var i = 0; i < cities.length; i++) {
    setTimeout(function() {
      addMarker();
    }, i * 10);
  }
}


function handleFormSubmit(evt) {
    evt.preventDefault();
    $.ajax({
        type: "POST",
        url: "/userinput",
        data: $('#userinput').serialize(),
        dataType: "json",
        success: function( data ) {
            var image = data.img_file;
            $("#plot").attr("src", data.img_file);
            $('#number').text(data.iterations);
            $('#score').text(data.best_score);
            $('#route').text(data.route);
      }
});
}

function get_cities_data(evt){
    $.ajax({
          type: 'GET',
          url: "/get_cities_data",
          dataType: 'json',
          success: function(data) {
            for (i=0; i< data.length; i++){
                console.log(data[i].lat, -data[i].longitude);
                cities.push(new google.maps.LatLng(data[i].lat, -data[i].longitude));
            }
            alert(cities[0]);
            drop();
          }
        });
}

});
