// /*
//  Smart Traffic Management System
//  Arduino Traffic Signal Controller
//  Commands format from Python:
//  NORTH_GREEN
//  NORTH_RED
//  SOUTH_GREEN
//  etc.
// */

// // -------------------------------
// // PIN CONFIGURATION
// // -------------------------------

// // North Signal
// #define N_RED 2
// #define N_YELLOW 3
// #define N_GREEN 4

// // South Signal
// #define S_RED 5
// #define S_YELLOW 6
// #define S_GREEN 7

// // East Signal
// #define E_RED 8
// #define E_YELLOW 9
// #define E_GREEN 10

// // West Signal
// #define W_RED 11
// #define W_YELLOW 12
// #define W_GREEN 13

// // -------------------------------

// String command = "";

// // -------------------------------
// void setup()
// {
//     Serial.begin(9600);

//     pinMode(N_RED, OUTPUT);
//     pinMode(N_YELLOW, OUTPUT);
//     pinMode(N_GREEN, OUTPUT);

//     pinMode(S_RED, OUTPUT);
//     pinMode(S_YELLOW, OUTPUT);
//     pinMode(S_GREEN, OUTPUT);

//     pinMode(E_RED, OUTPUT);
//     pinMode(E_YELLOW, OUTPUT);
//     pinMode(E_GREEN, OUTPUT);

//     pinMode(W_RED, OUTPUT);
//     pinMode(W_YELLOW, OUTPUT);
//     pinMode(W_GREEN, OUTPUT);

//     allRed(); // Safety default
//     Serial.println("Arduino Traffic Signal Ready");
// }

// // -------------------------------
// void loop()
// {
//     if (Serial.available())
//     {
//         command = Serial.readStringUntil('\n');
//         command.trim();
//         handleCommand(command);
//     }
// }

// // -------------------------------
// // COMMAND HANDLER
// // -------------------------------
// void handleCommand(String cmd)
// {

//     allRed(); // Safety: reset before setting new signal

//     if (cmd == "NORTH_GREEN")
//     {
//         digitalWrite(N_GREEN, HIGH);
//     }
//     else if (cmd == "NORTH_YELLOW")
//     {
//         digitalWrite(N_YELLOW, HIGH);
//     }
//     else if (cmd == "NORTH_RED")
//     {
//         digitalWrite(N_RED, HIGH);
//     }

//     else if (cmd == "SOUTH_GREEN")
//     {
//         digitalWrite(S_GREEN, HIGH);
//     }
//     else if (cmd == "SOUTH_YELLOW")
//     {
//         digitalWrite(S_YELLOW, HIGH);
//     }
//     else if (cmd == "SOUTH_RED")
//     {
//         digitalWrite(S_RED, HIGH);
//     }

//     else if (cmd == "EAST_GREEN")
//     {
//         digitalWrite(E_GREEN, HIGH);
//     }
//     else if (cmd == "EAST_YELLOW")
//     {
//         digitalWrite(E_YELLOW, HIGH);
//     }
//     else if (cmd == "EAST_RED")
//     {
//         digitalWrite(E_RED, HIGH);
//     }

//     else if (cmd == "WEST_GREEN")
//     {
//         digitalWrite(W_GREEN, HIGH);
//     }
//     else if (cmd == "WEST_YELLOW")
//     {
//         digitalWrite(W_YELLOW, HIGH);
//     }
//     else if (cmd == "WEST_RED")
//     {
//         digitalWrite(W_RED, HIGH);
//     }

//     Serial.print("Executed: ");
//     Serial.println(cmd);
// }

// // -------------------------------
// // SAFETY FUNCTION
// // -------------------------------
// void allRed()
// {
//     digitalWrite(N_RED, HIGH);
//     digitalWrite(S_RED, HIGH);
//     digitalWrite(E_RED, HIGH);
//     digitalWrite(W_RED, HIGH);

//     digitalWrite(N_YELLOW, LOW);
//     digitalWrite(N_GREEN, LOW);

//     digitalWrite(S_YELLOW, LOW);
//     digitalWrite(S_GREEN, LOW);

//     digitalWrite(E_YELLOW, LOW);
//     digitalWrite(E_GREEN, LOW);

//     digitalWrite(W_YELLOW, LOW);
//     digitalWrite(W_GREEN, LOW);
// }


// ------------------------------------------------------------------

/*
 Smart Traffic Management System
 Arduino Traffic Signal Controller
 Stable Version (No Serial Spam)
*/

// -------------------------------
// PIN CONFIGURATION
// -------------------------------
#define N_RED 2
#define N_YELLOW 3
#define N_GREEN 4

#define S_RED 5
#define S_YELLOW 6
#define S_GREEN 7

#define E_RED 8
#define E_YELLOW 9
#define E_GREEN 10

#define W_RED 11
#define W_YELLOW 12
#define W_GREEN 13

String command = "";

// -------------------------------
void setup()
{
    Serial.begin(9600);

    pinMode(N_RED, OUTPUT);
    pinMode(N_YELLOW, OUTPUT);
    pinMode(N_GREEN, OUTPUT);

    pinMode(S_RED, OUTPUT);
    pinMode(S_YELLOW, OUTPUT);
    pinMode(S_GREEN, OUTPUT);

    pinMode(E_RED, OUTPUT);
    pinMode(E_YELLOW, OUTPUT);
    pinMode(E_GREEN, OUTPUT);

    pinMode(W_RED, OUTPUT);
    pinMode(W_YELLOW, OUTPUT);
    pinMode(W_GREEN, OUTPUT);

    allRed(); // Safety default
}

// -------------------------------
void loop()
{
    if (Serial.available() > 0)
    {
        command = Serial.readStringUntil('\n');
        command.trim();

        if (command.length() > 0)
        {
            handleCommand(command);
        }
    }
}

// -------------------------------
void handleCommand(String cmd)
{

    allRed(); // Safety reset

    if (cmd == "NORTH_GREEN")
        digitalWrite(N_GREEN, HIGH);
    else if (cmd == "NORTH_YELLOW")
        digitalWrite(N_YELLOW, HIGH);
    else if (cmd == "NORTH_RED")
        digitalWrite(N_RED, HIGH);

    else if (cmd == "SOUTH_GREEN")
        digitalWrite(S_GREEN, HIGH);
    else if (cmd == "SOUTH_YELLOW")
        digitalWrite(S_YELLOW, HIGH);
    else if (cmd == "SOUTH_RED")
        digitalWrite(S_RED, HIGH);

    else if (cmd == "EAST_GREEN")
        digitalWrite(E_GREEN, HIGH);
    else if (cmd == "EAST_YELLOW")
        digitalWrite(E_YELLOW, HIGH);
    else if (cmd == "EAST_RED")
        digitalWrite(E_RED, HIGH);

    else if (cmd == "WEST_GREEN")
        digitalWrite(W_GREEN, HIGH);
    else if (cmd == "WEST_YELLOW")
        digitalWrite(W_YELLOW, HIGH);
    else if (cmd == "WEST_RED")
        digitalWrite(W_RED, HIGH);
}

// -------------------------------
void allRed()
{
    digitalWrite(N_RED, HIGH);
    digitalWrite(S_RED, HIGH);
    digitalWrite(E_RED, HIGH);
    digitalWrite(W_RED, HIGH);

    digitalWrite(N_YELLOW, LOW);
    digitalWrite(N_GREEN, LOW);

    digitalWrite(S_YELLOW, LOW);
    digitalWrite(S_GREEN, LOW);

    digitalWrite(E_YELLOW, LOW);
    digitalWrite(E_GREEN, LOW);

    digitalWrite(W_YELLOW, LOW);
    digitalWrite(W_GREEN, LOW);
}
