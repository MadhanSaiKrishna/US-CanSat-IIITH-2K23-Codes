// Updating table values
function updateData(data) {
  document.getElementById("mission_time").innerHTML = data["mission_time"]
  document.getElementById("packet_count").innerHTML = data["packet_count"]
  document.getElementById("mode").innerHTML = data["mode"]
  document.getElementById("state").innerHTML = data["state"]
  document.getElementById("heat_shield").innerHTML = data["HS_deployed"]
  document.getElementById("parachute").innerHTML = data["PC_deployed"]
  document.getElementById("gps_time").innerHTML = data["GPS_time"]
  document.getElementById("gps_latitude").innerHTML = data["GPS_latitude"]
  document.getElementById("gps_longitude").innerHTML = data["GPS_longitude"]
  document.getElementById("gps_satellites").innerHTML = data["GPS_sats"]
  document.getElementById("tilt_x").innerHTML = data["tiltX"]
  document.getElementById("tilt_y").innerHTML = data["tiltY"]
  document.getElementById("rotation_z").innerHTML = data["rotZ"]
  document.getElementById("command_echo").innerHTML = data["command_echo"]
  document.getElementById("optional_data").innerHTML = data["optional_data"]
  document.getElementById("CX_btn").innerHTML = data["CX_btn"]
  document.getElementById("BCN_btn").innerHTML = data["BCN_btn"]
}


// Plotting charts
const titles = [
  "Altitude (m) vs Mission time",
  "Air Speed (m/s) vs Mission time",
  "Temperature (°C) vs Mission Time",
  "Pressure (kPa) vs Mission Time",
  "Voltage (V) vs Mission Time",
  "GPS_altitude (m) vs Mission Time",
];

const chartIDs = [
  "myChart_alt",
  "myChart_air_speed",
  "myChart_temperature",
  "myChart_pressure",
  "myChart_voltage",
  "myChart_GPS_altitude",
];

let xValues = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
let alt_Values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
let air_speed_Values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
let temperature_Values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
let pressure_Values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
let voltage_Values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
let GPS_altitude_Values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

let yValues = [
  alt_Values,
  air_speed_Values,
  temperature_Values,
  pressure_Values,
  voltage_Values,
  GPS_altitude_Values,
];

let myChart = [0,0,0,0,0,0];

for (let i = 0; i < 6; i++) {
  let config = {
    type: "line",
    data: {
      labels: xValues,
      datasets: [
        {
          backgroundColor: "rgba(40,100,55,1.0)",
          borderColor: "rgba(0,0,0,0.6)",
          data: yValues[i],
        },
      ],
    },

    options: {
      plugins: {
        title: {
          display: true,
          text: titles[i],
          fontSize: 20,
        },
        legend: {
          display: false,
        },
      },

      scales: {
        x: {
          title: {
            beginAtZero: true,
            display: true,
            text: "Mission Time",
          },
        },
        y: {
          title: {
            beginAtZero: true,
            display: true,
            text: titles[i].split("vs")[0],
          },
        },
      },
    },
  };

  myChart[i] = new Chart(document.getElementById(chartIDs[i]), config);
}


// Fetching data from server every second and updating tables, charts
setInterval(function () {
  fetch("/data_json")
    .then(response => response.json())
    .then(data => {
        updateData(data);

        xValues = data["xValues"];
        alt_Values = data["alt_Values"];
        air_speed_Values = data["air_speed_Values"];
        temperature_Values = data["temperature_Values"];
        pressure_Values = data["pressure_Values"];
        voltage_Values = data["voltage_Values"];
        GPS_altitude_Values = data["gps_altitude_Values"];
        
        // console.log(GPS_altitude_Values)

        yValues = [
          alt_Values,
          air_speed_Values,
          temperature_Values,
          pressure_Values,
          voltage_Values,
          GPS_altitude_Values,
        ];
        
        for (let i = 0; i < 6; i++) {
            myChart[i].data.labels = xValues;
            myChart[i].data.datasets[0].data = yValues[i];
            myChart[i].update();
        }
        // console.log(data)
      }
    );
  }, 1000);

setInterval(function (){
  fetch("/SIMP_call").then(response => response.json())
}, 1000);