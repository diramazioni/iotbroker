export const IBM_palette_light = [
	'#6929c4', // 01. Purple 70
	'#1192e8', // 02. Cyan 50
	'#005d5d', // 03. Teal 70
	'#9f1853', // 04. Magenta 70
	'#fa4d56', // 05. Red 50
	'#570408', // 06. Red 90
	'#198038', // 07. Green 60
	'#80002d', // 08. Blue 80
	'#ee538b', // 09. Magenta 50
	'#b28600', // 10. Yellow 50
	'#009d9a', // 11. Teal 50
	'#900127', // 12. Cyan 90
	'#8a3800', // 13. Orange 70
	'#a56eff' // 14. Purple 50
]

export const IBM_palette_dark = [
	'#8a3ffc', // 01. Purple 60
	'#33b1ff', // 02. Cyan 40
	'#007d79', // 03. Teal 60
	'#ff7eb6', // 04. Magenta 40
	'#fa4d56', // 05. Red 50
	'#fff1f1', // 06. Red 10
	'#6fdc8c', // 07. Green 30
	'#4589ff', // 08. Blue 50
	'#d12771', // 09. Magenta 60
	'#d2a106', // 10. Yellow 40
	'#08bdba', // 11. Teal 40
	'#bae6ff', // 12. Cyan 20
	'#ba4e00', // 13. Orange 60
	'#d4bbff' // 14. Purple 30
]

// input: h in [0,360] and s,v in [0,1] - output: r,g,b in [0,1]
export function hsv2rgb(h,s,v) {                              
  let f= (n,k=(n+h/60)%6) => v - v*s*Math.max( Math.min(k,4-k,1), 0);     
  return [f(5),f(3),f(1)];       
}   

// r,g,b are in [0-1], result e.g. #0812fa.
let rgb2hex = (r,g,b) => "#" + [r,g,b].map(x=>Math.round(x*255).toString(16).padStart(2,0) ).join('');

// hexStr e.g #abcdef, result "rgb(171,205,239)"
let hexStr2rgb  = (hexStr) => `rgb(${hexStr.substr(1).match(/../g).map(x=>+`0x${x}`)})`;

// rgb - color str e.g."rgb(12,233,43)", result color hex e.g. "#0ce92b"
let rgbStrToHex= rgb=> '#'+rgb.match(/\d+/g).map(x=>(+x).toString(16).padStart(2,0)).join``
