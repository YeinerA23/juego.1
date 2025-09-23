// Arduino Quiz - 5 verdes y 5 rojos
// Botones en pines 2-5 (INPUT_PULLUP)
// Luces verdes: 6-10, Luces rojas: 11-15 (5 en total cada color)

const int BTN_A = 2;
const int BTN_B = 3;
const int BTN_C = 4;
const int BTN_D = 5;

const int verdes[5] = {6, 7, 8, 9, 10};
const int rojos[5]  = {11, 12, 13, A0, A1}; // A0 y A1 como pines digitales

const unsigned long DEBOUNCE = 80;
unsigned long lastPress = 0;

void setup() {
  Serial.begin(9600);

  pinMode(BTN_A, INPUT_PULLUP);
  pinMode(BTN_B, INPUT_PULLUP);
  pinMode(BTN_C, INPUT_PULLUP);
  pinMode(BTN_D, INPUT_PULLUP);

  // Inicializar LEDs
  for (int i = 0; i < 5; i++) {
    pinMode(verdes[i], OUTPUT);
    pinMode(rojos[i], OUTPUT);
    digitalWrite(verdes[i], LOW);
    digitalWrite(rojos[i], LOW);
  }

  Serial.println("ARDUINO READY");
}

void loop() {
  // --- Enviar pulsaciones ---
  if (millis() - lastPress > DEBOUNCE) {
    if (digitalRead(BTN_A) == LOW) { Serial.println("A"); lastPress = millis(); }
    if (digitalRead(BTN_B) == LOW) { Serial.println("B"); lastPress = millis(); }
    if (digitalRead(BTN_C) == LOW) { Serial.println("C"); lastPress = millis(); }
    if (digitalRead(BTN_D) == LOW) { Serial.println("D"); lastPress = millis(); }
  }

  // --- Recibir comandos ---
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toUpperCase();

    if (cmd == "CORRECTO") {
      Serial.println("✅ Respuesta CORRECTA -> Verdes ON");
      encenderGrupo(verdes);
    }
    else if (cmd == "INCORRECTO") {
      Serial.println("❌ Respuesta INCORRECTA -> Rojos ON");
      encenderGrupo(rojos);
    }
  }
}

// --- Función para encender un grupo de 5 LEDs ---
void encenderGrupo(const int pines[5]) {
  for (int i = 0; i < 5; i++) {
    digitalWrite(pines[i], HIGH);
  }
  delay(1000);
  for (int i = 0; i < 5; i++) {
    digitalWrite(pines[i], LOW);
  }
}

