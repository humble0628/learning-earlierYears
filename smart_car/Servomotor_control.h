#ifndef _SERVOMOTOR_CONTROL_H
#define _SERVOMOTOR_CONTROL_H

#include "headfile.h"
#include "hardware_init.h"
#include "Misc.h"

#define MOTOR_DJ   PWM4_MODULE2_CHA_C30   //定义2电机反转PWM引脚
#define Servo_left      4300    //备用:3800  主:4300
#define Servo_mid       3900    //备用:3400  主:3900
#define Servo_right     3500    //备用:3000  主:3500

void Servomotor_control();
int inside_pid(int target_in);
int outside_pid(int target_out);

#endif