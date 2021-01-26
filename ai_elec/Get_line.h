#ifndef Get_line_H
#define Get_line_H

#include "headfile.h"

void get_line(void);


//////////影响模型运行部分，禁止删除//////////
#include "nncie.h"
extern void* RunModel(const void *in_buf);
//////////////////////////////////////////////


#endif