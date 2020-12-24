#include "Servomotor_control.h"
/******************************************************************************
* 舵机PID
*******************************************************************************/
int servo_piderror[2];//当前偏差e(n)
int servo_piderror_last[2];//上一次的偏差e(n-1)
int servo_piderror_last[2];//上一次的偏差e(n-1)
float servo_kp[2] = {1.0,2.0};         //3 ， 0 ， 5 , 0 , 0 , 0 
float servo_ki[2] = {0,0};
float servo_kd[2] = {0.0,4.0};
int servo_final_speed[2];
float p_gyro = 0.001;
int inside_pid(int target_in){
  	servo_piderror[0] = target_in;		                //E(n)
        servo_final_speed[0] = (int)(servo_kp[0]*(servo_piderror[0]) + servo_kd[0]*(servo_piderror[0] - servo_piderror_last[0]));	
	servo_piderror_last[0] = servo_piderror[0];		//更新误差值
        return servo_final_speed[0];
}
int outside_pid(int target_out){
        servo_piderror[1] = target_out + p_gyro * icm_gyro_z;		//E(n)
        servo_final_speed[1] = (int)(servo_kp[1]*servo_piderror[1]) + servo_kd[1]*(servo_piderror[1] - servo_piderror_last[1]);
	servo_piderror_last[1] = servo_piderror[1];
        return servo_final_speed[1];
}

extern float mid_in;
extern int crossroad;
extern int hill;
extern float mid_servomotor;
extern float predict_mid_error_servomotor;
extern float Range_Limit(float value, float range);
int servo_output = Servo_mid;
void Servomotor_control(){
  
    if(crossroad == 0){
      servo_output = Servo_mid - outside_pid( inside_pid(mid_servomotor + predict_mid_error_servomotor) );
    }
    if(crossroad == 1){
      servo_output = Servo_mid - outside_pid( inside_pid(mid_servomotor) );
    }
    if(hill != 0){
      servo_output = Servo_mid - outside_pid( inside_pid(mid_servomotor) );
    }
    
    //限幅
    if (servo_output > Servo_left){servo_output = Servo_left;}
    if (servo_output < Servo_right){servo_output = Servo_right;}
  
    pwm_duty(MOTOR_DJ, servo_output);
  
}