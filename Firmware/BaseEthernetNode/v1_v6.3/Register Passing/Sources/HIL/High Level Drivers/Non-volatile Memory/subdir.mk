################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../../../../makefile.local

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS_QUOTED += \
"C:/Users/jwhong/Desktop/M51CN128RD SW/Sources/HIL/High Level Drivers/Non Volatile Memory/constants.c" \
"C:/Users/jwhong/Desktop/M51CN128RD SW/Sources/HIL/High Level Drivers/Non Volatile Memory/setget.c" \

C_SRCS += \
C:/Users/jwhong/Desktop/M51CN128RD\ SW/Sources/HIL/High\ Level\ Drivers/Non\ Volatile\ Memory/constants.c \
C:/Users/jwhong/Desktop/M51CN128RD\ SW/Sources/HIL/High\ Level\ Drivers/Non\ Volatile\ Memory/setget.c \

OBJS += \
./Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/constants_c.obj \
./Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/setget_c.obj \

OBJS_QUOTED += \
"./Sources/HIL/High Level Drivers/Non-volatile Memory/constants_c.obj" \
"./Sources/HIL/High Level Drivers/Non-volatile Memory/setget_c.obj" \

C_DEPS += \
./Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/constants_c.d \
./Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/setget_c.d \

OBJS_OS_FORMAT += \
./Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/constants_c.obj \
./Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/setget_c.obj \


# Each subdirectory must supply rules for building sources it contributes
Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/constants_c.obj: C:/Users/jwhong/Desktop/M51CN128RD\ SW/Sources/HIL/High\ Level\ Drivers/Non\ Volatile\ Memory/constants.c
	@echo 'Building file: $<'
	@echo 'Invoking: ColdFire Compiler'
	"$(CF_ToolsDirEnv)/mwccmcf" @@"Sources/HIL/High Level Drivers/Non-volatile Memory/constants.args" -o "Sources/HIL/High Level Drivers/Non-volatile Memory/constants_c.obj" "$<" -MD -gccdep
	@echo 'Finished building: $<'
	@echo ' '

Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/constants_c.d: C:/Users/jwhong/Desktop/M51CN128RD\ SW/Sources/HIL/High\ Level\ Drivers/Non\ Volatile\ Memory/constants.c
	@echo 'Regenerating dependency file: $@'
	
	@echo ' '

Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/setget_c.obj: C:/Users/jwhong/Desktop/M51CN128RD\ SW/Sources/HIL/High\ Level\ Drivers/Non\ Volatile\ Memory/setget.c
	@echo 'Building file: $<'
	@echo 'Invoking: ColdFire Compiler'
	"$(CF_ToolsDirEnv)/mwccmcf" @@"Sources/HIL/High Level Drivers/Non-volatile Memory/setget.args" -o "Sources/HIL/High Level Drivers/Non-volatile Memory/setget_c.obj" "$<" -MD -gccdep
	@echo 'Finished building: $<'
	@echo ' '

Sources/HIL/High\ Level\ Drivers/Non-volatile\ Memory/setget_c.d: C:/Users/jwhong/Desktop/M51CN128RD\ SW/Sources/HIL/High\ Level\ Drivers/Non\ Volatile\ Memory/setget.c
	@echo 'Regenerating dependency file: $@'
	
	@echo ' '


