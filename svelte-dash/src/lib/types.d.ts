interface WeatherStation {
  id: number;
  timestamp: string;
  Battery_Voltage: number;
  Solar_Panel_Voltage: number;
  Temperature: number;
  Pressure: number;
  Humidity: number;
  GasResistance: number;
  Altitude: number;
  Ts_1: number;
  Ts_2: number;
  Ts_3: number;
  Us_1: number;
  Us_2: number;
  Us_3: number;
  W_vel: number;
  W_dir: number;
  deviceId: number;
}

interface Device {
  id: number;
  name: string;
  calibration: null | number; 
  timestamp: bigint;
  weatherStation: WeatherStation;
}
