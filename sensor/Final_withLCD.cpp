#include <Arduino.h>
#include <NewPing.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ---------- Ultrasonic pins ----------
#define TRIGGER_PIN 33
#define ECHO_PIN 32
#define MAX_DISTANCE 400

// ---------- LCD (16x2 I2C) ----------
#define LCD_ADDR 0x27
#define LCD_COLS 16
#define LCD_ROWS 2

// ---------- Wi-Fi AP ----------
const char *AP_SSID = "Ultrasonic-ESP32";
const char *AP_PASS = "12345678";

// ---------- Sampling ----------
const unsigned long SAMPLE_INTERVAL_MS = 500;
const int MAX_POINTS = 240; // ~2 minutes at 500 ms

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);
WebServer server(80);

unsigned long lastSampleMs = 0;
unsigned int currentDistanceCm = 0;

unsigned int distanceHistory[MAX_POINTS];
unsigned long timeHistory[MAX_POINTS];
int pointsCount = 0;

String alertTextForDistance(unsigned int d) {
  if (d == 0) {
    return "No object / out rng";
  }
  if (d < 10) {
    return "RED ALERT (<10cm)";
  }
  if (d < 20) {
    return "YELLOW (10-19cm)";
  }
  return "SAFE";
}

void addHistoryPoint(unsigned int d, unsigned long t) {
  if (pointsCount < MAX_POINTS) {
    distanceHistory[pointsCount] = d;
    timeHistory[pointsCount] = t;
    pointsCount++;
    return;
  }

  // Shift left when buffer is full.
  for (int i = 1; i < MAX_POINTS; i++) {
    distanceHistory[i - 1] = distanceHistory[i];
    timeHistory[i - 1] = timeHistory[i];
  }
  distanceHistory[MAX_POINTS - 1] = d;
  timeHistory[MAX_POINTS - 1] = t;
}

void updateLcd(unsigned int d) {
  lcd.clear();
  lcd.setCursor(0, 0);
  if (d == 0) {
    lcd.print("Distance: -- cm");
  } else {
    lcd.print("Distance: ");
    lcd.print(d);
    lcd.print(" cm");
  }

  lcd.setCursor(0, 1);
  String alert = alertTextForDistance(d);
  if (alert.length() > LCD_COLS) {
    alert = alert.substring(0, LCD_COLS);
  }
  lcd.print(alert);
}

String makeJsonData() {
  String json = "{";
  json += "\"distance\":" + String(currentDistanceCm) + ",";
  json += "\"alert\":\"" + alertTextForDistance(currentDistanceCm) + "\",";
  json += "\"uptime\":" + String(millis()) + ",";

  json += "\"history\":[";
  for (int i = 0; i < pointsCount; i++) {
    if (i > 0) {
      json += ",";
    }
    json += "{";
    json += "\"t\":" + String(timeHistory[i]);
    json += ",\"d\":" + String(distanceHistory[i]);
    json += "}";
  }
  json += "]";
  json += "}";
  return json;
}

void handleRoot() {
  static const char html[] PROGMEM = R"rawliteral(
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Ultrasonic Dashboard</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; background:#10141b; color:#e8eefc; margin:0; padding:16px; }
    .card { background:#18202b; border:1px solid #2a3444; border-radius:12px; padding:16px; max-width:900px; margin:0 auto 16px; }
    h1 { margin:0 0 12px; font-size:22px; }
    .row { display:flex; gap:16px; flex-wrap:wrap; }
    .pill { padding:10px 12px; background:#111823; border-radius:10px; border:1px solid #2a3444; min-width:180px; }
    .value { font-size:24px; font-weight:700; }
    .small { color:#a9b4c9; font-size:13px; }
    .ok { color:#50d890; }
    .warn { color:#ffd166; }
    .danger { color:#ff6b6b; }
    canvas { width:100%; height:320px; background:#0f1520; border-radius:10px; border:1px solid #2a3444; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Ultrasonic Sensor Dashboard</h1>
    <div class="row">
      <div class="pill">
        <div class="small">Distance</div>
        <div id="distance" class="value">-- cm</div>
      </div>
      <div class="pill">
        <div class="small">Status</div>
        <div id="alert" class="value">Waiting...</div>
      </div>
      <div class="pill">
        <div class="small">ESP32 AP</div>
        <div class="value" style="font-size:16px;">Ultrasonic-ESP32</div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="small" style="margin-bottom:10px;">Distance over time</div>
    <canvas id="chart" width="860" height="320"></canvas>
  </div>

  <script>
    const distanceEl = document.getElementById('distance');
    const alertEl = document.getElementById('alert');
    const canvas = document.getElementById('chart');
    const ctx = canvas.getContext('2d');

    function setAlertStyle(text) {
      alertEl.className = 'value';
      if (text.includes('RED')) alertEl.classList.add('danger');
      else if (text.includes('YELLOW')) alertEl.classList.add('warn');
      else alertEl.classList.add('ok');
    }

    function drawChart(points) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const padL = 45, padR = 10, padT = 10, padB = 30;
      const w = canvas.width - padL - padR;
      const h = canvas.height - padT - padB;

      ctx.strokeStyle = '#2f3b4f';
      ctx.lineWidth = 1;
      for (let i = 0; i <= 4; i++) {
        const y = padT + (h * i / 4);
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(padL + w, y);
        ctx.stroke();
      }

      if (!points || points.length < 2) return;

      const minT = points[0].t;
      const maxT = points[points.length - 1].t;
      const spanT = Math.max(1, maxT - minT);
      const maxD = Math.max(50, ...points.map(p => p.d));

      ctx.strokeStyle = '#52a5ff';
      ctx.lineWidth = 2;
      ctx.beginPath();
      points.forEach((p, i) => {
        const x = padL + ((p.t - minT) / spanT) * w;
        const y = padT + h - ((p.d || 0) / maxD) * h;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      ctx.fillStyle = '#a9b4c9';
      ctx.font = '12px Segoe UI';
      ctx.fillText('0', 22, padT + h);
      ctx.fillText(String(maxD), 14, padT + 10);
      ctx.fillText('Time', padL + w - 30, canvas.height - 8);
      ctx.fillText('cm', 10, 18);
    }

    async function refresh() {
      try {
        const res = await fetch('/data');
        const data = await res.json();
        distanceEl.textContent = data.distance === 0 ? '-- cm' : `${data.distance} cm`;
        alertEl.textContent = data.alert;
        setAlertStyle(data.alert);
        drawChart(data.history || []);
      } catch (e) {
        console.error(e);
      }
    }

    refresh();
    setInterval(refresh, 1000);
  </script>
</body>
</html>
  )rawliteral";

  server.send(200, "text/html", html);
}

void handleData() {
  server.send(200, "application/json", makeJsonData());
}

void setup() {
  Serial.begin(115220);
  Wire.begin();

  // --- I2C Scanner ---
  Serial.println("\nScanning for I2C devices...");
  byte count = 0;
  for (byte i = 8; i < 120; i++) {
    Wire.beginTransmission(i);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found I2C device at: 0x");
      Serial.println(i, HEX);
      count++;
      delay(1);
    }
  }
  Serial.print("Found ");
  Serial.print(count);
  Serial.println(" device(s).");
  if (count == 0) {
    Serial.println("!!! NO I2C DEVICE FOUND. Please check wiring.");
  }
  // --- End Scanner ---

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Ultrasonic System");
  lcd.setCursor(0, 1);
  lcd.print("Starting...");

  WiFi.mode(WIFI_AP);
  bool apOk = WiFi.softAP(AP_SSID, AP_PASS);
  
  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.begin();

  IPAddress apIp = WiFi.softAPIP();

  Serial.println();
  Serial.println("=== ESP32 Hotspot ===");
  Serial.print("SSID: ");
  Serial.println(AP_SSID);
  Serial.print("PASS: ");
  Serial.println(AP_PASS);
  Serial.print("IP:   ");
  Serial.println(apIp);
  Serial.print("AP OK: ");
  Serial.println(apOk ? "YES" : "NO");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("AP: Ultrasonic-ESP32");
  lcd.setCursor(0, 1);
  lcd.print(apIp.toString());
  delay(2000);
}

void loop() {
  server.handleClient();

  unsigned long now = millis();
  if (now - lastSampleMs < SAMPLE_INTERVAL_MS) {
    return;
  }
  lastSampleMs = now;

  currentDistanceCm = sonar.ping_cm();
  addHistoryPoint(currentDistanceCm, now);
  updateLcd(currentDistanceCm);

  Serial.print(currentDistanceCm);
  Serial.print(",");
  Serial.println(now);
}