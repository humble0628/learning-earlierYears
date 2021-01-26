/*********************************************************************************************************************
 * COPYRIGHT NOTICE
 * Copyright (c) 2019,逐飞科技
 * All rights reserved.
 * 技术讨论QQ群：一群：179029047(已满)  二群：244861897
 *
 * 以下所有内容版权均属逐飞科技所有，未经允许不得用于商业用途，
 * 欢迎各位使用并传播本程序，修改内容时必须保留逐飞科技的版权声明。
 *
 * @file       		main
 * @company	   		成都逐飞科技有限公司
 * @author     		逐飞科技(QQ3184284598)
 * @version    		查看doc内version文件 版本说明
 * @Software 		IAR 8.3 or MDK 5.26
 * @Target core		NXP RT1021DAG5A
 * @Taobao   		https://seekfree.taobao.com/
 * @date       		2019-02-18
 ********************************************************************************************************************/


//整套推荐IO查看Projecct文件夹下的TXT文本



//打开新的工程或者工程移动了位置务必执行以下操作
//第一步 关闭上面所有打开的文件
//第二步 project  clean  等待下方进度条走完




#include "headfile.h"

#include "fsl_device_registers.h"
#include "fsl_debug_console.h"
#include "board.h"

#include "pin_mux.h"
#include "clock_config.h"
/*******************************************************************************
 * Definitions
 ******************************************************************************/
volatile uint32_t g_tick;
/*******************************************************************************
 * Prototypes
 ******************************************************************************/
/*******************************************************************************
 * Code
 ******************************************************************************/
/*!
 * @brief Main function
 */
 
#include "nncie.h"
extern void* RunModel(const void *in_buf);
#define SYSTICK_PRESCALE 10
///////////////////////////以上东西，尽量不要修改///////////////////////////////


uint8 flag_1, flag_2, flag_3 ,flag_4 ;
int stop_flag , out_flag;
int count_garage;
extern int stop_count , speed_down_flag, car_speed , peak_mid_1st , real_pwm[2];
void OutPut_Data(int data);


int main(void)
{
	/////////////////////////////勿动//////////////////////////////////
	  DisableGlobalIRQ();
	  board_init();//务必保留，本函数用于初始化MPU 时钟 调试串口
		hardware_init();
		systick_delay_ms(2000); 
	  EnableGlobalIRQ(0);
	  SysTick_Config(CLOCK_GetFreq(kCLOCK_CoreSysClk) / (SYSTICK_PRESCALE * 10000U));
	  const CI_OutMetricInfo* pOM = CI_GetOutMetricInfo(0);
	  ModelInfo_t inf;
		CI_GetModelInfoXIP(model1, &inf);
	///////////////////////////////////////////////////////////////////
	
	
	//在此添加自己的部分
		
	
    while (1)
    { 
			
				//停车识别
//				flag_1 = 1 - gpio_get(C20);
//				flag_2 = 1 - gpio_get(C22);
//				flag_3 = gpio_get(C29);
//				flag_4 = gpio_get(C27);
//			  if ((flag_1 + flag_2 + flag_3 + flag_4) > 0) 	
//				{
//						out_flag = 1;
//				}
				
//				if(count_garage > 200 * 6)
//				{
//						count_garage = 200 * 6;
//				}
//				if(   out_flag == 1 && count_garage == 200 * 6 &&   ((flag_1 + flag_2 + flag_3 + flag_4) > 0))//  ||    stop_count>200*16.8   )
//				{
//						stop_flag = 1;
//				}
    }
}



























/////////////////////////////底层配置，最好不要动//////////////////////////////////////
#define PROFILING	1
#ifdef 	PROFILING

#define PROF_CNT		20
#define PROF_ERR		16
#define PROF_MASK 		(~(PROF_ERR - 1))
#define PROF_HITCNT_INC	100
// whether hitCnt should decay, faster decay makes most time consuming functions
// seems to have even more hit count
#define PROF_DECAY	
uint32_t s_ignrList[] = {
	0,
	// (uint32_t)sensor_snapshot + 0x40 ,
};

typedef struct {
	uint32_t baseAddr;	// (aligned) base address range of PC sample
	uint32_t hitCnt;    // hit count (a decay mecahnism automatically drops it)
	uint32_t hitRatio;	// 10-bit resolution hit ratio, 
	uint32_t rsvd;		// reserved for better view in memory window
} ProfUnit_t;

typedef struct {
	uint8_t decayNdx;  // which item to decay its hitCnt 
	uint32_t profCnt;  // totoal hit count of profiling
	ProfUnit_t items[PROF_CNT];
}Prof_t;
Prof_t s_prof;

void _ProfOnHit(ProfUnit_t *pItem, uint32_t pc) 
{
	pItem->baseAddr = pc & PROF_MASK;
	s_prof.profCnt+= PROF_HITCNT_INC;
	pItem->hitCnt += PROF_HITCNT_INC;
	pItem->hitRatio = 
		(uint32_t)(((uint64_t)(pItem->hitCnt) << 10) / s_prof.profCnt);
	// sort items descending
	ProfUnit_t tmpItem;	
	for (;pItem != s_prof.items && pItem[0].hitCnt > pItem[-1].hitCnt; pItem--) 
	{
		tmpItem = pItem[0]; pItem[0] = pItem[-1] ; pItem[-1] = tmpItem;
	}
}
void ProfUpdateRate(float res)
{
  uint32_t i; 
  float profCnt = s_prof.profCnt;
  ProfUnit_t *pItem = s_prof.items;
  for (i=0; i<PROF_CNT; i++, pItem++) {
	pItem->hitRatio = 
	  (uint32_t)( (float)(pItem->hitCnt) * res / profCnt);
  }
}
void ProfReset(void)
{
  memset(&s_prof, 0, sizeof(s_prof));
}
void Profiling(uint32_t pc) 
{
	uint32_t i;
	ProfUnit_t *pItem = &s_prof.items[0];
	// filter ignore list
	for (i=0; i<ARRAY_SIZE(s_ignrList); i++) {
		if (pc - s_ignrList[i] < PROF_ERR)
			return;
	}
	#ifdef PROF_DECAY
		// apply decaying, we do not decay to zero, this means PC samples do not
		// get removed automatically, only can be pushed by later new more frequent
		// hit PC samples 
		if (s_prof.items[s_prof.decayNdx].hitCnt > 1) {
			s_prof.items[s_prof.decayNdx].hitCnt--;
			s_prof.profCnt--;
		}
		if (++s_prof.decayNdx == PROF_CNT)
			s_prof.decayNdx = 0;
	#endif	
	uint32_t freeNdx = PROF_CNT;
	// >>> traverse to search existing same PC sample
	for (i=0, pItem = s_prof.items; i<PROF_CNT; i++, pItem++) {
		if (pItem->baseAddr == (pc & PROF_MASK)) {
			_ProfOnHit(pItem, pc);
			break;
		} else if (freeNdx == PROF_CNT && pItem->hitCnt == 0){
			// record empty item, in case need to use for new PC sample
			freeNdx = i;
		}
	}
	if (i == PROF_CNT) {
		if (freeNdx < PROF_CNT) {
			// does not find, allocate for new
			_ProfOnHit(s_prof.items + freeNdx, pc);
		} else {
		  // replace the last one. We must give new samples chance to compete to
		  // get into the list.
		  freeNdx = PROF_CNT - 1;
		  s_prof.profCnt -= s_prof.items[freeNdx].hitCnt;
		  s_prof.items[freeNdx].hitCnt = 0;
		  _ProfOnHit(s_prof.items + freeNdx, pc);
		}
	}
}

#endif
typedef struct {
    uint32_t    r0, r1, r2, r3, r12, lr, pc, xpsr;
} ExceptionRegisters_t;


volatile uint32_t s_prescale;
void SysTick_C_Handler(ExceptionRegisters_t *regs) {
    extern uint32_t uwTick;
	
	#if SYSTICK_PRESCALE > 1
	if (++s_prescale < SYSTICK_PRESCALE)
		return;
	s_prescale = 0;
	#endif
	
	#ifdef PROFILING
	Profiling(regs->pc);
	#endif	
	g_tick++;
}



#if (__CC_ARM)
__asm void SysTick_Handler(void) 
{
	IMPORT	SysTick_C_Handler

	PRESERVE8
	tst lr, #4 
    ite eq 
	mrseq r0, msp
	mrsne r0, psp	
	push   {lr}
	bl SysTick_C_Handler  // Off to C land
	pop    {lr}
	bx	   lr
}

#else

void SysTick_Handler(void)
{
    __asm (
		".globl SysTick_C_Handler\n"
		".align 3				\n"
        "tst lr, #4             \n"
        "ite eq              	\n"
        "mrseq r0, msp       	\n"
		"mrsne r0, psp	        \n"
		"push   {lr}	        \n"
		"bl SysTick_C_Handler	\n"
		"pop    {lr}	       	\n"
		"bx	   lr				\n"
    );
}
 
#endif
