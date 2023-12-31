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
}