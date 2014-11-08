$(document).ready(function () {

var cities = [];
var markers = [];
var iterator = 0;
var map;
var linePath;

google.maps.event.addDomListener(window, 'load', initialize);
$("#userinput").on("submit", handleFormSubmit);
$("#drop").on("click", get_cities_data);


function initialize(){
    // Create an array of styles.
    var styles = [
       {
         featureType: "administrative",
         elementType: "labels",
         stylers: [
           { visibility: "off" }
         ]
       },{
         featureType: "poi",
         elementType: "labels",
         stylers: [
           { visibility: "off" }
         ]
       },{
         featureType: "water",
         elementType: "labels",
         stylers: [
           { visibility: "off" }
         ]
       },{
         featureType: "road",
         elementType: "labels",
         stylers: [
           { visibility: "off" }
         ]
       }
     ];

    // Create a new StyledMapType object, passing it the array of styles,
    // as well as the name to be displayed on the map type control.
    var styledMap = new google.maps.StyledMapType(styles,
        {name: "Styled Map"});

    // Create a map object, and include the MapTypeId to add
    // to the map type control.
            var mapOptions = {
                center: { lat: 38.5, lng: -96},
                zoom: 5,
                //mapTypeId: google.maps.MapTypeId.TERRAIN,
                disableDefaultUI: true,
                draggable: false,
                zoomControl: false,
                scrollwheel: false,
                disableDoubleClickZoom: true,
                mapTypeControlOptions: {
                    mapTypeIds: [google.maps.MapTypeId.TERRAIN, 'map_style']
                }
            };

    map = new google.maps.Map(document.getElementById('map-canvas'),
                mapOptions);
    linePath = new google.maps.Polyline();

    //Associate the styled map with the MapTypeId and set it to display.
    map.mapTypes.set('map_style', styledMap);
    map.setMapTypeId('map_style');

    //Draw a line on the map. Design decision to draw using google LatLng function
    //but can get this from the database later if needed

    }


// So this isn't working. It probably would be better to build a
//long list of the coordinates and then just accumulate a long list into
//line coordinates. Create linepath one time. Then setMap.

function drawLine(tour_coords){

    console.log(tour_coords);
    var lineCoordinates = [];
    for (var i=0; i<tour_coords.length; i++){
        lat1 = tour_coords[i][0];
        long1 = -tour_coords[i][1];
        console.log(lat1, long1);
        lineCoordinates.push(
            new google.maps.LatLng(lat1, long1)
        );
    }
    lineCoordinates.push(
            new google.maps.LatLng(tour_coords[0][0], -tour_coords[0][1])
        );
            linePath = new google.maps.Polyline({
            path: lineCoordinates,
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 2
        });
    console.log(linePath);
    linePath.setMap(map);
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
            linePath.setMap(null);
            var image = data.img_file;
            var tour_coords = data.tour_coords;
            $("#plot").attr("src", data.img_file);
            $('#number').text(data.iterations);
            $('#score').text(data.best_score);
            $('#route').text(data.route);
            drawLine(tour_coords);
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
