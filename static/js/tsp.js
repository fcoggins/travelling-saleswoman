var MAP_PIN = 'M0-165c-27.618 0-50 21.966-50 49.054C-50-88.849 0 0 0 0s50-88.849 50-115.946C50-143.034 27.605-165 0-165z';
var MAP_CIRCLE = google.maps.SymbolPath.CIRCLE;
var cities = [];
var markers = [];
var iterator = 0;
var map;
var linePath, iterations, best_score, tour_cities, tour_coords, current_score, polyline_best_tour, selected_cities_text;
var drawAnimationFunction;
var polyline;
var linePaths = [];
var neighborPaths = [];
var selected_cities = [];
var cities_string = "";

$(document).ready(function () {
google.maps.event.addDomListener(window, 'load', initialize);
window.setTimeout(show_intro(), 100);
$("#continue").on("click", begin);
$("#new").on("click", new_tour);
$("#drop").on("click", handleCitiesForm);
$("#userinput").on("submit", handleFormSubmit);
$("#clear").on("click", clear);
$("#stop").on("click", stop);
$("#next").on("click", resetMyForm);
$("#select_algorithm").on("click", function(evt){
  evt.preventDefault();
  var algorithm = $('#algorithm').val();
  $("#select_algorithm").hide();
  if (algorithm == 'nearest'){
    $(".nearest_neighbor").show();
    $(".hill_anneal").hide();
    $(".anneal").hide();
    $(".mode_class").show();
    $("#submitbutton").show();
    $(".stop_clear").show();
    $("#next_algorithm").show();
    $(".new_tour").show();
    $("label[for='algorithm']").hide();
    $("#algorithm").hide();
    $(".mode_class").prepend('<h4>Algorithm: Nearest Neighbor</h4>');
    $("#stop").hide();
  }
  else if (algorithm == 'hillclimb' || algorithm == 'hill_restart') {
    $(".nearest_neighbor").hide();
    $(".anneal").hide();
    $(".mode_class").show();
    $(".hill_anneal").show();
    $("#submitbutton").show();
    $(".stop_clear").show();
    $("#next_algorithm").show();
    $(".new_tour").show();
    $("label[for='algorithm']").hide();
    $("#algorithm").hide();
    $("#stop").show();
    if (algorithm == 'hillclimb'){
      $(".mode_class").prepend('<h4>Algorithm: Hillclimb</h4>');
      }
      else
      {
      $(".mode_class").prepend('<h4>Algorithm: Hillclimb & Restart</h4>');
      }
    }
  else if (algorithm == 'annealing'){
    $(".nearest_neighbor").hide();
    $(".hill_anneal").show();
    $(".mode_class").show();
    $(".anneal").show();
    $("#submitbutton").show();
    $(".stop_clear").show();
    $("#next_algorithm").show();
    $(".new_tour").show();
    $("label[for='algorithm']").hide();
    $("#algorithm").hide();
    $("#stop").show();
    $(".mode_class").prepend('<h4>Algorithm: Simulated Annealing</h4>');
  }
  else{
    console.log('error in algorithm selection');
  }
});


function show_intro(){
    setTimeout(function() {
        $( "#intro" ).hide().fadeIn();
      }, 1500 );
    }
//}

function begin(){
  $("#intro").hide().fadeOut();
  $("#cities").show().fadeIn();
  get_cities_list();
}

function drop() {
  for (var i = 0; i < cities.length; i++) {
    setTimeout(function() {
      addMarker();
    }, i * 10);
  }
}

function initialize(){
    // Create an array of styles.
    var styles = [
        {"elementType":"labels","stylers":[{ "visibility": "off" }]},
        {"stylers":[{"saturation":-100},{"gamma":1}]},
        {"elementType":"labels.text.stroke","stylers":[{"visibility":"off"}]},
        {"featureType":"poi.business","elementType":"labels.text","stylers":[{"visibility":"off"}]},
        {"featureType":"poi.business","elementType":"labels.icon","stylers":[{"visibility":"off"}]},
        {"featureType":"poi.place_of_worship","elementType":"labels.text","stylers":[{"visibility":"off"}]},
        {"featureType":"poi.place_of_worship","elementType":"labels.icon","stylers":[{"visibility":"off"}]},
        {"featureType":"road","elementType":"geometry","stylers":[{"visibility":"simplified"}]},
        {"featureType":"water","stylers":[{"visibility":"on"},{"saturation":50},{"gamma":0},{"hue":"#50a5d1"}]},
        {"featureType":"administrative.neighborhood","elementType":"labels.text.fill","stylers":[{"color":"#333333"}]},
        {"featureType":"road.local","elementType":"labels.text","stylers":[{"weight":0.5},{"color":"#333333"}]},
        {"featureType":"transit.station","elementType":"labels.icon","stylers":[{"gamma":1},{"saturation":50}]}
     ];



    // Create a new StyledMapType object, passing it the array of styles,
    // as well as the name to be displayed on the map type control.
    var styledMap = new google.maps.StyledMapType(styles,
        {name: "Styled Map"});

    // Create a map object, and include the MapTypeId to add
    // to the map type control.
            var mapOptions = {
                center: { lat: 39, lng: -90},
                zoom: 5,
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
            strokeColor: '#ec571d',
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
            strokeColor: '#ec571d',
            strokeOpacity: 1.0,
            strokeWeight: 3
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
                strokeColor: '#ec571d',
                strokeOpacity: 1.0,
                strokeWeight: 3
            });
            linePath.setMap(map);
            linePaths.push(linePath);
            $('.iterations').hide();
            $('#score').text(-best_score);//here we add the current route length
            $('#route').text(cities_string);//write the route here
        }
    }, 100);
}

function drawAnimation(animation_coords){
    $('.iterations').show();
    var i=0;
    drawAnimationFunction = setInterval(function () {
      if($("#mode").val() == 'as_the_crow_flies'){
        drawLine(animation_coords[i]);
      }
      else
      {
        addEncodedPaths(animation_coords[i]);
      }
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
    var fillcolor = "#99aead";
      markers.push(new google.maps.Marker({
        position: cities[iterator],
        map: map,
        draggable: false,
        icon: {
        path: MAP_PIN,
        fillColor: fillcolor,
        fillOpacity: 1,
        strokeColor: '#000',
        strokeWeight: 1,
        scale: 1/8
        },
        animation: google.maps.Animation.DROP,
        title: selected_cities[iterator][1]
      }));
          iterator++;
        }

//draw actual road paths

function addEncodedPaths(tour) {
    var path;
    var paths=[];
    if (polyline){
      polyline.setMap( null );
    }
    for( var i = 0, n = tour.length;  i < n;  i++ ) {
        path=google.maps.geometry.encoding.decodePath(tour[i]);
        paths = paths.concat(path);
    }

    polyline = new google.maps.Polyline({
        path: paths,
        strokeColor: "#2f575d",
        strokeOpacity: 1.0,
        strokeWeight: 2
    });
    polyline.setMap( map );
}

function drawNeighborRoad(){
    var path;
    var i=0;
    var drawFunction;
    //$("#stop").disabled = true; //stop button messes up the nearest neighbor
    drawFunction = setInterval(function () {
        path=google.maps.geometry.encoding.decodePath(polyline_best_tour[i]);

        linePath = new google.maps.Polyline({
            path: path,
            geodesic: true,
            strokeColor: '#2f575d',
            strokeOpacity: 1.0,
            strokeWeight: 3
        });
        linePath.setMap(map);
        neighborPaths.push(linePath);
        i+=1;
        if (i>polyline_best_tour.length-2){
            clearInterval(drawFunction);
           //close the loop
            path=google.maps.geometry.encoding.decodePath(polyline_best_tour[i]);
            linePath = new google.maps.Polyline({
                path: path,
                geodesic: true,
                strokeColor: '#2f575d',
                strokeOpacity: 1.0,
                strokeWeight: 3
            });
            linePath.setMap(map);
            neighborPaths.push(linePath);
        }
    $('.iterations').hide();
    $('#score').text(-best_score);//here we add the current route length
    $('#route').text(cities_string);//write the route here
    }, 100);
}

function clear() {
    clearInterval(drawAnimationFunction);//stop the animation running
    $('#number').empty();
    $('#score').empty();
    $('#route').empty();
    iterations = 0;
    best_score = 0;
    cities_string = '';
    tour_coords = null;
    polyline_best_tour = null;
    linePath.setMap( null );//remove best route from map(as the crow flies)
    if (polyline){
      polyline.setMap( null );//remove best route from map(road distance)
    }
    for (var i=0; i<linePaths.length; i++){
        linePaths[i].setMap(null);//remove the individual legs from map(Nearest Neighbor)
    }
    for (var j=0; j<neighborPaths.length; j++){
        neighborPaths[j].setMap(null);//remove the individual legs from map(Nearest Neighbor, Road)
    }

}

function stop() {
    clearInterval(drawAnimationFunction);
    if(tour_coords && $('#mode').val() == 'as_the_crow_flies'){
      drawLine(tour_coords);
    }

    if(polyline_best_tour && $('#mode').val() == 'roads'){
      addEncodedPaths(polyline_best_tour);
    }
    $('.iterations').show();
    $('#number').text(iterations);
    $('#score').text(best_score);
    $('#route').text(cities_string);
}

function resetMyForm(){
    $('.results').hide();
    $('#userinput')[0].reset();
    $(".nearest_neighbor").hide();
    $(".hill_anneal").hide();
    $(".anneal").hide();
    $("#submitbutton").hide();
    $(".stop_clear").hide();
    $("#select_algorithm").show();
    $(".mode_class").hide();
    $("#next_algorithm").hide();
    $("label[for='algorithm']").show();
    $("#algorithm").show();
    $(".mode_class > h4").remove();
    clear_start_city(selected_cities);
    clear();
}

function handleCitiesForm(evt) {
  evt.preventDefault();

  $.ajax({
    type: "POST",
    url: "/get_cities_data",
    data: $('#cityinput').serializeArray(),
    dataType: "json",
    success: function( data ) {
      for (i=0; i< data.length; i++){
                cities.push(new google.maps.LatLng(data[i].lat, -data[i].longitude));
                selected_cities.push([data[i].id, data[i].city]);
            }

      get_start_city(selected_cities); //populate the cities for nearest neighbor
      $("#cities").hide();
      $("#input").show();
        drop();
    }
  });
}

function handleFormSubmit(evt) {
    evt.preventDefault();
    var jsonText = $('#userinput').serialize();
    jsonText += "&selected_cities="+selected_cities;
    $.ajax({
        type: "POST",
        url: "/userinput",
        data: jsonText,
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
            $('#results').show();

            //import our data
            //var image = data.img_file;
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
            var poly_animation_steps = data.poly_animation_steps;

            if($('#algorithm').val() == 'nearest'){
                clear_start_city(selected_cities);
                start_city_coords = new google.maps.LatLng(tour_coords[0][0], -tour_coords[0][1]);
                var fillcolor = "#28363d";
                  markers.push(new google.maps.Marker({
                    position: start_city_coords,
                    map: map,
                    draggable: false,
                    icon: {
                    path: MAP_PIN,
                    fillColor: fillcolor,
                    fillOpacity: 1,
                    strokeColor: '#000',
                    strokeWeight: 1,
                    scale: 1/8
                    },
                    animation: google.maps.Animation.DROP,
                    title: tour_cities[0]
                  }));

              if($('#mode').val() == 'as_the_crow_flies'){
                drawNearestNeighbor(tour_coords);
              }
              else if($('#mode').val() == 'roads'){
                drawNeighborRoad();                 
              }
              else{
                console.log('error');
              }
            }
            else
            {
              if($('#mode').val() == 'as_the_crow_flies'){
                drawAnimation(animation_coords);
              }
              else if($('#mode').val() == 'roads'){
                drawAnimation(poly_animation_steps);
              }
              else{
                console.log('error');
              }
            }
      }
});
}

function clear_start_city(selected_cities){
    var fillcolor = "#99aead";
    for(i=0; i<selected_cities.length; i++){
    markers.push(new google.maps.Marker({
        position: cities[i],
        map: map,
        draggable: false,
        icon: {
        path: MAP_PIN,
        fillColor: fillcolor,
        fillOpacity: 1,
        strokeColor: '#000',
        strokeWeight: 1,
        scale: 1/8
        },
        animation: null,
        title: selected_cities[i][1]
      }));
        }
        }

    function new_tour(){
        selected_cities = [];
        tour_cities = [];
        cities = [];
        iterator = 0;
        $("#input").hide();
        resetMyForm();
        deleteMarkers();
        polyline = null;
        linePath.setMap(null);
        iterations = null;
        best_score = null;
        cities_string = "";
        polyline_best_tour = [];        
        for (var i=0; i<linePaths.length; i++){
                linePaths[i].setMap(null);
            }
    begin();
    }

    // Sets the map on all markers in the array.
function setAllMap(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

// Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
  setAllMap(null);
}

// Shows any markers currently in the array.
function showMarkers() {
  setAllMap(map);
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
  clearMarkers();
  markers = [];
}

});// close document.ready function



//initial population of cities drop down and add all cities to map
function get_cities_list(){
    var iterator = 0;
    $.ajax({
          type: 'GET',
          url: "/get_initial_data",
          dataType: 'json',
          success: function(data) {
            
            text = "";
            for (var i=0; i< data.length; i++){
                //create the dropdown
                text +="<option value='"+ i +"'>"+ data[i].city +"</option>";
                //add markers for all cities on map
                var pos = new google.maps.LatLng(data[i].lat, -data[i].longitude);
                var capital = data[i].capital;
                if (capital === 0){
                    icontype = {
                        path: google.maps.SymbolPath.CIRCLE,
                        fillColor: '#6d9197',
                        fillOpacity: 1,
                        strokeColor: '#2f575d',
                        strokeWeight: 0.5,
                        scale: 3.7
                    };
                }
                else
                {
                    icontype = {
                        url: 'static/img/star.gif',
                        size: new google.maps.Size(14, 13),
                        origin: new google.maps.Point(0,0),
                        anchor: new google.maps.Point(6, 6)
                    };
                }
                markers.push(new MarkerWithLabel({
                    position: pos,
                    map: map,
                    icon: icontype,
                    title: data[i].city,
                    labelContent: data[i].city,
                    labelAnchor: new google.maps.Point(0, 0),
                    labelClass: "labels", // the CSS class for the label
                    labelStyle: {opacity: 0.75}
                }));
            }
            $('#city_group').html(text);
            selected_cities_text = [{'city_group':null}, {'city_group':null}];
            for (var j=0; j < markers.length; j++){
                google.maps.event.addListener(markers[j], 'click', bindClick(j));
            }
            
            function bindClick(k){
                return function(){
                    var select_list = [];
                    //change the marker color here
                    change_Marker_Red(k);

                    $('#city_group option').each(function(){
                        select_list.push($(this).val());
                    });
                    console.log(select_list, "select");
                    for (var i=0; i<select_list.length; i++){
                        if(select_list[i] == data[k].id - 1){
                            $('#city_group option[value='+select_list[i]+']').attr("selected","selected");
                        }
                    }
                };
            }
    }
    });
}

$( "#city_group" ).change(function(evt){
console.log('change in dropdown');
$( "#city_group option:selected" ).each(function() {
      console.log($( this ).val()); //$(this).val()+1 is the city id
      selected = $(this).val();
      console.log(markers[selected]);
      change_Marker_Red(selected);
    });
});
                  
  // 3. when you have the marker change its color 
function change_Marker_Red(k){
    markers[k].setIcon({
    path: google.maps.SymbolPath.CIRCLE,
    fillColor: '#ff530d',
    fillOpacity: 1,
    strokeColor: '#2f575d',
    strokeWeight: 0.5,
    scale: 3.5
    });
}


function get_start_city(selected_cities){
            text = "";
            for (i=0; i< selected_cities.length; i++){
                text +="<option value='"+ selected_cities[i][0] +"'>"+ selected_cities[i][1]+"</option>";
            }
            $('#start').html(text);
        }

$(function() {
    $( "#intro" ).draggable();
    $( "#cities" ).draggable();
    $( "#input" ).draggable();
    $( "#results" ).draggable();
  });









