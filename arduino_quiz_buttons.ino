// Arduino Quiz Buttons -> Envía 'A','B','C','D' por Serial al presionar
// Cablea cada botón entre pin y GND. Usa INPUT_PULLUP (reposo en HIGH, pulsado LOW).

const int BTN_A = 2;
const int BTN_B = 3;
const int BTN_C = 4;
const int BTN_D = 5;

const unsigned long DEBOUNCE = 60; // ms
unsigned long tA=0, tB=0, tC=0, tD=0;
bool prevA=HIGH, prevB=HIGH, prevC=HIGH, prevD=HIGH;

void setup() {
  Serial.begin(9600);
  pinMode(BTN_A, INPUT_PULLUP);
  pinMode(BTN_B, INPUT_PULLUP);
  pinMode(BTN_C, INPUT_PULLUP);
  pinMode(BTN_D, INPUT_PULLUP);
}

void loop() {
  leerBoton(BTN_A, prevA, tA, 'A');
  leerBoton(BTN_B, prevB, tB, 'B');
  leerBoton(BTN_C, prevC, tC, 'C');
  leerBoton(BTN_D, prevD, tD, 'D');
}

void leerBoton(int pin, bool &prev, unsigned long &t, char letra) {
  bool estado = digitalRead(pin);
  if (estado != prev) {
    t = millis();
    prev = estado;
  }
  if (estado == LOW && (millis() - t) > DEBOUNCE) {
    // pulsado (flanco estable)
    Serial.println(letra);
    delay(250); // evita repeticiones por mantener pulsado
    // esperar a soltar
    while (digitalRead(pin) == LOW) { delay(10); }
  }
}
