#include "hardware_init.h"
#include "headfile.h"

/*
    硬件系统初始化
*/

void hardware_init(void)
{ 
 /*********************************电机初始化*********************************/
		pwm_init(PWM1_MODULE3_CHB_D1, 17000, 0);    //正转，右
		pwm_init(PWM1_MODULE3_CHA_D0, 17000, 0);    //反转，右
	
		pwm_init(PWM2_MODULE3_CHB_D3, 17000, 0);    //反转，左
		pwm_init(PWM2_MODULE3_CHA_D2, 17000, 0);    //正转，左
	
/*********************************舵机初始化*********************************/
		pwm_init(PWM1_MODULE1_CHA_D14, 50, 3550);     // left_edge=3900, middle=3500, right_edge=3100
	
/*********************************电磁初始化*********************************/
    adc_init(ADC_1 , ADC1_CH15_B26 , ADC_8BIT );  //AD1  
	  adc_init(ADC_1 , ADC1_CH0_B27 , ADC_8BIT );   //AD2 
	  adc_init(ADC_1 , ADC1_CH13_B24 , ADC_8BIT );  //AD3 
	  adc_init(ADC_1 , ADC1_CH14_B25 , ADC_8BIT );  //AD4 
	  adc_init(ADC_1 , ADC1_CH11_B22 , ADC_8BIT );  //AD5 
	  adc_init(ADC_1 , ADC1_CH12_B23 , ADC_8BIT );  //AD6 
	  adc_init(ADC_1 , ADC1_CH9_B20 , ADC_8BIT );   //AD7 
	  adc_init(ADC_1 , ADC1_CH10_B21 , ADC_8BIT );  //AD8 
	  adc_init(ADC_1 , ADC1_CH7_B18 , ADC_8BIT );   //AD9 
	  adc_init(ADC_1 , ADC1_CH8_B19 , ADC_8BIT );	  //AD10 
 	  adc_init(ADC_1 , ADC1_CH5_B16 , ADC_8BIT );	  //AD11
	  adc_init(ADC_1 , ADC1_CH6_B17 , ADC_8BIT );	  //AD12
		adc_init(ADC_1 , ADC1_CH3_B14 , ADC_8BIT );	  //AD13
 	  adc_init(ADC_1 , ADC1_CH1_B12 , ADC_8BIT );	  //AD14
	  adc_init(ADC_1 , ADC1_CH4_B15 , ADC_8BIT );	  //AD15

/********************************编码器初始化********************************/		
    qtimer_quad_init(QTIMER_1,QTIMER1_TIMER0_C0,QTIMER1_TIMER1_C1);    //C0为提取值
    qtimer_quad_init(QTIMER_1,QTIMER1_TIMER2_C2,QTIMER1_TIMER3_C24);   //C2为提取值
		
/******************************初始化定时器中断******************************/
    pit_init();                     //初始化pit外设
    pit_interrupt_ms(PIT_CH0,5);    //初始化pit通道0 周期
	  //NVIC_SetPriority(PIT_IRQn,15);  //设置中断优先级 范围0-15 越小优先级越高 四路PIT共用一个PIT中断函数


/*********************************串口初始化*********************************/
		seekfree_wireless_init();   //无线转串口模块相关引脚定义在 wireless.h文件中, 默认D16,D17
//		
		simiic_init();
		icm20602_init();

	/*********************************TFT初始化*********************************/

   gpio_init(C20, GPI, 0, GPIO_PIN_CONFIG);
   gpio_init(C22, GPI, 0, GPIO_PIN_CONFIG);
   gpio_init(C29, GPI, 0, GPIO_PIN_CONFIG);
   gpio_init(C27, GPI, 0, GPIO_PIN_CONFIG);
}