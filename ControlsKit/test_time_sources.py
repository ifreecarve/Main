import unittest
import math
from math_utils import *

from time_sources import TimeSource, StopWatch


# Side effect: tests getTime() and getDelta()
def check(test_case, ts, time, delta):
    test_case.assertAlmostEqual(time, ts.getTime())
    test_case.assertAlmostEqual(delta, ts.getDelta())


class TimeSourceTestCase(unittest.TestCase):
    def setUp(self):
        self.ts = TimeSource()
    def tearDown(self):
        pass

    def testDefaultsToZeros(self):
        check(self, self.ts, 0.0, 0.0)
    
    def testInitialTime(self):
        ts = TimeSource(1.234, 0.036)
        check(self, ts, 1.234, 0.036)
    
    def testUpdateTime(self):
        self.ts.updateTime(0.1)
        check(self, self.ts, 0.1, 0.1)
        self.ts.updateTime(0.33)
        check(self, self.ts, 0.33, 0.23)
    def testUpdateTimeAlwaysIncreasesTimeExceptZero(self):
        self.ts.updateTime(0.0)  # no error because getTime() == 0.0
        self.ts.updateTime(0.1)
        self.assertRaises(ValueError, self.ts.updateTime, 0.1)
        self.assertRaises(ValueError, self.ts.updateTime, 0.0)
        
    def testUpdateDelta(self):
        self.ts.updateDelta(0.1)
        check(self, self.ts, 0.1, 0.1)
        self.ts.updateDelta(0.45)
        check(self, self.ts, 0.55, 0.45)
    def testUpdateDeltaAlwaysIncreasesTimeExceptZero(self):
        self.ts.updateTime(0.0)  # no error because getTime() == 0.0
        self.ts.updateTime(0.1)
        self.assertRaises(ValueError, self.ts.updateDelta, 0.0)
        self.assertRaises(ValueError, self.ts.updateDelta, -0.1)


class StopWatchTestCase(unittest.TestCase):
    def setUp(self):
        self.ts = TimeSource()
        self.ts.updateTime(6.0)
        self.ts.updateDelta(0.1)
        self.sw = StopWatch(time_source=self.ts)
    def tearDown(self):
        pass
    
    def testStartsCountingFromZero(self):
        check(self, self.sw, 0.0, 0.0)
    def testUpdatesLocalTime(self):
        self.sw.update()
        self.ts.updateDelta(0.3)
        self.ts.updateDelta(0.2)
        check(self, self.sw, 0.5, 0.5)
        self.ts.updateDelta(0.1)
        check(self, self.sw, 0.6, 0.1)
    
    def testStop(self):
        self.sw.update()
        self.ts.updateDelta(0.1)
        self.sw.update()
        self.sw.stop()
        self.ts.updateDelta(0.1)
        check(self, self.sw, 0.1, 0.0)
    def testStart(self):
        self.testStop()  # Get an inactive StopWatch
        self.sw.start()
        check(self, self.sw, 0.1, 0.0)
        self.ts.updateDelta(0.2)
        check(self, self.sw, 0.3, 0.2)
    def testIsActive(self):
        self.assertTrue(self.sw.isActive())
        self.sw.stop()
        self.assertFalse(self.sw.isActive())
        self.sw.start()
        self.assertTrue(self.sw.isActive())
    def testInactiveConstructor(self):
        sw = StopWatch(active=False, time_source=self.ts)
        self.assertFalse(sw.isActive())
        check(self, sw, 0.0, 0.0)
        self.ts.updateDelta(0.1)
        check(self, sw, 0.0, 0.0)
        sw.start();
        sw.update()
        self.assertTrue(sw.isActive())
        self.ts.updateDelta(0.2)
        check(self, sw, 0.2, 0.2)
    
    def testSmoothStart(self):
        duration = 0.52345
        self.testStop()  # Get an inactive StopWatch
        self.sw.smoothStart(duration)
        self.assertTrue(self.sw.isActive())
        self.sw.update()
        
        dt = 0.01
        prev_sw_delta = 0.0
        
        for i in range(int(duration/dt)):
            self.ts.updateDelta(dt)
            # Slope should always be increasing
            self.assertGreater(self.sw.getDelta(), prev_sw_delta)
            # But should never be greater than 1.0
            self.assertLess(self.sw.getDelta(), dt)
            prev_sw_delta = self.sw.getDelta()

        t_0 = self.sw.getTime()
        for i in range(100):
            self.ts.updateDelta(dt)
            # Slope should be equal to 1.0
            check(self, self.sw, t_0 + (1 + i)*dt, dt)
    def testSmoothStop(self):
        duration = 0.625
        self.sw.smoothStop(duration)
        self.assertTrue(self.sw.isActive())
        self.sw.update()
        
        dt = 0.01
        prev_sw_delta = 1.0
        
        for i in range(int(math.floor(duration/dt))):
            self.ts.updateDelta(dt)
            # Slope should always be decreasing
            self.assertLess(self.sw.getDelta(), prev_sw_delta)
            # But should always be positive
            self.assertGreater(self.sw.getDelta(), 0.0)
            prev_sw_delta = self.sw.getDelta()
        
        t_0 = self.sw.getTime()
        for i in range(100):
            self.ts.updateDelta(dt)
            # Slope should be equal to 0.0
            check(self, self.sw, t_0, 0.0)
            self.assertFalse(self.sw.isActive())

    def doPartialSmoothStart(self):
        duration = 0.52345
        dt = 0.01
        self.testStop()  # Get an inactive StopWatch
        self.sw.smoothStart(duration)
        
        # Get part-way through the start transition
        for i in range(int(duration/(2*dt))):
            self.ts.updateDelta(dt)
            self.sw.update()
    def testSmoothStartInterruptedByStart(self):
        self.doPartialSmoothStart()
        self.sw.start()
        self.sw.update()
        self.assertTrue(self.sw.isActive())
        self.ts.updateDelta(0.1)
        self.assertAlmostEqual(0.1, self.sw.getDelta())
        self.ts.updateDelta(0.1)
        self.assertAlmostEqual(0.1, self.sw.getDelta())
    def testSmoothStartInterruptedByStop(self):
        self.doPartialSmoothStart()
        self.sw.stop()
        self.sw.update()
        self.assertFalse(self.sw.isActive())
        self.ts.updateDelta(0.1)
        self.assertAlmostEqual(0.0, self.sw.getDelta())
        self.ts.updateDelta(0.1)
        self.assertAlmostEqual(0.0, self.sw.getDelta())
    def testSmoothStartInterruptedBySmoothStart(self):
        duration = 0.5
        self.doPartialSmoothStart()
        self.sw.smoothStart(duration)
        self.sw.update()
        
        dt = 0.01
        prev_sw_delta = 0.0
        for i in range(10):
            self.ts.updateDelta(dt)
            # Slope should always be decreasing
            self.assertGreater(self.sw.getDelta(), prev_sw_delta)
            # But should always be positive
            self.assertLess(self.sw.getDelta(), dt)
            prev_sw_delta = self.sw.getDelta()
    def testSmoothStartInterruptedBySmoothStop(self):
        duration = 0.5
        self.doPartialSmoothStart()
        self.sw.smoothStop(duration)
        self.sw.update()
        
        dt = 0.01
        prev_sw_delta = 1.0
        for i in range(10):
            self.ts.updateDelta(dt)
            # Slope should always be decreasing
            self.assertLess(self.sw.getDelta(), prev_sw_delta)
            # But should always be positive
            self.assertGreater(self.sw.getDelta(), 0.0)
            prev_sw_delta = self.sw.getDelta()

    def doPartialSmoothStop(self):
        duration = 0.52345
        dt = 0.01
        self.sw.smoothStop(duration)
        
        # Get part-way through the stop transition
        for i in range(int(duration/(2*dt))):
            self.ts.updateDelta(dt)
            self.sw.update()
    def testSmoothStopInterruptedByStart(self):
        self.doPartialSmoothStop()
        self.sw.start()
        self.sw.update()
        self.assertTrue(self.sw.isActive())
        self.ts.updateDelta(0.1)
        self.assertAlmostEqual(0.1, self.sw.getDelta())
        self.ts.updateDelta(0.1)
        self.assertAlmostEqual(0.1, self.sw.getDelta())
    def testSmoothStopInterruptedByStop(self):
        self.doPartialSmoothStop()
        self.sw.stop()
        self.sw.update()
        self.assertFalse(self.sw.isActive())
        self.ts.updateDelta(0.1)
        self.assertAlmostEqual(0.0, self.sw.getDelta())
        self.ts.updateDelta(0.1)
        self.assertAlmostEqual(0.0, self.sw.getDelta())
    def testSmoothStopInterruptedBySmoothStart(self):
        duration = 0.5
        self.doPartialSmoothStop()
        self.sw.smoothStart(duration)
        self.sw.update()
        
        dt = 0.01
        prev_sw_delta = 0.0
        for i in range(10):
            self.ts.updateDelta(dt)
            # Slope should always be decreasing
            self.assertGreater(self.sw.getDelta(), prev_sw_delta)
            # But should always be positive
            self.assertLess(self.sw.getDelta(), dt)
            prev_sw_delta = self.sw.getDelta()
    def testSmoothStopInterruptedBySmoothStop(self):
        duration = 0.5
        self.doPartialSmoothStop()
        self.sw.smoothStop(duration)
        self.sw.update()
        
        dt = 0.01
        prev_sw_delta = 1.0
        for i in range(10):
            self.ts.updateDelta(dt)
            # Slope should always be decreasing
            self.assertLess(self.sw.getDelta(), prev_sw_delta)
            # But should always be positive
            self.assertGreater(self.sw.getDelta(), 0.0)
            prev_sw_delta = self.sw.getDelta()


if __name__ == '__main__':
    unittest.main()
