$(document).ready(function () {

var cities = [];
var markers = [];
var iterator = 0;
var map;
var linePath, iterations, best_score, tour_cities, tour_coords, current_score, polyline_best_tour;
var drawAnimationFunction, polyline;
var linePaths = [];
var cities_string = "";

google.maps.event.addDomListener(window, 'load', initialize);
get_cities_list(); //populate the cities dropdown 
$("#userinput").on("submit", handleFormSubmit);
$("#drop").on("click", get_cities_data);
$("#clear").on("click", clear);
$("#stop").on("click", stop);



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
    linePath.setMap(null);

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
    //$("#stop").disabled = true; //stop button messes up the nearest neighbor
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

function drawAnimation(animation_coords){
    var i=0;
    drawAnimationFunction = setInterval(function () {
        drawLine(animation_coords[i]);
        $('#number').text(i+1);
        $('#score').text(current_score[i]);//here we add the current route length
        i+=1;
        if (i>(animation_coords.length - 1)){
            clearInterval(drawAnimationFunction);
            $('#route').text(cities_string);//write the route here
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

//draw actual road paths

function addEncodedPaths() {
    for( var i = 0, n = polyline_best_tour.length;  i < n;  i++ ) {
        addEncodedPath( polyline_best_tour[i] );
    }
}

function addEncodedPath( encodedPath ) {

    var path = google.maps.geometry.encoding.decodePath( encodedPath );

    polyline = new google.maps.Polyline({
        path: path,
        strokeColor: "#0000FF",
        strokeOpacity: 1.0,
        strokeWeight: 2
    });
    polyline.setMap( map );
    console.log(polyline);
}

function clear() {
    clearInterval(drawAnimationFunction);//stop the animation running
    $('#number').empty();
    $('#score').empty();
    $('#route').empty();
    linePath.setMap( null );//remove best route from map(as the crow flies)
    console.log(linePath);
    //console.log(polyline);
    //polyline.setMap( null );//remove best route from map(Road distance)
    for (var i=0; i<linePaths.length; i++){
        linePaths[i].setMap(null);//remove the individual legs from map(Nearest Neighbor)
    }
}

function stop() {
    clearInterval(drawAnimationFunction);
    drawLine(tour_coords);
    $('#number').text(iterations);
    $('#score').text(best_score);
    $('#route').text(cities_string);
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
          //initialize everything
            linePath.setMap(null);
            iterations = null;
            best_score = null;
            cities_string = "";
            polyline_best_tour = [];
            for (var i=0; i<linePaths.length; i++){
                    linePaths[i].setMap(null);
                }
            clear();

            //import our data
            var image = data.img_file;
            tour_coords = data.tour_coords;
            var animation_coords = data.animation_coords;
            iterations = data.iterations;
            best_score = -data.best_score.toFixed(0);
            tour_cities = data.tour_cities;
            for (var k=0; k < tour_cities.length; k++){              
                cities_string += tour_cities[k] + ', ';
            }
            current_score = data.current_score;
            for (var j=0; j < current_score.length; j++){
                current_score[j] = -current_score[j].toFixed(0);
            }
            polyline_best_tour = data.poly_list;


            //Draw on our map
            // $('#plot').attr("src", data.img_file);
            if($('#algorithm').val() == 'nearest'){
                drawNearestNeighbor(tour_coords);
            }
            else
            {
              if($('#mode').val() == 'as_the_crow_flies'){
                drawAnimation(animation_coords);
              }
              else if($('#mode').val() == 'roads'){
                addEncodedPaths();
              }
              else{
                console.log('error');
              }
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





