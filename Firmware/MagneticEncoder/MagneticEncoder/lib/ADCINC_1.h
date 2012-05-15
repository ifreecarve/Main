//*****************************************************************************
//*****************************************************************************
//  FILENAME: ADCINC_1.h
//  Version: 1.20, Updated on 2011/6/28 at 6:7:58
//  Generated by PSoC Designer 5.1.2306
//
//  DESCRIPTION:  C declarations for theADCINCPWM User Module with
//                a 1st-order modulator.
//-----------------------------------------------------------------------------
//      Copyright (c) Cypress Semiconductor 2011. All Rights Reserved.
//*****************************************************************************
//*****************************************************************************
#ifndef ADCINC_1_INCLUDE
#define ADCINC_1_INCLUDE

#include <m8c.h>

#pragma fastcall16 ADCINC_1_Start
#pragma fastcall16 ADCINC_1_SetPower
#pragma fastcall16 ADCINC_1_Stop
#pragma fastcall16 ADCINC_1_GetSamples
#pragma fastcall16 ADCINC_1_StopADC
#pragma fastcall16 ADCINC_1_fIsDataAvailable
#pragma fastcall16 ADCINC_1_iClearFlagGetData
#pragma fastcall16 ADCINC_1_wClearFlagGetData
#pragma fastcall16 ADCINC_1_cClearFlagGetData
#pragma fastcall16 ADCINC_1_bClearFlagGetData
#pragma fastcall16 ADCINC_1_iGetData
#pragma fastcall16 ADCINC_1_wGetData
#pragma fastcall16 ADCINC_1_cGetData
#pragma fastcall16 ADCINC_1_bGetData
#pragma fastcall16 ADCINC_1_fClearFlag
#pragma fastcall16 ADCINC_1_WritePulseWidth

//-------------------------------------------------
// Prototypes of the ADCINC_1 API.
//-------------------------------------------------
extern void  ADCINC_1_Start(BYTE bPower);
extern void  ADCINC_1_SetPower(BYTE bPower);
extern void  ADCINC_1_Stop(void);
extern void  ADCINC_1_GetSamples(BYTE bNumSamples);
extern void  ADCINC_1_StopADC(void);
extern BYTE  ADCINC_1_fIsDataAvailable(void);
extern INT   ADCINC_1_iClearFlagGetData(void);
extern WORD  ADCINC_1_wClearFlagGetData(void);
extern CHAR  ADCINC_1_cClearFlagGetData(void);
extern BYTE  ADCINC_1_bClearFlagGetData(void);
extern INT   ADCINC_1_iGetData(void);
extern WORD  ADCINC_1_wGetData(void);
extern CHAR  ADCINC_1_cGetData(void);
extern BYTE  ADCINC_1_bGetData(void);
extern BYTE  ADCINC_1_fClearFlag(void);
extern void  ADCINC_1_WritePulseWidth(BYTE bPulseWidthValue);


//-------------------------------------------------
// Defines for ADCINC_1 API's.
//-------------------------------------------------
#define ADCINC_1_OFF         0
#define ADCINC_1_LOWPOWER    1
#define ADCINC_1_MEDPOWER    2
#define ADCINC_1_HIGHPOWER   3


//-------------------------------------------------
// Hardware Register Definitions
//-------------------------------------------------
#pragma ioport  ADCINC_1_PWMdr0:    0x020                 //Period reg
BYTE            ADCINC_1_PWMdr0;
#pragma ioport  ADCINC_1_PWMdr1:    0x021                 //1_ADDRh   ; Down count reg
BYTE            ADCINC_1_PWMdr1;               
#pragma ioport  ADCINC_1_PWMdr2:    0x022                 //Compare reg
BYTE            ADCINC_1_PWMdr2;
#pragma ioport  ADCINC_1_PWMcr0:    0x023                 //Control reg
BYTE            ADCINC_1_PWMcr0;
#pragma ioport  ADCINC_1_PWMfn: 0x120                  //Function reg
BYTE            ADCINC_1_PWMfn;
#pragma ioport  ADCINC_1_PWMsl: 0x121                  //Input select reg
BYTE            ADCINC_1_PWMsl;
#pragma ioport  ADCINC_1_PWMos: 0x122                  //Output select reg
BYTE            ADCINC_1_PWMos;
#pragma ioport  ADCINC_1_AtoD1cr0:  0x080              //Analog block 1 control register 0
BYTE            ADCINC_1_AtoD1cr0;
#pragma ioport  ADCINC_1_AtoD1cr1:  0x081              //Analog block 1 control register 1
BYTE            ADCINC_1_AtoD1cr1;
#pragma ioport  ADCINC_1_AtoD1cr2:  0x082              //Analog block 1 control register 2
BYTE            ADCINC_1_AtoD1cr2;
#pragma ioport  ADCINC_1_AtoD1cr3:  0x083              //Analog block 1 control register 3
BYTE            ADCINC_1_AtoD1cr3;
#pragma ioport  ADCINC_1_AtoD2cr0:  0x090              //Analog block 2 control register 0
BYTE            ADCINC_1_AtoD2cr0;
#pragma ioport  ADCINC_1_AtoD2cr1:  0x091              //Analog block 2 control register 1
BYTE            ADCINC_1_AtoD2cr1;
#pragma ioport  ADCINC_1_AtoD2cr2:  0x092              //Analog block 2 control register 2
BYTE            ADCINC_1_AtoD2cr2;
#pragma ioport  ADCINC_1_AtoD2cr3:  0x093              //Analog block 2 control register 3
BYTE            ADCINC_1_AtoD2cr3;

#endif
// end of file ADCINC_1.h
