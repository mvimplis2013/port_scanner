function stackMin(serie) {
    return d3.min(serie,  function(d) { return d[0]; });
}

function stackMax(serie) {
    return d3.max(serie, function(d) { return d[1]; });
}

(function() {
    var data = [
        {month: "Q1-2016", apples: 3840, bananas: 1920, cherries: -1960, dates: -400},
        {month: "02-2016", apples: 1600, bananas: 1440, cherries: -960, dates: -400}
    ];

    /*
    var series = d3.stack()
        .keys(["apples", "bananas", "cherries", "dates"])
        .offset(d3.stackOffsetDiverging)
        (data);

    var svg = d3.select("svg");
    var margin = {top: 20, right: 30, bottom: 30, left: 60};
    var width = +svg.attr("width");
    var height = +svg.attr("height");

    var x = d3.scaleBand().domain(data.map(function(d) { return d.month; })).rangeRound([margin.left, width-margin.right]).padding(0.1);

    var y = d3.scaleLinear().domain([d3.min(series, stackMin), d3.max(series, stackMax)]).rangeRound([height-margin.bottom, margin.top]);

    var z = d3.scaleOrdinal(d3.schemeCategory10);

    svg.append("g").selectAll("g").data(series).enter().append("g").attr("fill", function(d) { return z(d.key);})
        .selectAll("rect").attr("width", x.bandwidth).attr("x", function(d) { return x(d.data.month); })
        .attr("y", function(d) { return y(d[1]); }).attr("height", function(d) { return y(d[0]) - y(d[1]); })

    svg.append("g").attr("transform", "translate(0," + y(0) + ")").call(d3.axisBottom(x));

    svg.append("g").attr("transform", "translate(" + margin.left + ", 0)"); */

    var canvas = document.querySelector("#donut");
    var context = canvas.getContext("2d");

    var width = canvas.width, height = canvas.height, radius = Math.min(width, height) / 2;

    var colors = ["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"];

    var arc = d3.arc().outerRadius(radius-10).innerRadius(radius-70).context(context);

    var labelArc = d3.arc().outerRadius(radius-40).innerRadius(radius-40).context(context);

    var pie = d3.pie().sort(null).value(function(d) { return d.population; });

    context.translate(width/2, height/2);

    //function(d) {
    //    console.log( "Population is ... " + d.population );

    //    d.population = +d.population;
    //    return d;
    //},

    d3.tsv("gui/data/data.tsv", 
        function(d) {
            //console.log( "Population is ... " + d.age + " , " + d.population );
    
            d.population = +d.population;
            
            return d;
        }, function(error, data) {
            if (error) throw error;

            //console.log("Data is ..." + data );
            
            var arcs = pie(data);
        
            //console.log( data[1].age );
            //console.log( arcs );

            arcs.forEach( function(d, i) {
                //console.log( ">>>> " + i + " ... " + d.data.age );

                context.beginPath();
                arc(d);
                context.fillStyle = colors[i];
                context.fill();
            });

            context.beginPath();
            arcs.forEach(arc);
            context.strokeStyle = "#fff";
            context.stroke();

            context.textAlign = "center";
            context.textBaseline = "middle";
            context.fillStyle = "#000";
            arcs.forEach( function(d) {
                var c = labelArc.centroid(d);
                context.fillText(d.data.age, c[0], c[1]);
            });
    });

    var canvas_bar = document.querySelector( "#bar" );
    var context_bar = canvas_bar.getContext("2d");

    var margin = {top: 20, right: 20, bottom: 30, left: 40};
    
    var width = canvas.width - margin.left - margin.right;
    var height = canvas.height - margin.top - margin.bottom;

    var x = d3.scaleBand().rangeRound([0, width]).padding(0.1);
    var y = d3.scaleLinear().rangeRound([height, 0]);

    context_bar.translate(margin.left, margin.top);

    d3.tsv("gui/data/data_bar.tsv", function(d) {
        d.frequency = +d.frequency;

        return d;
    }, function(error, data) {
        if (error) throw error;

        x.domain( data.map( function(d) { return d.letter; }));
        y.domain( [0, d3.max(data, function(d) { return d.frequency; })]);
    
        var yTickCount = 18;
        var yTicks = y.ticks(yTickCount);
        var yTickFormat = y.tickFormat(yTickCount, "%");

        context_bar.beginPath();
        x.domain().forEach( function(d) {
            context_bar.moveTo(x(d) + x.bandwidth() / 2, height);
            context_bar.lineTo(x(d) + x.bandwidth() / 2, height + 6);
        });
        context_bar.strokeStyle = "black";
        context_bar.stroke();

        context_bar.textAlign = "center";
        context_bar.textBaseline = "top";
        x.domain().forEach(function(d) {
        context_bar.fillText(d, x(d) + x.bandwidth() / 2, height + 6);
    });

    context_bar.beginPath();
    yTicks.forEach( function(d) {
        context_bar.moveTo(0, y(d) + 0.5);
        context_bar.lineTo(-6, y(d) + 0.5);
    });
    context_bar.strokeStyle = "black";
    context_bar.stroke();

    context_bar.textAlign = "right";
    context_bar.textBaseline = "middle";
    yTicks.forEach(function(d) {
        context_bar.fillText(yTickFormat(d), -9, y(d));
    });

    context_bar.beginPath();
    context_bar.moveTo(-6.5, 0+0.5);
    context_bar.lineTo(0.5, 0+0.5);
    context_bar.lineTo(0.5, height+0.5);
    context_bar.lineTo(-6.5, height+0.5);
    context_bar.strokeStyle = "black";
    context_bar.stroke();

    context_bar.save();
    context_bar.rotate(-Math.PI/2);
    context_bar.textAlign = "right";
    context_bar.textBaseline = "top";
    context_bar.font = "bold 10px sans-serif";
    context_bar.fillText("Frequency", -10, 10);
    context_bar.restore();

    context_bar.fillStyle = "steelblue";
    data.forEach(function(d) {
        context_bar.fillRect(x(d.letter), y(d.frequency), x.bandwidth(), height - y(d.frequency));
    });
});
    var formatChange = d3.format("+d");
    var formatValue = d3.format("d");

    svg = d3.select("#waterfall");

    margin = {top:20, right: 40, bottom: 40, left: 80};
    width = svg.attr("width") - margin.left - margin.right;
    height = svg.attr("height") - margin.top - margin.bottom;

    var g = svg.append("g").attr("transform", "translate(" + margin.left + " , " + margin.top + ")");

    d3.tsv("gui/data/data_waterfall.tsv", function(d) {
        d.value = +d.value;

        return d;
    }, function(error, data) {
        if (error) throw error;

        data.reduce(function(v, d) {
            return d.value1 = (d.value0 = v) + d.value; 
        }, 0);

        var x = d3.scaleLinear().domain(d3.extent(data, function(d) { return d.value1; })).nice().range([0, width]);
        var y = d3.scaleBand().domain(data.map(function(d) { return d.region; })).rangeRound([0, height]).padding(0.1);

        g.append("g").attr("transform", "translate(0," + height + ")" ).attr("class", "axis axis--x").call(d3.axisBottom(x));

        g.append("g").selectAll("rect").data(data).enter().append("rect")
            .attr("class", function(d) { return "rect rect--" + (d.value0 < d.value1 ? "positive" : "negative"); })
            .attr("y", function(d) { return y(d.region); })
            .attr("x", function(d) { return x(d.value0 < d.value1 ? d.value0 : d.value1); })
            .attr("width", function(d) { return d.value0 < d.value1 ? x(d.value1) - x(d.value0) : x(d.value0) - x(d.value1); })
            .attr("height", y.bandwidth());

        g.append("g")
            .attr("class", "axis axis--y")
            .attr("transform", "translate(" + x(0) + ",0)")
            .call(d3.axisLeft(y).tickSize(0).tickPadding(x(0) + 6));
    });
}()); 