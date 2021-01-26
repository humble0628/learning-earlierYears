#include "Get_line.h"

/*
    电磁提线部分
    根据采集到的电感值进行结算，对赛道信息进行分析。
		1.通过普通方法进行提线
		2.根据神经网络方法进行提线
*/
extern uint16 peak_max[15];
extern uint16 peak[AdcNum];
extern uint8 flag_1, flag_2;
int cross_in_flag , cross_count , cross_out_flag;

//------------------------------------//
//--------------保护程序--------------//
int forced_stop;  //强制停车标志

void protect(void)   
{
		if(peak[0] < 10 && peak[2] < 10 && peak[4] < 10)//当电感值都小于一定值时触发保护程序
		{
				forced_stop = 1;
		}
}



//------------------------------------//
//--------------提线程序--------------//

int x[5];   //拟合的电感数组从左到右分别为0，1，2（推算出来的0位置），3，4
float rudder_error, motor_error;	

int right_island_flag ,left_island_flag, normal_track_flag, cross_flag, downslope_flag, slope_flag;
int speed_flag;

int speed_up_flag, speed_up_count, speed_down_flag;

//1.通过普通方法进行提线

uint8 send_array[11];  //通过串口发送数据

int peak_mid_1st, peak_mid_2nd;
float error_k_1st, error_k_2nd;
float peak_across_sub_1st, peak_across_add_1st, peak_vertical_sub_1st, peak_vertical_add_1st;
float peak_across_sub_2nd, peak_across_add_2nd, peak_vertical_sub_2nd, peak_vertical_add_2nd;
float error_across1_1st, error_vertical_1st;
float error_across1_2nd, error_vertical_2nd;
float error_1st, error_2nd;
int peak_mid2;

void island_judge(void)
{
    peak_mid2 = 150;
//**************************************国赛赛道十字特殊处理*****************************************//	
	  if(peak[1]>125&&peak[3]>125)cross_in_flag = 1;
		if(cross_in_flag == 1)cross_count++;
		if(cross_count>150 && peak[1]>125 && peak[3]>125 && cross_in_flag == 1)		
		{
				cross_out_flag = 1;
		}
		if(cross_count>250 && peak[1]<80  &&  peak[3]<80 && cross_out_flag == 1)		
		{
				cross_in_flag = 0;
				cross_count = 0;
		}

	
//****************************************十字特殊处理**********************************//	
  if ((peak[1]>(peak_mid2*0.5)&&peak[3]>(peak_mid2*0.5)&&peak[2]>(peak_mid2*0.8))||(cross_flag==1&&peak[6]>(peak_mid2*0.5)&&peak[8]>(peak_mid2*0.5)))   //十字
	{ //十字
			cross_flag=1;
			normal_track_flag = 0;
	}
	//*****************************************环岛特殊处理***************************************//
	else if((peak[0]>(peak_mid2*0.37)&&peak[2]>(peak_mid2*1.07)&&peak[4]>(peak_mid2*0.5)&&left_island_flag==0 && (peak[3]-peak[1])>12) || (right_island_flag==1&&(peak[7]>=(peak_mid2*1.07)||peak[2]>=(peak_mid2*1.07))))  
	{	//右环岛
			right_island_flag = 1;
			normal_track_flag = 0;
  }
	else if((peak[0]>(peak_mid2*0.5)&&peak[2]>(peak_mid2*1.07)&&peak[4]>(peak_mid2*0.37) &&right_island_flag ==0)  ||  (left_island_flag==1&&(peak[7]>=(peak_mid2*1.07)||peak[2]>=(peak_mid2*1.07))) )
  {	//左环岛
			left_island_flag = 1;
			normal_track_flag = 0;
  }
	else 
	{	//正常
			normal_track_flag = 1;
	}
		
	
	if(left_island_flag ==1&&peak[7]<(peak_mid2*1.07)&&peak[2]<(peak_mid2*1.07))  
	{
			left_island_flag = 0;
	}
	if(right_island_flag ==1&&peak[7]<(peak_mid2*1.07)&&peak[2]<(peak_mid2*1.07))  
	{
			right_island_flag  = 0;
	}	
	
	if(cross_flag==1&&peak[6]<(peak_mid2*0.47)&&peak[8]<(peak_mid2*0.47)&&peak[1]<(peak_mid2*0.47)&&peak[3]<(peak_mid2*0.47))
	{
			cross_flag = 0;
	}
	
}


void get_line_normal(void)
{
//////////////////正常赛道//////////////////////		
//		/////////////////第一行///////////////////
		peak_mid_1st = peak[2];
		peak_mid_2nd = peak[7];
	
		if(normal_track_flag == 1)
		{
				error_k_1st = 1 - peak_mid_1st * 1.0 / 150;
				if(error_k_1st < 0.1) error_k_1st = 0.1;
				if(error_k_1st >   1) error_k_1st = 1;
			
				peak_across_sub_1st = peak[0] - peak[4];
				peak_across_add_1st = peak[0] + peak[4];
				peak_vertical_sub_1st = peak[1] - peak[3];
				peak_vertical_add_1st = peak[1] + peak[3];
				
		//	  if(peak_mid1 < 30)
		//		{
		//				peak04_sub = peak04_sub/fabs(peak04_sub) * 100;
		//				peak13_sub = peak13_sub/fabs(peak13_sub) * 30;
		//		}

				error_across1_1st = peak_across_sub_1st*1.0/peak_across_add_1st;
				error_vertical_1st = peak_vertical_sub_1st*1.0/peak_vertical_add_1st;
				
				
				if(fabs(peak[1] - peak[3]) > 10)
				{
						error_1st = (float)(error_across1_1st*0.8 + error_vertical_1st*0.2) * (1 + error_k_1st*2);
				}
				else
				{
						error_1st = (float)(error_across1_1st) * (1 + error_k_1st*2);
				}
						
		//		/////////////////第二行///////////////////
				
				error_k_2nd = 1 - peak_mid_2nd * 1.0 / 150;
				if(error_k_2nd < 0.1) error_k_2nd = 0.1;
				if(error_k_2nd >   1) error_k_2nd = 1;
			
				peak_across_sub_2nd = peak[5] - peak[9];
				peak_across_add_2nd = peak[5] + peak[9];
				peak_vertical_sub_2nd = peak[6] - peak[8];
				peak_vertical_add_2nd = peak[6] + peak[8];
				
		//	  if(peak_mid1 < 30)
		//		{
		//				peak04_sub = peak04_sub/fabs(peak04_sub) * 100;
		//				peak13_sub = peak13_sub/fabs(peak13_sub) * 30;
		//		}

				error_across1_2nd = peak_across_sub_2nd*1.0/peak_across_add_2nd;
				error_vertical_2nd = peak_vertical_sub_2nd*1.0/peak_vertical_add_2nd;
				
				
				if(fabs(peak[6] - peak[8]) > 15)
				{
						error_2nd = (float)(error_across1_2nd*0.8 + error_vertical_2nd*0.2) * (1 + error_k_2nd*2);
				}
				else
				{
						error_2nd = (float)(error_across1_2nd) * (1 + error_k_2nd*2);
				}		

		}

		//环岛特殊处理，跟据具体值调节乘项系数
		else if(right_island_flag == 1)
		{
				if(peak[2]>(peak_mid2*1.69))
				{
						error_1st =  (peak[0] - peak[4]*0.8)/ (peak[0] +	peak[4]);
				}
				
				else if(peak[2]>(peak_mid2*1.56))
				{
						error_1st =  (peak[0] - peak[4]*0.62)/ (peak[0] +	peak[4]);
				}
				else if(peak[2] >(peak_mid2*1.2))
				{
						error_1st =  (peak[0] - peak[4]*0.45)/ (peak[0] +	peak[4]);
				}
				else if(peak[2] >(peak_mid2*1.1))
				{
						error_1st =  (peak[0] - peak[4]*0.75)/ (peak[0] +	peak[4]);
				}
				else
				{
						error_1st =  (peak[0] - peak[4]*0.9)/ (peak[0] +	peak[4]);
				}
				error_2nd = error_1st;
		}	

		else if(left_island_flag == 1)
		{
				if(peak[2]>(peak_mid2*1.69))
				{
						error_1st = (peak[0]*0.8 - peak[4])/ (peak[0]*0.8 +	peak[4]);
				}
				else if(peak[2]>(peak_mid2*1.56))
				{
						error_1st = (peak[0]*0.62 - peak[4])/ (peak[0]*0.62 +	peak[4]);
				}
				else if(peak[2] >(peak_mid2*1.2))
				{
						error_1st = (peak[0]*0.45 - peak[4])/ (peak[0]*0.45 +	peak[4]);
				}
				else if(peak[2] >(peak_mid2*1.1))
				{
						error_1st = (peak[0]*0.75 - peak[4])/ (peak[0]*0.75 +	peak[4]);
				}
				else 
				{
						error_1st = (peak[0]*0.9- peak[4])/ (peak[0] +	peak[4]);
				}
				error_2nd = error_1st;
		}	
		else if(cross_flag == 1)
		{
				error_1st = (peak[0]- peak[4])/ (peak[0] +	peak[4]);
				error_2nd = error_1st;
		}


		else
		{
				error_1st = (peak[0]- peak[4])/ (peak[0] +	peak[4]);
				error_2nd = error_1st;	
		}			
}

float error_pred;
float k_pred;

void predict(void)
{	
		k_pred = (error_1st - error_2nd) / 12;
		error_pred = k_pred * (12 + 12) + error_2nd;
		if( error_pred> 3) error_pred = 3;
		if(error_pred < -3) error_pred = -3;
		
		if(cross_in_flag == 1) 
		{
				rudder_error = error_pred * (error_pred * error_pred *0  + 100);
				motor_error  = error_pred * 5500;
		}
		
		else 
	  {
				rudder_error = error_pred * (error_pred * error_pred *50 + 100);
				motor_error  = error_pred * 6000;
		}
	
  	send_array[0] = (uint8)(peak[0]);
		send_array[1] = (uint8)(peak[1]);
		send_array[2] = (uint8)(peak[2]);
		send_array[3] = (uint8)(peak[3]);
		send_array[4] = (uint8)(peak[4]);
		send_array[5] = (uint8)(peak[5]);
		send_array[6] = (uint8)(peak[6]);
		send_array[7] = (uint8)(peak[7]);
		send_array[8] = (uint8)(peak[8]);
		send_array[9] = (uint8)(peak[9]);
		send_array[10] = (uint8)((error_pred + 3)*42);

//		seekfree_wireless_send_buff(send_array, sizeof(send_array));
		
	
}


//2.根据神经网络方法进行提线
int8 input_data[10];
void cie_data_get(void)
{
	input_data[0] = (peak[0]-128);
	input_data[1] = (peak[1]-128);
	input_data[2] = (peak[2]-128);
	input_data[3] = (peak[3]-128);
	input_data[4] = (peak[4]-128);
	input_data[5] = (peak[5]-128);
	input_data[6] = (peak[6]-128);
	input_data[7] = (peak[7]-128);
	input_data[8] = (peak[8]-128);
	input_data[9] = (peak[9]-128);
}
uint8 collection_succes;
int16_t result;
float error_neural;
void get_line_neural(void)
{
	 peak_mid_1st = peak[2];
	 peak_mid_2nd = peak[7];
		cie_data_get();//获取RunModel函数所需的参数
		
		//调用模型，并对计算结果进行右移位
		int16_t temp;
		CI_RunModelXIP(model1, input_data, &temp);
		temp = temp >> SHIFT;
	  
		error_neural = (float)(temp)/42;
	
		if( error_neural > 3)  error_neural = 3;
		if (error_neural <-3)  error_neural = -3;
		
	
		if(cross_in_flag == 1) 
		{
				rudder_error = error_neural * (error_neural * error_neural *0  + 100);
				motor_error  = error_neural * 5500;
		}
		
		else 
	  {
				rudder_error = error_neural * (error_neural * error_neural *20 + 100);
				motor_error  = error_neural * 5500;
		}
		
}


void get_line(void)
{  
		protect();
	  island_judge();
  	get_line_normal();
		predict();
//		get_line_neural();
}
