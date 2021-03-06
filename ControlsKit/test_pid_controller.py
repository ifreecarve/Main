import unittest
import math

from time_sources import global_time, resetTimeSourceForTestingPurposes
from pid_controller import PIDController


class PIDControllerTestCase(unittest.TestCase):
    def setUp(self):
        resetTimeSourceForTestingPurposes(global_time)
        self.pid = PIDController(0.2, 0.02, 0.1)
    def tearDown(self):
        pass

    def testUpdateNoop(self):
        global_time.updateDelta(0.1)
        self.assertEquals(0, self.pid.update(0, 0))

    def testUpdateSmallPositiveError(self):
        global_time.updateDelta(0.1)
        self.assertTrue(0 < self.pid.update(.1, 0))

    def testUpdateSmallNegativeError(self):
        global_time.updateDelta(0.1)
        self.assertTrue(0 > self.pid.update(-.1, 0))

    def testUpdatePTerm(self):
        self.pid.ki = 0
        self.pid.kd = 0
        global_time.updateDelta(0.1)
        small = self.pid.update(.1, 0)
        global_time.updateDelta(0.1)
        large = self.pid.update(2, 0)
        self.assertTrue(small < large)

    def testUpdateDTerm(self):
        self.pid.kp = 0
        self.pid.ki = 0
        global_time.updateDelta(0.1)
        large = self.pid.update(.1, 0)
        self.pid.prev_error = .2
        global_time.updateDelta(0.1)
        small = self.pid.update(.1, 0)
        self.assertTrue(small < large)

    def testUpdateITerm(self):
        self.pid.kp = 0
        self.pid.kd = 0
        global_time.updateDelta(0.1)
        small = self.pid.update(.1, 0)
        global_time.updateDelta(0.1)
        large = self.pid.update(.1, 0)
        self.assertTrue(small < large)

    def testNanGetsSanitized(self):
        try:
            global_time.updateDelta(0.1)
            self.pid.update(float("nan"), 2)
            self.assertTrue(False)
        except ValueError as error:
            self.assertTrue("cannot be NaN" in str(error))
    
    def testSetPointCappedToAngleRange(self):
        #commented out because now we throw an error rather
        #than bounding any angle quietly
        """"global_time.updateDelta(0.1)
        first = self.pid.update(22, 0)
        self.pid.prev_error = 0
        self.pid.integral_error_accumulator = 0
        second = self.pid.update(10, 0)
        self.assertEquals(first, second)

        self.pid.prev_error = 0
        self.pid.integral_error_accumulator = 0
        first = self.pid.update(-10, 0)
        self.pid.prev_error = 0
        self.pid.integral_error_accumulator = 0
        global_time.updateDelta(0.1)
        second = self.pid.update(-math.pi/2, 0)
        self.assertEquals(first, second)"""
    
    def testMaxMovementRateBounded(self):
        self.pid.max_movement_rate = 100
        try:
            global_time.updateDelta(0.1)
            self.pid.update(20, 2)
            self.assertTrue(False)
        except ValueError as error:
            self.assertTrue("unsafe rate" in str(error))
    
    def testTimeSeriesRampInput(self):
        kp = 0.2
        ki = 0.02
        kd = 0.1
        p = PIDController(kp, 0.0, 0.0)
        i = PIDController(0.0, ki, 0.0)
        d = PIDController(0.0, 0.0, kd)
        
        t = 0.0
        dt = 0.008
        i_command_1 = 0.0
        i_command_2 = 0.0
        i_command_3 = 0.0
        while t < 10.0:
            t += dt
            global_time.updateTime(t)
            
            desired = t
            measured = -2.0*t
            p_command = p.update(desired, measured)
            i_command = i.update(desired, measured)
            d_command = d.update(desired, measured)
            pid_command = self.pid.update(desired, measured)
            
            self.assertAlmostEqual(p_command, kp * 3.0*t)
            
            # Testing the integral here is hard because of the discrete-time
            # approximation.
            
            # 1st derivative is positive
            self.assertGreater(i_command, i_command_1)
            # 2nd derivative is positive
            i_diff = i_command - i_command_1
            i_diff_1 = i_command_1 - i_command_2
            self.assertGreater(i_diff, i_diff_1)
            # 3rd derivative is zero
            i_diff_2 = i_command_2 - i_command_3
            self.assertAlmostEqual(i_diff - i_diff_1, i_diff_1 - i_diff_2, 5)
            
            i_command_3 = i_command_2
            i_command_2 = i_command_1
            i_command_1 = i_command
            
            self.assertAlmostEqual(d_command, kd * 3.0)
            self.assertAlmostEqual(pid_command, p_command + i_command + d_command)
    def testTimeSeriesConstantInput(self):
        kp = 0.2
        ki = 0.02
        kd = 0.1
        p = PIDController(kp, 0.0, 0.0)
        i = PIDController(0.0, ki, 0.0)
        d = PIDController(0.0, 0.0, kd)
        
        t = 0.0
        dt = 0.12
        while t < 10.0:
            t += dt
            global_time.updateTime(t)
            
            desired = -0.5
            measured = 2.0
            p_command = p.update(desired, measured)
            i_command = i.update(desired, measured)
            d_command = d.update(desired, measured)
            pid_command = self.pid.update(desired, measured)
            
            self.assertAlmostEqual(p_command, kp * -2.5)
            
            # Because the input signal is constant, here the discrete-time
            # integral is exact
            self.assertAlmostEqual(i_command, ki * -2.5 * t)
            
            if (t == dt):  # First run
                self.assertAlmostEqual(d_command, kd * -2.5 / dt)
            else:
                self.assertAlmostEqual(d_command, 0.0)
            self.assertAlmostEqual(pid_command, p_command + i_command + d_command)

if __name__ == '__main__':
    unittest.main()

