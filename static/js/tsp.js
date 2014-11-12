$(document).ready(function () {

var cities = [];
var markers = [];
var iterator = 0;
var map;
var linePath;
var linePaths = [];

google.maps.event.addDomListener(window, 'load', initialize);
get_cities_list();
$("#userinput").on("submit", handleFormSubmit);
$("#drop").on("click", get_cities_data);
$("#clear").on("click", clear);


function initialize(){
    // Create an array of styles.
    var styles = [
  //   {
  //   "featureType": "administrative.province",
  //   "elementType": "geometry.stroke",
  //   "stylers": [
  //     { "color": "#bdd4de" }
  //   ]
  // },{
  //   "featureType": "landscape.natural",
  //   "stylers": [
  //     { "color": "#2b3a42" }
  //   ]
  // },{
  //   "featureType": "water",
  //   "stylers": [
  //     { "visibility": "on" },
  //     { "color": "#3f5765" }
  //   ]
  // },{
  //   "featureType": "landscape.natural.terrain",
  //   "elementType": "geometry.stroke",
  //   "stylers": [
  //     { "visibility": "on" },
  //     { "color": "#808080" }
  //   ]
  // },
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
       },{
        featureType: "road",
        stylers: [
            { visibility: "off" }
    ]
  }
  // ,{
  //   "featureType": "landscape.natural.terrain",
  //   "stylers": [
  //     { "visibility": "off" }
  //   ]
  // }
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
                mapTypeIds: [google.maps.MapTypeId.ROADMAP, 'map_style']
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


function drawLine(tour_coords){

    var lineCoordinates = [];
    for (var i=0; i<tour_coords.length; i++){
        lat1 = tour_coords[i][0];
        long1 = -tour_coords[i][1];
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
    linePath.setMap(map);
}


function drawNearestNeighbor(tour_coords){
    var tourLength = tour_coords.length;
    var lineCoordinates = [];
    var i=0;
    linePaths = [];
    var drawFunction;
    drawFunction = setInterval(function () {
        j = i + 1;
        lat1 = tour_coords[i][0];
        long1 = -tour_coords[i][1];
        lat2 = tour_coords[j][0];
        long2 = -tour_coords[j][1];
        lineCoordinates = [new google.maps.LatLng(lat1, long1),
            new google.maps.LatLng(lat2, long2)];
        linePath = new google.maps.Polyline({
            path: lineCoordinates,
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 2
        });
        linePath.setMap(map);
        linePaths.push(linePath);
        i+=1;
        if (i>tourLength-2){
            clearInterval(drawFunction);
           //close the loop
            lat1 = tour_coords[tourLength - 1][0];
            long1 = -tour_coords[tourLength - 1][1];
            lat2 = tour_coords[0][0];
            long2 = -tour_coords[0][1];
            lineCoordinates = [new google.maps.LatLng(lat1, long1),
                new google.maps.LatLng(lat2, long2)];
            linePath = new google.maps.Polyline({
                path: lineCoordinates,
                geodesic: true,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2
            });
            linePath.setMap(map);
            linePaths.push(linePath);
        }
    }, 100);
}

function drawAnimation(animation_steps){
    //Here we animate
    var i=0;
    var drawFunction;
    drawFunction = setInterval(function () {
        console.log(animation_steps[i]); //The animation steps are there!
        drawLine(animation_steps[i]); // can I call this function here???
        i+=1;
    if (i>4){
        clearInterval(drawFunction);
    }
    }, 100);
}

function addMarker() {
          markers.push(new google.maps.Marker({
            position: cities[iterator],
            map: map,
            draggable: false,
            icon: "http://labs.google.com/ridefinder/images/mm_20_gray.png",
            animation: google.maps.Animation.DROP
          }));
          iterator++;
        }

function clear(evt) {
    evt.preventDefault();
    linePath.setMap(null);
    for (var i=0; i<linePaths.length; i++){
        linePaths[i].setMap(null);
    }
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
            for (var i=0; i<linePaths.length; i++){
                    linePaths[i].setMap(null);
                }
            var image = data.img_file;
            var tour_coords = data.tour_coords;
            var animation_steps = data.animation_steps;
            console.log(animation_steps);
            $('#plot').attr("src", data.img_file);
            $('#number').text(data.iterations);
            $('#score').text(data.best_score);
            $('#route').text(data.tour_cities);
            if($('#algorithm').val() == 'nearest'){
                drawNearestNeighbor(tour_coords);
            }
            else
            {
                drawLine(tour_coords);
                //drawAnimation(animation_steps);
            }
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
                cities.push(new google.maps.LatLng(data[i].lat, -data[i].longitude));
            }
            drop();
          }
        });
}

//populate the cities drop down list in the form
function get_cities_list(){
    $.ajax({
          type: 'GET',
          url: "/get_cities_data",
          dataType: 'json',
          success: function(data) {
            text = "";
            for (i=0; i< data.length; i++){
                text +="<option value='"+ i +"'>"+ data[i].city +"</option>";
            }
            $('#start').html(text);
        }
    });
}
});






