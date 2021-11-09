from common.numpy_fast import clip
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.subaru import subarucan
from selfdrive.car.subaru.values import DBC, PREGLOBAL_CARS, CarControllerParams
from opendbc.can.packer import CANPacker


class CarController():
  def __init__(self, dbc_name, CP, VM):
    self.apply_steer_last = 0
    self.es_lkas_state_cnt = -1
    self.es_dashstatus_cnt = -1
    self.cruise_control_cnt = -1
    self.brake_status_cnt = -1
    self.es_distance_cnt = -1
    self.es_status_cnt = -1
    self.es_brake_cnt = -1
    self.es_accel_cnt = -1
    self.es_lkas_cnt = -1
    self.cruise_button_prev = 0
    self.steer_rate_limited = False
    self.rpm_steady = 0
    self.throttle_steady = 0

    self.packer = CANPacker(DBC[CP.carFingerprint]['pt'])
    self.params = CarControllerParams()

  def update(self, enabled, CS, frame, actuators, pcm_cancel_cmd, visual_alert, left_line, right_line, left_lane_depart, right_lane_depart, lead_visible):

    P = self.params
    can_sends = []

    # *** steering ***
    if (frame % P.STEER_STEP) == 0:

      apply_steer = int(round(actuators.steer * P.STEER_MAX))

      # limits due to driver torque

      new_steer = int(round(apply_steer))
      apply_steer = apply_std_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, P)
      self.steer_rate_limited = new_steer != apply_steer

      if not enabled:
        apply_steer = 0

      if CS.CP.carFingerprint in PREGLOBAL_CARS:
        can_sends.append(subarucan.create_preglobal_steering_control(self.packer, apply_steer, frame, P.STEER_STEP))
      else:
        can_sends.append(subarucan.create_steering_control(self.packer, apply_steer, frame, P.STEER_STEP))

      self.apply_steer_last = apply_steer

    ### LONG ###

    cruise_rpm = 0
    cruise_throttle = 0

    brake_cmd = False
    brake_value = 0

    if CS.CP.openpilotLongitudinalControl:

      # Manual trigger using wipers signal
      #if CS.wipers:
      #  actuators.accel = -1.5
      #  print("wipers set brake 1.5")
      #  brake_cmd = True

      if enabled and actuators.accel < P.ACCEL_BRAKE:
        brake_value = clip(int(abs(actuators.accel) * P.BRAKE_SCALE), P.BRAKE_MIN, P.BRAKE_MAX)
        brake_cmd = True
        #print('actuators.accel: %s, es_brake_pressure: %s es_brake_active: %s brake_value: %s' % (actuators.accel, CS.es_brake_pressure, CS.es_brake_active, brake_value))

      # PCB passthrough
      if enabled and CS.es_brake_active:
        brake_cmd = True
        brake_value = CS.es_brake_pressure

      if enabled and actuators.accel > P.ACCEL_BRAKE:
        # limit min and max values
        target_accel = actuators.accel
        cruise_throttle = clip(int(P.THROTTLE_BASE + ((CS.out.vEgo + target_accel) * P.THROTTLE_SCALE)), P.THROTTLE_MIN, P.THROTTLE_MAX)
        cruise_rpm = clip(int(P.RPM_BASE + ((CS.out.vEgo + target_accel) * P.RPM_SCALE)), P.RPM_MIN, P.RPM_MAX)

        #print('actuators.accel: %s throttle_cruise: %s tcm_rpm: %s op_cruise_throttle: %s op_cruise_rpm: %s' % (actuators.accel, CS.throttle_cruise, CS.tcm_rpm, cruise_throttle, cruise_rpm))

    # *** alerts and pcm cancel ***

    if CS.CP.carFingerprint in PREGLOBAL_CARS:
      if self.es_accel_cnt != CS.es_accel_msg["Counter"]:
        # 1 = main, 2 = set shallow, 3 = set deep, 4 = resume shallow, 5 = resume deep
        # disengage ACC when OP is disengaged
        if pcm_cancel_cmd:
          cruise_button = 1
        # turn main on if off and past start-up state
        elif not CS.out.cruiseState.available and CS.ready:
          cruise_button = 1
        else:
          cruise_button = CS.cruise_button

        # unstick previous mocked button press
        if cruise_button == 1 and self.cruise_button_prev == 1:
          cruise_button = 0
        self.cruise_button_prev = cruise_button

        can_sends.append(subarucan.create_es_throttle_control(self.packer, cruise_button, CS.es_accel_msg))
        self.es_accel_cnt = CS.es_accel_msg["Counter"]

    else:
      if self.es_distance_cnt != CS.es_distance_msg["Counter"]:
        can_sends.append(subarucan.create_es_distance(self.packer, CS.es_distance_msg, enabled, pcm_cancel_cmd, brake_cmd, brake_value, cruise_throttle))
        self.es_distance_cnt = CS.es_distance_msg["Counter"]

      if self.es_status_cnt != CS.es_status_msg["Counter"]:
        can_sends.append(subarucan.create_es_status(self.packer, CS.es_status_msg, enabled, brake_cmd, cruise_rpm))
        self.es_status_cnt = CS.es_status_msg["Counter"]

      if self.es_dashstatus_cnt != CS.es_dashstatus_msg["Counter"]:
        can_sends.append(subarucan.create_es_dashstatus(self.packer, CS.es_dashstatus_msg, enabled, lead_visible))
        self.es_dashstatus_cnt = CS.es_dashstatus_msg["Counter"]

      if self.es_lkas_state_cnt != CS.es_lkas_state_msg["Counter"]:
        can_sends.append(subarucan.create_es_lkas_state(self.packer, CS.es_lkas_state_msg, enabled, visual_alert, left_line, right_line, left_lane_depart, right_lane_depart))
        self.es_lkas_state_cnt = CS.es_lkas_state_msg["Counter"]

      if self.es_brake_cnt != CS.es_brake_msg["Counter"]:
        can_sends.append(subarucan.create_es_brake(self.packer, CS.es_brake_msg, enabled, brake_cmd, brake_value))
        self.es_brake_cnt = CS.es_brake_msg["Counter"]

      if self.cruise_control_cnt != CS.cruise_control_msg["Counter"]:
        can_sends.append(subarucan.create_cruise_control(self.packer, CS.cruise_control_msg))
        self.cruise_control_cnt = CS.cruise_control_msg["Counter"]

      if self.brake_status_cnt != CS.brake_status_msg["Counter"]:
        can_sends.append(subarucan.create_brake_status(self.packer, CS.brake_status_msg, CS.es_brake_active))
        self.brake_status_cnt = CS.brake_status_msg["Counter"]

    return can_sends
