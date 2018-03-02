{% load i18n %}

(function ($, document, google) {
  var $valuesContainer = document.getElementById('{{ id_values|default:"values-histogram" }}');
  var $scoresContainer = document.getElementById('{{ id_scores|default:"scores-histogram" }}');

  var valuesChart = new google.visualization.Histogram($valuesContainer);
  var scoresChart = new google.visualization.Histogram($scoresContainer);

  $.get('{{ url_values }}', function (data) {
    valuesChart.draw(
      new google.visualization.DataTable(data),
      {
        colors: ['#bd2222'],
        height: 300,
        legend: { position: 'none' },
        title: '{% trans "Values" %}',
      }
    );
  }).fail(function () {
    $valuesContainer.textContent = '{% trans "An error occured while loading this chart." %}';
  });

  $.get('{{ url_scores }}', function (data) {
    scoresChart.draw(
      new google.visualization.DataTable(data),
      {
        height: 300,
        legend: { position: 'none' },
        title: '{% trans "Quality scores" %}',
      }
    );
  }).fail(function () {
    $scoresContainer.textContent = '{% trans "An error occured while loading this chart." %}';
  });
})($, document, google);
