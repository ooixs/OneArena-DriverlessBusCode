import time

info = []

vm = {'stop': 1, 'dice': 2, 'target': 3, 'left arrow': 4, 'right arrow': 5, 'forward arrow': 6, 'red heart': 8, 
      '0': 10, '1': 11, '2': 12, '3': 13, '4': 14, '5': 15, '6': 16, '7': 17, '8': 18, '9': 19, 
      'A': 20, 'B': 21, 'C': 22, 'D': 23, 'E': 24, 'F': 25, 'G': 26, 'H': 27, 'I': 28, 'J': 29, 'K': 30, 'L': 31, 'M': 32, 'N': 33, 'O': 34, 'P': 35, 'Q': 36, 'R': 37, 'S': 38, 'T': 39, 'U': 40, 'V': 41, 'W': 42, 'X': 43, 'Y': 44, 'Z': 45}

turn_right = vm["7"]
turn_left = vm["6"]
pick_humanoid = 46
drop_humanoid = 46
end = vm["5"]
turn_left_offset_dist = 0.2 #m
turn_right_offset_dist = 0
vm_marker_distance = 0.3 #m
std_trans_speed = 0.75 #0-3.5 m/s
slow_trans_speed = 0.2
very_slow_trans_speed = 0.1
std_rotate_speed = 180
robotic_arm_x_pos = 0 #mm
robotic_arm_x_pos_far = 900
vm_height = -220
humanoid_head_height = -220
humanoid_body_height = -220
turning_marker_distance = 5 #cm #used in moveToVM
humanoid_scan_time = 2 #s
humanoid_valid_distance = 50 #cm
humanoid_width = 0.045 #m
gripper_close_time = 2 #s

def openGripper():
    while not(gripper_ctrl.is_open()):
        gripper_ctrl.open()
    gripper_ctrl.stop()

def closeGripper(): 
    gripper_ctrl.close()
    time.sleep(gripper_close_time)
    gripper_ctrl.stop()

def closeGripperFull():
    while not(gripper_ctrl.is_closed()):
        gripper_ctrl.close()
    gripper_ctrl.stop()

def moveToVM():
    skip = False
    chassis_ctrl.set_trans_speed(slow_trans_speed)
    while ir_distance_sensor_ctrl.get_distance_info(1) > turning_marker_distance: 
        chassis_ctrl.move(0)
    chassis_ctrl.stop()
    chassis_ctrl.set_trans_speed(std_trans_speed)

def endColor():
    chassis_ctrl.stop()

    #set led to red
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)
    led_ctrl.set_top_led(rm_define.armor_top_all, 255, 0, 0, rm_define.effect_always_on)

def init():
    #gripper and arm position
    robotic_arm_ctrl.moveto(robotic_arm_x_pos_far, vm_height, wait_for_complete=False)
    # robotic_arm_ctrl.recenter()
    media_ctrl.exposure_value_update(rm_define.exposure_value_large)
    gripper_ctrl.update_power_level(4)
    closeGripperFull()

    #detect vision marker
    vision_ctrl.enable_detection(rm_define.vision_detection_marker)
    vision_ctrl.set_marker_detection_distance(vm_marker_distance)

    #detect distance (IR)
    ir_distance_sensor_ctrl.enable_measure(1)

    #set speeds
    chassis_ctrl.set_trans_speed(std_trans_speed)
    chassis_ctrl.set_rotate_speed(std_rotate_speed)

    #set led to green
    led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 0, 0, 255, rm_define.effect_always_on)
    #led_ctrl.set_top_led(rm_define.armor_top_all, 0, 0, 255, rm_define.effect_always_on)

def start():
    init()
    skip = False
    last = None

    while True:
        chassis_ctrl.move(0)
        info = vision_ctrl.get_marker_detection_info()

        if len(info)>2:
            print(info[1])
            if info[1] == last:
                continue
            if info[1] == turn_right:
                # moveToVM()
                chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)
                chassis_ctrl.move_with_distance(90, turn_right_offset_dist)
                # chassis_ctrl.move_with_distance(90, 0.2)
                
            elif info[1] == turn_left:
                # moveToVM()
                chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
                chassis_ctrl.move_with_distance(90, turn_left_offset_dist)

            elif info[1] == pick_humanoid:
                skip = False
                chassis_ctrl.stop()
                # openGripper()
                chassis_ctrl.set_trans_speed(very_slow_trans_speed)
                # robotic_arm_ctrl.moveto(robotic_arm_x_pos_far, humanoid_body_height)
                startTime = time.time()
                
                # if ir_distance_sensor_ctrl.get_distance_info(1) >= humanoid_valid_distance:
                #     while time.time() - startTime <= humanoid_scan_time:
                #         chassis_ctrl.move(-90)
                        
                #         if ir_distance_sensor_ctrl.get_distance_info(1) < humanoid_valid_distance:
                #             chassis_ctrl.move_with_distance(-90, humanoid_width/2)
                #             break

                # if ir_distance_sensor_ctrl.get_distance_info(1) >= humanoid_valid_distance:
                #     while time.time() - startTime <= humanoid_scan_time*3:
                #         chassis_ctrl.move(90)
                #         if ir_distance_sensor_ctrl.get_distance_info(1) < humanoid_valid_distance:
                #             chassis_ctrl.move_with_distance(-90, humanoid_width/2)
                #             break
                    
                while ir_distance_sensor_ctrl.get_distance_info(1) > 0.6: #distance to humanoid
                    chassis_ctrl.move(0)
                chassis_ctrl.stop()
                robotic_arm_ctrl.moveto(robotic_arm_x_pos_far, humanoid_head_height)
                chassis_ctrl.set_trans_speed(std_trans_speed)
                closeGripper()

                # lift arm
                robotic_arm_ctrl.moveto(robotic_arm_x_pos_far, vm_height, wait_for_complete=False)
            
            elif info[1] == drop_humanoid:
                moveToVM()
                chassis_ctrl.rotate_with_degree(rm_define.clockwise, 90)

                # lower arm and drop 
                # robotic_arm_ctrl.moveto(robotic_arm_x_pos_far, humanoid_head_height+5)
                openGripper()

                # robotic_arm_ctrl.moveto(robotic_arm_x_pos, vm_height)
                chassis_ctrl.rotate_with_degree(rm_define.anticlockwise, 90)
                # closeGripperFull()

            elif info[1] == end:
                moveToVM()
                led_ctrl.set_bottom_led(rm_define.armor_bottom_all, 255, 0, 0, rm_define.effect_always_on)
                break
            last = info[1]

        # if other robot detected, just stop and wait
        elif ir_distance_sensor_ctrl.get_distance_info(1) < turning_marker_distance and skip == False:
            obstacle_start = time.time()
            while time.time() - obstacle_start <= 5:
                chassis_ctrl.stop()
            skip = True
    endColor()
