$(window).on('load', function() {
  $("#loading").fadeOut(600);
});

$(".select2").select2();

function drawBubbleChart(csv_file) {

  var width = 520,
      height = 520;

  var div = d3.select("#svg-container").append("div") 
      .attr("class", "tooltip")
      .attr("pointer-events", "none") 
      .style("opacity", 0);

  var svg =  d3.select("#svg-container")
      .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("font-family", "sans-serif")
        .attr("font-size", 10)
        .attr("text-anchor", "middle");

  var format = d3.format(",d");

  var color = d3.scaleOrdinal(d3.schemeCategory20c);

  var pack = d3.pack()
      .size([width, height])
      .padding(1.5);

  d3.csv(csv_file, function(d) {
    d.value = +d.value;
    if (d.value) return d;
  }, function(error, classes) {
    if (error) throw error;

    var root = d3.hierarchy({children: classes})
        .sum(function(d) { return d.value; })
        .each(function(d) {
          d.id = d.data.word;
        });

    var node = svg.selectAll(".node")
      .data(pack(root).leaves())
      .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

    node.append("circle")
        .attr("id", function(d) { return d.id; })
        .attr("r", function(d) { return d.r; })
        .style("fill", function(d) { return color(d.value); })
        .on("mouseover", function(d) {
            d3.select(this).style("fill", "gold"); 
            div.transition()    
                .duration(200)    
                .style("opacity", .9);    
            div .html("Palabra: " + d.id + "<br/>Frecuencia: "  + d.value)  
                .style("left", (d3.event.pageX) + "px")   
                .style("top", (d3.event.pageY - 28) + "px");  
        })
        .on("mousemove", function(d,i) {
            div .html("Palabra: " + d.id + "<br/>Frecuencia: "  + d.value)  
                .style("left", (d3.event.pageX) + "px")   
                .style("top", (d3.event.pageY - 60) + "px"); 
        })         
        .on("mouseout", function(d) {
            d3.select(this).style("fill", function(d) { return color(d.value); }); 
            div.transition()    
                .duration(500)    
                .style("opacity", 0); 
        });

    node.append("text")
      .text(function(d) { return d.id; })
      .attr("pointer-events", "none")
      .style("font-size", adaptLabelFontSize)
      .attr("dy", ".35em");

  });

  function adaptLabelFontSize(d) {
    var xPadding, diameter, labelAvailableWidth, labelWidth;
    xPadding = 8;
    diameter = 2 * d.r;
    labelAvailableWidth = diameter - xPadding;
    labelWidth = this.getComputedTextLength();
    // There is enough space for the label so leave it as is.
    if (labelWidth < labelAvailableWidth) {
      return null;
    }
    /*
     * The meaning of the ratio between labelAvailableWidth and labelWidth equaling 1 is that
     * the label is taking up exactly its available space.
     * With the result as `1em` the font remains the same.
     *
     * The meaning of the ratio between labelAvailableWidth and labelWidth equaling 0.5 is that
     * the label is taking up twice its available space.
     * With the result as `0.5em` the font will change to half its original size.
     */
    return (labelAvailableWidth / labelWidth) + 'em';
  }
};

drawBubbleChart('./csv/filtered_words_per_accounts.csv');

$('.select2').on('change', function() {
  $('.tooltip').remove();
  d3.select("svg").remove();
  option = $(".select2").val();
  switch(option) {
    case "0":
      drawBubbleChart('./csv/filtered_words_per_accounts.csv');
      var text = 'Se muestra un gráfico de burbujas en donde el tamaño de las mismas viene determinado por la ocurrencia de la palabra';
      text = text + '. Estas palabras fueron tomadas de los tweets de las cuentas que mencionaron a @Miguel_pizarro en los últimos 7 días,'
      text = text + ' de cada una de estas cuentas se tomaron 10 tweets.'
      $("#info-text").text(text);
      break;
    case "1":
      drawBubbleChart('./csv/filtered_words_search_api.csv');
      var text = 'Se muestra un gráfico de burbujas en donde el tamaño de las mismas viene determinado por la ocurrencia de la palabra';
      text = text + '. Estas palabras fueron tomadas de los tweets que mencionaron a @Miguel_pizarro en los últimos 7 días.'
      $("#info-text").text(text);
      break;
    case "2":
      drawBubbleChart('./csv/filtered_words_hashtags_search_api.csv');
      var text = 'Se muestra un gráfico de burbujas en donde el tamaño de las mismas viene determinado por la ocurrencia de la palabra';
      text = text + '. Estos hashtags fueron tomados de los tweets que mencionaron a @Miguel_pizarro en los últimos 7 días.'
      $("#info-text").text(text);
      break;
    case "3":
      drawBubbleChart('./csv/filtered_ngrams_search_api.csv');
      var text = 'Se muestra un gráfico de burbujas en donde el tamaño de las mismas viene determinado por la ocurrencia de las agrupaciones';
      text = text + ' de palabras. Estos agrupaciones fueron tomadas de los tweets que mencionaron a @Miguel_pizarro en los últimos 7 días.'
      $("#info-text").text(text);
      break;
  }
});

