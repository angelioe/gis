

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

//------INPUTS-----//
int i1pin = 0;
int i2pin = 2;
int i3pin = 4;
int i4pin = 5;
int i5pin = 15;
int i6pin = 16;
//-----------------//
int si1 = 0;
int si2 = 0;
int si3 = 0;
int si4 = 0;
int si5 = 0;
int si6 = 0;
//-----------------//
int lsi1 = HIGH;
int lsi2 = HIGH;
int lsi3 = HIGH;
int lsi4 = HIGH;
int lsi5 = HIGH;
int lsi6 = HIGH;
//-----------------//

//-----OUTPUTS-----//
int o1pin = 12;
int o2pin = 14;
int o3pin = 13;
//-----------------//
int so1 = 0;
int so2 = 0;
int so3 = 0;
//-----------------//

bool flag1 = true;
bool flag2 = true;
bool flag3 = true;
bool flag4 = true;
bool flag5 = true;
bool flag6 = true;

bool emergency = false;

char* topic = "angel/wifi";
const char *ssid =  "Angel";
const char *pass =  "adnkevaa";


IPAddress server(192, 168, 0, 100);
WiFiClient wclient05;
PubSubClient client(wclient05, server,1883);

void callback(const MQTT::Publish& pub) {
  String command = pub.payload_string();
  
  //----------------------------OUTPUT'S MESSAGES------------------------//
  if(pub.payload_string()==WiFi.macAddress()+";"+"c"+";"+"o1"+";"+"on"){ // OUT 1
    digitalWrite (o1pin, LOW);
    so1=HIGH;
    client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o1"+";"+"on");}
  if(pub.payload_string()==WiFi.macAddress()+";"+"c"+";"+"o1"+";"+"off"){
    digitalWrite (o1pin, HIGH);
    so1=LOW;
    client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o1"+";"+"off");}
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"o1"+";"+"x"){
    if(so1==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o1"+";"+"on");
    if(so1==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o1"+";"+"off");}
    
  if(pub.payload_string()==WiFi.macAddress()+";"+"c"+";"+"o2"+";"+"on"){ // OUT 2
    digitalWrite (o2pin, LOW);
    so2=HIGH;
    client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o2"+";"+"on");}
  if(pub.payload_string()==WiFi.macAddress()+";"+"c"+";"+"o2"+";"+"off"){
    digitalWrite (o2pin, HIGH);
    so2=LOW;
    client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o2"+";"+"off");}
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"o2"+";"+"x"){
    if(so2==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o2"+";"+"on");
    if(so2==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o2"+";"+"off");}
    
  if(pub.payload_string()==WiFi.macAddress()+";"+"c"+";"+"o3"+";"+"on"){ // OUT 3
    digitalWrite (o3pin, LOW);
    so3=HIGH;
    client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o3"+";"+"on");}
  if(pub.payload_string()==WiFi.macAddress()+";"+"c"+";"+"o3"+";"+"off"){
    digitalWrite (o3pin, HIGH);
    so3=LOW;
    client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o3"+";"+"off");}
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"o3"+";"+"x"){
    if(so3==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o3"+";"+"on");
    if(so3==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"o3"+";"+"off");}

  //---------------------------------------------------------------------//
  //---------------------------INPUT-------------------------------------//
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"i1"+";"+"x"){
    if(si1==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i1"+";"+"off");
    if(si1==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i1"+";"+"on");}
      
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"i2"+";"+"x"){
    if(si2==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i2"+";"+"off");
    if(si2==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i2"+";"+"on");}
      
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"i3"+";"+"x"){
    if(si3==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i3"+";"+"off");
    if(si3==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i3"+";"+"on");}
      
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"i4"+";"+"x"){
    if(si4==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i4"+";"+"off");
    if(si4==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i4"+";"+"on");}
      
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"i5"+";"+"x"){
    if(si5==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i5"+";"+"off");
    if(si5==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i5"+";"+"on");}
      
  if(pub.payload_string()==WiFi.macAddress()+";"+"s"+";"+"i6"+";"+"x"){
    if(si6==HIGH)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i6"+";"+"off");
    if(si6==LOW)
      client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i6"+";"+"on");}

  //---------------------------------------------------------------------//

   
}

void setup() {

  pinMode (o1pin, OUTPUT);
  pinMode (o2pin, OUTPUT);
  pinMode (o3pin, OUTPUT);
  
  pinMode (i1pin, INPUT);
  pinMode (i2pin, INPUT);
  pinMode (i3pin, INPUT);
  pinMode (i4pin, INPUT);
  pinMode (i5pin, INPUT);
  pinMode (i6pin, INPUT);
    
  digitalWrite (o1pin, HIGH);
  digitalWrite (o2pin, HIGH);
  digitalWrite (o3pin, HIGH);

}

void loop() {
  
  si1 = digitalRead(i1pin);
  si2 = digitalRead(i2pin);
  si3 = digitalRead(i3pin);
  si4 = digitalRead(i4pin);
  si5 = digitalRead(i5pin);
  si6 = digitalRead(i6pin);

  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, pass);
    if (WiFi.waitForConnectResult() != WL_CONNECTED){
      return;}
  }

  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      if (client.connect("Client05")) {
        client.set_callback(callback);
        client.subscribe(topic);
        client.publish(topic, "Check check check: " + WiFi.macAddress());
      }
    }
    if (client.connected()){
      if (si1 != lsi1) {
        if (si1 == LOW && flag1){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i1"+";"+"on");
          lsi1=LOW;
          flag1=false;}
        if (si1 == HIGH && !flag1){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i1"+";"+"off");
          lsi1=HIGH;
          flag1=true;}}
    
      if (si2 != lsi2) {
        if (si2 == LOW && flag2){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i2"+";"+"on");
          lsi2=LOW;
          flag2=false;}
        if (si2 == HIGH && !flag2){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i2"+";"+"off");
          lsi2=HIGH;
          flag2=true;}}

      if (si3 != lsi3) {
        if (si3 == LOW && flag3){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i3"+";"+"on");
          lsi3=LOW;
          flag3=false;}
        if (si3 == HIGH && !flag3){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i3"+";"+"off");
          lsi3=HIGH;
          flag3=true;}}
          
      if (si4 != lsi4) {
        if (si4 == LOW && flag4){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i4"+";"+"on");
          lsi4=LOW;
          flag4=false;}
        if (si4 == HIGH && !flag4){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i4"+";"+"off");
          lsi4=HIGH;
          flag4=true;}}

      if (si5 != lsi5) {
        if (si5 == LOW && flag5){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i5"+";"+"on");
          lsi5=LOW;
          flag5=false;}
        if (si5 == HIGH && !flag5){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i5"+";"+"off");
          lsi5=HIGH;
          flag5=true;}}
          
      if (si6 != lsi6) {
        if (si6 == LOW && flag6){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i6"+";"+"on");
          lsi6=LOW;
          flag6=false;}
        if (si6 == HIGH && !flag6){
          client.publish(topic, WiFi.macAddress()+";"+"s"+";"+"i6"+";"+"off");
          lsi6=HIGH;
          flag6=true;}}

      
      client.loop();
      delay(500);  
    }

  }

  
   
}
