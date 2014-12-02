<h1>The Travelling Saleswoman</h1>
<hr>
<p>The Travelling Saleswoman provides a tool to visualize the classic computer science travelling 
salesman optimization problem. This visualization tool provides the ability a solution for a user-selected 
subset of US cities. Choices of "Nearest Neighbor", "Hillclimb" and "Simulated Annealing" algorithms allow comparisons
of various solution methods. Solution modes include "As-the-crow-flies", "Drive", or "Fly" with the latter two modes
utilizing Directions from Google Directions API and Flight data from Google's QPX Express API.</p>
<img src = "static/img/TSPscreen1.png">
<h2>Technology Stack</h2>
<ul>
<li>Python</li>
<li>Flask</li>
<li>Google Maps API</li>
<li>Google Directions API</li>
<li>QPX Express API</li>
<li>SQLite/SQLAlchemy</li>
<li>Javascript/JQuery/JQuery UI</li>
<li>HTML/CSS/Bootstrap</li>
</ul>

<h2>File Guide</h2>
<ul>
<li>model.py</li>
<li>tsp.py: calculate distance matrix, solution algorithms</li>
<li>tspapp.py: controls the Flask app</li>
<li>tsp.js: user interactions</li>
</ul>



<h2>Additional Screenshots</h2>
<img src = "static/img/tspscreen2.png">


