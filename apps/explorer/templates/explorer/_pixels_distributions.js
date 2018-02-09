{% load i18n %}

<script src="//www.gstatic.com/charts/loader.js"></script>
<script src="//ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script type="text/javascript">
  google.charts.load('current', {'packages':['corechart']});
  google.charts.setOnLoadCallback(drawCharts);

  function drawCharts() {
    var valuesChart = new google.visualization.Histogram(document.getElementById('values-histogram'));
    var scoresChart = new google.visualization.Histogram(document.getElementById('scores-histogram'));

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
    });
  }
</script>
