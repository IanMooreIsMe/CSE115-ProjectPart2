/*globals TimelineLite, Power2, Bounce*/

function Visualizations() {
    $.get("./mapbox", function (data) {
        Plotly.setPlotConfig({
            mapboxAccessToken: data.token
        });
    });

    
    this.magColor = {0: "black", 1: "red", 2: "orange", 3: "yellow", 4: "green", 5: "blue", 6: "indigo", 7: "violet"};
}

Visualizations.prototype.update = function () {
    var myself = this,
        success = function (data) {
            myself.drawMap(data);
            myself.drawChart(data);
            myself.indicateLatest(data);
        };
    return $.get("./quakes").done(success);
};

Visualizations.prototype.drawMap = function (rawData) {
    var myself = this,
        data = [{
            type: "scattermapbox",
            mode: "markers",
            marker: {
                size: rawData.map(function (q) { return q.mag * 5 }),
                color: rawData.map(function (q) { return myself.magColor[Math.round(q.mag)] })
            },
            lat: rawData.map(function (q) { return q.lat }),
            lon: rawData.map(function (q) { return q.lon }),
            text: rawData.map(function (q) { return q.name })
        }],
        layout = {
            title: "Earthquakes",
            margin: {
                l: 0,
                r: 0,
                b: 0,
                t: 30,
                pad: 4
            },
            mapbox: {
                style: "satellite-streets"
            }
        };
    
    Plotly.newPlot("quake-map", data, layout, {responsive: true});
};

Visualizations.prototype.drawChart = function (rawData) {
    var freq = {};
    
    rawData.forEach(function (q) {
       var mag = Math.round(q.mag);
       if (mag in Object.keys(freq)) {
           freq[mag] += 1;
       } else {
           freq[mag] = 1;
       }
    });
    
    var data = [{
        values: Object.values(freq),
        labels: Object.keys(freq),
        marker: {
          colors: Object.values(this.magColor)
        },
        type: "pie"
    }];
    
    var layout = {
        title: "Rounded Magnitudes",
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 30,
            pad: 4
        }
    };
    
    Plotly.newPlot("quake-chart", data, layout, {responsive: true});
};

Visualizations.prototype.indicateLatest = function (rawData) {
    var quake = rawData[0],
        date = moment(quake.time).format('MMMM Do YYYY [at] h:mm:ss a');
    $("#quake-latest .detail").text( quake.name + " on " + date);
};