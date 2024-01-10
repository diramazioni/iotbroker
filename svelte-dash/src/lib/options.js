export default {
  title: 'Line (time series)',
  points: {
		enabled: false
	},
  axes: {
    bottom: {
      title: 'Time sensor values',
      mapsTo: 'date',
      scaleType: 'time'
    },
    left: {
      mapsTo: 'value',
      title: 'Values',
      scaleType: 'linear'
    } 
  },
  legend : {
    position : "left",
    orientation : "vertical",
    alignment : "center"
  },
  curve: 'curveMonotoneX',
  experimental : true,
  zoomBar : {
    top : {
      enabled : true
    }
  },  
  height: '600px',
  //"resizable": true,
  // width: '200px'

  /*
data : {
selectedGroups : [
0 : "Dataset 1"
1 : "Dataset 3"]}
  */
}