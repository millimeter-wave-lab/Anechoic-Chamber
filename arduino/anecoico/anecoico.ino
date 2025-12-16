// Include the AccelStepper Library
#include <AccelStepper.h>

// Define pin connections //Arduino UNO // Ardunio NANO
const int DirPin = 7;   // 7          // 7
const int StepPin = 4;  // 4          // 8

// Define motor interface type
#define motorInterfaceType 1

// Creates an instance per stepper
AccelStepper AntennaStepper(motorInterfaceType, StepPin, DirPin);

// Define stepper reduction
const int StepperReduction = 60;

// Rescaling for resolution
const int resolutionRescale = 100;

// Variable for defining reduction
int targetReduction = 0;

// Define steps for 360 loop
const int stepsPerLoop = 200;

// Define serial comm constants
const byte numChars = 32;
char receivedChars[numChars];
int receivedLength;

// Define variable for received commands
char recvCmd[numChars/2];
char recvTargetMotor[numChars/8];
int recvTargetMotorLength;
int recvCmdLength;
char recvCmdData[numChars/2];

int recvCmdDataLength;
// Varialbe for received data
boolean newData = false;

void setup() {
  // set the maximum speed, acceleration factor,
  // initial speed and the target position
  //azStepper.setMaxSpeed(200);
  //azStepper.setAcceleration(200);
  //azStepper.setSpeed(60);
  //elStepper.setMaxSpeed(200);
  //elStepper.setAcceleration(200);
  //elStepper.setSpeed(60);
  Serial.begin(115200);
  pinMode(9, OUTPUT);    // sets the digital pin 9 as output
  digitalWrite(9, LOW);
  //Serial.println("<Arduino is ready>");
  //myStepper.moveTo(200);
  //calibration(myStepper, 1);
  //azStepper.moveTo(200);
  //pinMode(LS1Pin, INPUT_PULLUP);
  
}

void loop() {
  // Change direction once the motor reaches target position
  //if (myStepper.distanceToGo() == 0) 
  //  myStepper.moveTo(-myStepper.currentPosition());

  // Move the motor one step
  //myStepper.run();
  //recvWithStartEndMarkers();
  //showNewData();
   // Waits until the LS is pressed

  //int sensorVal = digitalRead(LS1Pin);
    //delay(anglePollingTimeMs);
  //if (sensorVal == LOW){
  //  myStepper.stop();
  //}

  // Stop the motor
  recvWithStartEndMarkers();
  translateMsg();
  readCommand();
  AntennaStepper.run();
  
}

void readCommand(){
  AccelStepper *targetMotor;
  if(newData == true){
    // Checking target motor
    int targetMotorNumber = atoi(recvTargetMotor);
    if (targetMotorNumber == 1){
       targetMotor = &AntennaStepper;
       targetReduction = StepperReduction;       
    }
    else{
     Serial.println("Motor does not exist");
    }
    // Checking commands
    if (strcmp(recvCmd,"stop")==0){
     stopMotor(*targetMotor);
     Serial.println("<"+String(targetMotorNumber)+"-ok:stop>");
    }
    else if (strcmp(recvCmd,"move")==0){
     float targetAngle = atof(recvCmdData);
     long targetSteps = angleToSteps(targetAngle);
     moveMotor(*targetMotor, targetSteps);
     Serial.println("<"+String(targetMotorNumber)+"-ok:move-"+String(targetAngle)+">");
    }
    else if (strcmp(recvCmd,"setspd")==0){
     int targetSpeed = atoi(recvCmdData);
     setMotorSpeed(*targetMotor, targetSpeed); 
     Serial.println("<"+String(targetMotorNumber)+"-ok:setspd-"+String(targetSpeed)+">");
    }
    else if (strcmp(recvCmd,"setmaxspd")==0){
     int targetMaxSpeed = atoi(recvCmdData);
     setMotorMaxSpeed(*targetMotor, targetMaxSpeed);
     Serial.println("<"+String(targetMotorNumber)+"-ok:setmaxspd-"+String(targetMaxSpeed)+">");
    }
    else if (strcmp(recvCmd,"setacc")==0){
     int targetAcceleration = atoi(recvCmdData);
     setMotorAcceleration(*targetMotor, targetAcceleration);
     Serial.println("<"+String(targetMotorNumber)+"-ok:setacc-"+String(targetAcceleration)+">");
    }
    else if (strcmp(recvCmd,"rst")==0){
     resetMotorSettings(*targetMotor);
     Serial.println("<"+String(targetMotorNumber)+"-ok:rst>");
    }
    else if (strcmp(recvCmd,"rdangle")==0){
      float angle = readAngle(*targetMotor);
      Serial.println("<"+String(targetMotorNumber)+"-ok:"+String(angle)+">");
    }
    newData = false;  
  }   
}
void setMotorSpeed(AccelStepper &stepper, int targetSpeed){
  stepper.setSpeed(targetSpeed);
  //Serial.println("<Set target speed to>");
  //Serial.println(targetSpeed);
  
}
void setMotorMaxSpeed(AccelStepper &stepper, int targetMaxSpeed){
  stepper.setMaxSpeed(targetMaxSpeed);
}
void setMotorAcceleration(AccelStepper &stepper, int targetAcceleration){
  stepper.setAcceleration(targetAcceleration);
}

void stopMotor(AccelStepper &stepper){
  stepper.stop();
}
void moveMotor(AccelStepper &stepper,long targetStep){
  stepper.moveTo(targetStep);
}
void resetMotorSettings(AccelStepper &stepper){
  stepper.setMaxSpeed(40);
  stepper.setAcceleration(200);
  stepper.setSpeed(20);
}

long angleToSteps(float angle){
  long steps = round(angle/360*stepsPerLoop*targetReduction);
  return steps;
}

float stepsToAngle(long steps){
  float angle = steps*360.0/stepsPerLoop/targetReduction;
  return angle;
}

float readAngle(AccelStepper &stepper){
  long steps = stepper.currentPosition();
  float angle = stepsToAngle(steps);
  return angle;
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                receivedLength = ndx;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void translateMsg(){
  // Translates message in the following structure:
  // recvTargetMotor-recvCmd:recvCmdData
  
  if (newData == true){
    char motorLimiter = '-';
    char cmdLimiter = ':';
    boolean reachedMotorLimiter = false;
    boolean reachedCmdLimiter = false;
    for (int i = 0; i < receivedLength; i++){
      if (reachedMotorLimiter == false){
        if (receivedChars[i]== motorLimiter){
            reachedMotorLimiter = true;
            recvTargetMotor[i] = '\0';
            recvTargetMotorLength = i;
        }
        else{
          recvTargetMotor[i] = receivedChars[i];
        }
      }
      else{
        if (reachedCmdLimiter == false){
          if (receivedChars[i]== cmdLimiter){
            reachedCmdLimiter = true;
            recvCmd[i-recvTargetMotorLength-1] = '\0';
            recvCmdLength = i-recvTargetMotorLength-1;
          }
          else{
            recvCmd[i-recvTargetMotorLength-1] = receivedChars[i];
          }
        }
        else{
          recvCmdData[i-recvTargetMotorLength-1-recvCmdLength-1]= receivedChars[i];
          
          if (i == receivedLength - 1){
            recvCmdData[i+1-recvTargetMotorLength-1-recvCmdLength-1] = '\0';
            reachedCmdLimiter = false;
          }
        }
      }
    }
  }
  
}

void showNewData() {
    if (newData == true) {
        Serial.print("Received:");
        Serial.println(receivedChars);
        Serial.print("Received data length:");
        Serial.println(receivedLength);
        Serial.print("Received target motor:");
        Serial.println(recvTargetMotor);
        Serial.print("Received cmd:");
        Serial.println(recvCmd);
        Serial.print("Received cmd data:");
        Serial.println(recvCmdData);
        
        newData = false;
    }
}
