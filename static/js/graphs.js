queue()
    .defer(d3.json, "/data")
    .await(makeGraphs);
'use strict';
function makeGraphs(error, recordsJson) {
	
	//Clean data
	var currentBalance = recordsJson[0][1];
	var availableResources = recordsJson[1][1];

	var dateFormat = d3.time.format("%m/%d/%Y %H:%M:%S");

	currentBalance.forEach(function(d) {
		d["timestamp"] = dateFormat.parse(d["timestamp"]);
	});

	//Create a Crossfilter instance
	var ndx = crossfilter(currentBalance);
	var ndx_source = crossfilter(availableResources)

	//Define Dimensions
	var dateDim = ndx.dimension(function(d) { return d["timestamp"]; });
	var typeDim = ndx.dimension(function(d) { return d["Type"]; });
	//console.log(typeDim);
	var hour = ndx.dimension(function(d){ return d.timestamp.getHours() + d.timestamp.getMinutes() / 60}),
	hours = hour.group(Math.floor);
	var allDim = ndx.dimension(function(d) {return d;});

	//Group Data
	var numRecordsByDate = dateDim.group();
	var typeGroup = typeDim.group();
	var all = ndx.groupAll();
    //console.log(hours);

	//Define values (to be used in charts)
	var minDate = dateDim.bottom(1)[0]["timestamp"];
	var maxDate = dateDim.top(1)[0]["timestamp"]  ;
    //console.log(minDate , maxDate);

    //Charts
    var numberRecordsND = dc.numberDisplay("#number-records-nd");
	var timeChart = dc.barChart("#time-chart");
	var cashChart = dc.compositeChart("#cash-chart"); //  for cash flow chart
	var typeChart = dc.rowChart("#type-row-chart");
	var pieChart = dc.pieChart("#pie-chart");
	var dataTable = dc.dataTable('.dc-data-table');

	numberRecordsND
		.formatNumber(d3.format("d"))
		.valueAccessor(function(d){return d; })
		.group(all);


	timeChart
		.width(1220)
		.height(340)
		.margins({top: 10, right: 50, bottom: 20, left: 40})
		.group(numRecordsByDate)
		.dimension(dateDim)
		.transitionDuration(2000)
		.x(d3.time.scale().domain([minDate, maxDate]))
		.elasticY(true)
		.yAxis().ticks(6);

	typeChart
        .width(300)
        .height(300)
        .dimension(typeDim)
        .group(typeGroup)
        .ordering(function(d) { return -d.value })
        .colors(['blue'])
        .elasticX(true)
        .xAxis().ticks(4);

     var    cashGroup = dateDim.group().reduceSum(dc.pluck('current_cash_balance')),
            cdsGroup = dateDim.group().reduceSum(dc.pluck('current_cds_balance')),
            savingsGroup = dateDim.group().reduceSum(dc.pluck('current_savings_balance')),
            loansGroup = dateDim.group().reduceSum(dc.pluck('current_loan_balance')),
            checkingGroup = dateDim.group().reduceSum(dc.pluck('current_checking_balance')),
            fedFundsGroup = dateDim.group().reduceSum(dc.pluck('current_fedfunds_balance'));
      //console.log(cdsDim)

      cashChart
        .width(1250)
        .height(480)
        .margins({top: 10, right: 50, bottom: 20, left: 40})
        .transitionDuration(1000)
        .x(d3.time.scale().domain([minDate, maxDate]))
        .yAxisLabel("Balance")
        .legend(dc.legend().x(80).y(20).itemHeight(13).gap(5))
        .renderHorizontalGridLines(true)
        .compose([
            dc.lineChart(cashChart)
                .dimension(dateDim)
                .colors('#e2431e')
                .group(cashGroup, "Cash")
                .dashStyle([2,2]),
            dc.lineChart(cashChart)
                .dimension(dateDim)
                .colors('#e7711b')
                .group(cdsGroup, "CDs"),
                //.dashStyle([5,5]),
            dc.lineChart(cashChart)
                .dimension(dateDim)
                .colors('#f1ca3a')
                .group(savingsGroup, "Savings"),
            dc.lineChart(cashChart)
                .dimension(dateDim)
                .colors('#6f9654')
                .group(loansGroup, "Loans"),
            dc.lineChart(cashChart)
                .dimension(dateDim)
                .colors('#1c91c0')
                .group(checkingGroup, "Checkings"),
            dc.lineChart(cashChart)
                .dimension(dateDim)
                .colors('#43459d')
                .group(fedFundsGroup, "Fed Funds")
            ])
        .brushOn(false)
        .mouseZoomable(true)
        .render();


        var chart = c3.generate({
            data: {
                columns: [
                   ["CD1", 25000],
                ["CD5", 11925],
                ["Checking", 15110],
                ["Savings", 17650],
                ["Fed Funds", 31500],
                ],
                type : 'donut',
                onclick: function (d, i) { console.log("onclick", d, i); },
                onmouseover: function (d, i) { console.log("onmouseover", d, i); },
                onmouseout: function (d, i) { console.log("onmouseout", d, i); }
            },
            donut: {
                title: "Funding Resources"
            }
        });

        setTimeout(function () {
            chart.load({
                columns: [
                  ["CD1", 25000 - 300],
                ["CD5", 27000 - 75],
                ["Checking", 35000 - 730],
                ["Savings", 30000- 1175 ],
                ["Fed Funds", 30000 ],
                ]
            });
        }, 1500);

         var dateDimension = ndx.dimension(function (d) {
        return d.dd;
    });
        dataTable /* dc.dataTable('.dc-data-table', 'chartGroup') */
        .dimension(dateDim)
        .size(10)
        .columns([
            "date",    //
            "open",    // ...
            "close"   // ...
    ]);



	dc.renderAll();

};
