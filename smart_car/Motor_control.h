#ifndef _MOTOR_CONTROL_H
#define _MOTOR_CONTROL_H

#include "headfile.h"
#include "hardware_init.h"
#include "Misc.h"

int PID0(int target_speed0);
int PID1(int target_speed1);
int PID_STOP(int target_speed);
int motor_inside_pid(int motor_target_in);
int motor_outside_pid(int motor_target_out);
int16 Limit_range(int16 value, int16 range);
void motor_output();
void speed_Set();
#endif