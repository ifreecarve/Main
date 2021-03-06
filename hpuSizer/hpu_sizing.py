from pylab import *
import scipy.optimize


# Link lengths
#L1 = 1.8  # m
#L2 = 2.4  # m
L1 = 1.6  # m
L2 = 2.3  # m

# http://www.surpluscenter.com/item.asp?item=9-7257-10&catname=hydraulic
B1 = 1.0  # in, bore for hip-yaw cylinder
RD1 = 0.625  # in, rod diameter
# http://www.surpluscenter.com/item.asp?item=9-7715-12&catname=hydraulic
B2 = 2.0  # in, bore for hip-pitch and knee clyinders
RD2 = 1.125  # in, rod diameter
S = 10.0  # in, stroke
RL = 22.25  #in, retracted length

PRESSURE = 2000.0 * 6894.8  # Pascals

# Distance from cylinder attachment points to joint axis
CD1 = [0.6, 0.3]
CD2 = [0.3, 0.8]
CD3 = [0.8, 0.4]

# Gait parameters
HHL = 1.0  # m, hip height low
HHH = 2.0  # m, hip height high
STANCE = 1.2  # m, how far outside the hip should we place the foot?
STRIDE = 1.4  # m, how far do we move in one step?
SPEED = 1.5  # m/s


# The Cartesian position type is a numpy array
def CP(x,y,z):
	return array([x,y,z])

def in2m(l):
	return l * 0.0254

def trans(H, cp):
	cp2 = H * matrix(append(cp,1.0)).T
	assert abs(cp2[3] - 1.0) < 1e-10, "ERROR: 4th coefficient should be 1.0, not %f" % cp2[3]
	return array(cp2)[:-1,0]
def rotate(H, cp):
	return array(H[:3,:3] * matrix(cp).T)[:,0]


# Kinematics specified using simplified DH parameters as defined on page 76 of Spong,H,V:
#   The local frame is attached to the *end* of each link.
#   Joint angle (theta) is about previous link's Z-axis.
#   Length is the link's extent in the previous link's X-axis if theta is zero.
#   Rotation sets the Z-axis correctly for the next joint.
# To get from Frame i-1 to Frame i:
#   1. Rotate about Z by theta[i]
#   2. Translate along X by length[i]
#   3. Rotate about X by rotation[i]
class Link:
	def __init__(self, length, rotation):
		self.l = length  # m
		self.r = rotation  # rad
		self.sr = sin(self.r)
		self.cr = cos(self.r)

		self.setTheta(0.0)
		
		self.pLink = None  # Previous link in the chain
		self.dLink = None  # Next link in the chain
	
	def setProximalLink(self, link):
		if self.pLink != None:
			self.pLink.dLink = None
		self.pLink = link
		if link != None:
			link.dLink = self
	def setDistalLink(self, link):
		link.setProximalLink(self)
	
	def getTheta(self):
		return self.t
	def setTheta(self, theta):
		self.t = theta
		
		st = sin(self.t)
		ct = cos(self.t)
		
		sr = self.sr
		cr = self.cr
		
		l = self.l
		
		# Homogeneous transform from proximal frame to local frame
		self.l2p = matrix(
			[[ct, -st*cr,  st*sr, l*ct],
			 [st,  ct*cr, -ct*sr, l*st],
			 [ 0,     sr,     cr,    0],
			 [ 0,      0,      0,    1]]
			)
		
		# Inverse
		self.p2l = self.l2p.I
		
	def toProximal(self, cp):
		return trans(self.l2p, cp)
	def rotateToProximal(self, cp):
		return rotate(self.l2p, cp)
	def toDistal(self, cp):
		return trans(self.dLink.p2l, cp)
		
	def toWorld(self, cp):
		return self.pLink.toWorld(self.toProximal(cp))
	def rotateToWorld(self, cp):
		return self.pLink.rotateToWorld(self.rotateToProximal(cp))


class Cylinder:
	# Specify bore, stroke, retractedLength in inches. *sigh*
	def __init__(self, bore, rodDiameter, stroke, retractedLength, link1Index, attachmentPoint1, link2Index, attachmentPoint2):
		assert bore > rodDiameter
		
		self.area = in2m(bore/2.0)**2 * pi  # m^2
		self.rodArea = in2m(rodDiameter/2.0)**2 * pi  # m^2
		self.stroke = in2m(stroke)  # m
		self.rl = in2m(retractedLength)  # m
		
		self.forceBounds = array([-(self.area - self.rodArea), (self.area - self.rodArea)]) * PRESSURE
		
		self.l1 = link1Index
		self.ap1 = attachmentPoint1  # In link1 frame
		self.l2 = link2Index
		self.ap2 = attachmentPoint2  # In link2 frame

	def length(self):
		return norm(self.l1.toWorld(self.ap1) - self.l2.toWorld(self.ap2))
	
	def strokeValid(self):
		l = self.length()
		# Give some slop for numerical errors. It's common to move exactly to one extreme.
		return 2e-5 >= self.rl - l  and  -2e-5 <= self.rl + self.stroke - l
	
	def volume(self, warnOnStrokeError = True):
		l = self.length()
		if warnOnStrokeError and not self.strokeValid():
			raise ValueError("Cylinder length out of bounds: %f (min=%f, max=%f)" % (l, self.rl, self.rl + self.stroke))
		return (l - self.rl)*self.area * 1000.0  # Convert to liters

	def draw(self):
		ends = array([self.l1.toWorld(self.ap1), self.l2.toWorld(self.ap2)])
		
		subplot(121)  # X-Y
		plot(ends[:,0], ends[:,1], 'b.-', linewidth=2)
		subplot(122)  # X-Z
		plot(ends[:,0], ends[:,2], 'b.-', linewidth=2)

		
class Leg:
	def __init__(self, links, cylinders):
		self.links = list(links)
		self.cylinders = list(cylinders)
		self.dof = len(self.links)
		assert self.dof == 3,  "Legs must have exactly three links"
		assert len(self.cylinders) == self.dof, "Legs must have an equal number of cylinders and links"
		
		# Put the kinematic chain together
		self.pLink = None
		self.links[0].setProximalLink(self)
		for j in range(self.dof - 1):
			self.links[j].setDistalLink(self.links[j+1])
		
		# Replace link indices with links
		for c in self.cylinders:
			if c.l1 == -1:
				c.l1 = self
			else:
				c.l1 = self.links[c.l1]
			if c.l2 == -1:
				c.l2 = self
			else:
				c.l2 = self.links[c.l2]
			
			# Check that we can use the whole range of the cylinder
			d1 = norm(c.ap1)  # Distance from axis to ap1
			d2 = norm(c.l2.toProximal(c.ap2))  # Distance from axis to ap2
			assert abs(d1-d2) < c.rl
			assert d1+d2 > c.rl+c.stroke
	
	# Coordinates
	def getAngles(self):
		return array(map(Link.getTheta, self.links))
	def setAngles(self, *args):
		assert len(args) == self.dof
		map(Link.setTheta, self.links, args)

	def getLengths(self):
		return array(map(Cylinder.length, self.cylinders))
	
	# Length arguments range from 0.0 to c.stroke
	def setLengths(self, *args):
		assert len(args) == self.dof
		
		lengthTarget = array(args) + array(map(lambda c: c.rl, self.cylinders))
		def a2l(a):
			leg.setAngles(*a)
			return norm(leg.getLengths() - lengthTarget)
		print scipy.optimize.fmin(a2l, array([0,pi/4, -pi/2]), full_output=True) #, xtol=1e-6, ftol=1e-5
		
		print leg.getAngles(), leg.getLengths(), lengthTarget, leg.getLengths() - lengthTarget
		assert leg.strokesValid()
		#assert norm(leg.getLengths() - lengthTarget) < 1e-3
	
	# Kinematics
	def getFootPos(self):
		return self.links[-1].toWorld(CP(0,0,0))
	def setFootPos(self, cp):
		l1 = self.links[1].l
		l2 = self.links[2].l
		x = cp[0]
		y = cp[1]
		z = cp[2]
		r = norm(cp)

		# Ignoring joint limits, we can reach any pose within a sphere centered at the shoulder...
		if r >= l1 + l2:
			raise ValueError("Position unachievable: ||%f %f %f|| = %f > %f = %f + %f" % (x,y,z, norm(cp), l1 + l2, l1, l2))
		# ... unless it's too close.
		if r <= abs(l1 - l2):
			raise ValueError("Position unachievable: ||%f %f %f|| = %f < %f = |%f - %f|" % (x,y,z, norm(cp), abs(l1 - l2), l1, l2))

		q = zeros(3)
		
		# First, do the easy one
		q[0] = arctan2(y, x)

		# Then set the radius correctly
		q[2] = arccos((r**2 - l1**2 - l2**2)/(-2*l1*l2)) - pi  # Prefer the elbow-up solution
		
		# Then set Z correctly
		q[1] = arcsin(z/r) - arcsin( (l2*sin(q[2])) / r )
		
		self.setAngles(*q)
	
	# Base case for Link.toWorld() recursion
	def toDistal(self, cp):
		return trans(self.links[0].p2l, cp)
	def toWorld(self, cp):
		return cp  # Stub. No Body yet.
	def rotateToWorld(self, cp):
		return cp  # Stub. No Body yet.
	
	# Cylinder stuff
	def strokesValid(self):
		return all(map(Cylinder.strokeValid, self.cylinders))
	def getVolumes(self, warnOnStrokeError = False):
		return array(map(lambda c: c.volume(warnOnStrokeError), self.cylinders))
	def getTorqueBounds(self):
		assert leg.strokesValid()
		
		signs = [-1,-1,1]
		tau = zeros((leg.dof,2))
		for i in range(leg.dof):
			c = leg.cylinders[i]
			ap1 = c.l1.toWorld(c.ap1)
			ap2 = c.l2.toWorld(c.ap2)
			
			# Joint rotates about previous link's Z axis
			jointCenter = c.l2.pLink.toWorld(CP(0,0,0))
			if i == 0:
				jointAxis = CP(0,0,1)
			else:
				jointAxis = c.l2.pLink.rotateToWorld(CP(0,0,1))
				
			assert abs(norm(jointAxis) - 1.0) < 1e-10
			
			r = ap2 - jointCenter
			f_hat = ap2 - ap1
			f_hat /= norm(f_hat)
			tau[i,0] = signs[i] * dot(jointAxis, cross(r, c.forceBounds[0] * f_hat))
			tau[i,1] = signs[i] * dot(jointAxis, cross(r, c.forceBounds[1] * f_hat))
		
		return tau
		
	
	def draw(self):
		o = CP(0,0,0)
		origins = zeros((self.dof+1, 3))
		
		origins[0,:] = self.toWorld(o)
		for j in range(self.dof):
			origins[j+1,:] = self.links[j].toWorld(o)
		
		subplot(121)  # X-Y
		plot(origins[:,0], origins[:,1], 'ro-', linewidth=8)
		subplot(122)  # X-Z
		plot(origins[:,0], origins[:,2], 'ro-', linewidth=8)
		
		map(Cylinder.draw, self.cylinders)

#class Body:
#	def __init__(self, *args):
#		self.legs = list(args)
#		self.nLegs = len(self.legs)
#		
#		# Connect legs to body
#		for leg in self.legs:
#			leg.links[0].setProximalLink(self)


# Find the valid range of joint angles based on cylinder strokes/lengths.
# Assumes that leg.cylinders[i] controls leg.links[i]
def calcRanges(leg):
	ranges = zeros((leg.dof,2))
	
	leg.setLengths(0.0, 0.0, 0.0)
	if not leg.strokesValid():
		print leg.getAngles(), leg.getLengths(), map(Cylinder.strokeValid, leg.cylinders)
		assert False
	ranges[:,0] = leg.getAngles()
	
	leg.setLengths(leg.cylinders[0].stroke, leg.cylinders[1].stroke, leg.cylinders[2].stroke)
	if not leg.strokesValid():
		print leg.getAngles(), leg.getLengths(), map(Cylinder.strokeValid, leg.cylinders)
		#assert False
	ranges[:,1] = leg.getAngles()
	
	return ranges	

def plotWorkspace(leg):
	r = calcRanges(leg)
	print "Joint Ranges:"
	print r
	N = 50
	
	subplot(121)  # X-Y
	theta0 = linspace(r[0,0], r[0,1], N)
	
	ep = zeros((len(theta0), leg.dof))
	for i in range(len(theta0)):
		leg.setAngles(theta0[i], r[1,0], r[2,0])
		ep[i,:] = leg.getFootPos()
	plot(ep[:,0], ep[:,1], 'g')
	f = array(ep[0,:])
	l = array(ep[-1,:])
	for i in range(len(theta0)):
		leg.setAngles(theta0[i], r[1,1], r[2,1])
		ep[i,:] = leg.getFootPos()
	ep[0,:] = f
	ep[-1,:] = l
	plot(ep[:,0], ep[:,1], 'g')
	
	plot([STANCE,STANCE], [STRIDE/2, -STRIDE/2], 'r')
	axis('equal')
	
	subplot(122)  # X-Z
	theta1 = r[1,0]*ones(N)
	theta1 = append(theta1, linspace(r[1,0], r[1,1]), N)
	theta1 = append(theta1, r[1,1]*ones(N))
	theta1 = append(theta1, linspace(r[1,1], r[1,0]), N)

	theta2 = linspace(r[2,0], r[2,1], N)
	theta2 = append(theta2, r[2,1]*ones(N))
	theta2 = append(theta2, linspace(r[2,1], r[2,0]), N)
	theta2 = append(theta2, r[2,0]*ones(N))

	ep = zeros((len(theta1), leg.dof))
	for i in range(len(theta1)):
		leg.setAngles(0,theta1[i],theta2[i])
		ep[i,:] = leg.getFootPos()	
	plot(ep[:,0], ep[:,2], 'g')
	
	s1 = STANCE
	s2 = norm([STANCE, STRIDE/2])
	plot([s1, s2, s2, s1, s1], [-HHL, -HHL, -HHH, -HHH, -HHL], 'r')
	axis('equal')
	
	leg.setAngles(*r[:,0])
	assert leg.strokesValid()
	leg.draw()
	leg.setAngles(*r[:,1])
	assert leg.strokesValid()
	leg.draw()

def simulate(leg, speed, cp_0, cp_f, nPoints=500):
	dif = cp_f - cp_0
	l = norm(dif)
	vel = speed/l * dif
	
	t = linspace(0.0, l/speed, nPoints)
	dt = t[1] - t[0]
	cps = array(t, ndmin=2).T*vel + cp_0
	
	angles = zeros((len(t),leg.dof))
	strokesValid = zeros(shape(t))
	vols = zeros(shape(angles))
	
	for i in range(len(t)):
		leg.setFootPos(cps[i,:])
		angles[i,:] = leg.getAngles()
		strokesValid[i] = leg.strokesValid()
		vols[i,:] = leg.getVolumes()

	angularRates = diff(angles, axis=0) / dt
	flowRates = diff(vols, axis=0) / dt
	netRate = array(map(lambda r: sum(abs(r)), flowRates))
	
	figure()
	title("Joint angles (rad)")
	plot(t, angles)
	figure()
	title("Angular rates (rad/s)")
	plot(t[:-1], angularRates)
	figure()
	title("Cylinder volumes (l)")
	plot(t, vols)
	plot(t, strokesValid)
	figure()
	title("Flow rates (l/s)")
	plot(t[:-1], flowRates)
	plot(t[:-1], netRate)
	show()
	
	return ([max(flowRates[:,0]), max(flowRates[:,1]), max(flowRates[:,2])], max(netRate), all(strokesValid))

def setUpFigure(n=1):
	l = L1 + L2 + 0.1
	figure(n)
	subplot(121)
	title("Top down view")
	xlabel("X (m)")
	ylabel("Y (m)")
	axis([-l, l, -l, l])
	subplot(122)
	title("Side view")
	xlabel("X (m)")
	ylabel("Z (m)")
	axis([-l, l, -l, l])



# Main
#for CD in [0.42, 0.5, 0.55, 0.6]:
leg = Leg(
			[Link(0.0, pi/2), Link(L1, 0.0), Link(L2, 0.0)],
			[
				Cylinder(B1,RD1,S,RL, -1, CP(0, CD1[0], 0), 1, CP(CD1[1] - L1, 0, 0)),
				Cylinder(B2,RD2,S,RL, -1, CP(0, 0, CD2[0]), 1, CP(CD2[1] - L1, 0, 0)),
				Cylinder(B2,RD2,S,RL,  1, CP(-CD3[0], 0, 0), 2, CP(CD3[1] - L2, 0, 0))
			]
		)
#plotWorkspace(leg)

#leg.setAngles(0,pi/8,-pi/4)
#leg.setFootPos(CP(1.25,0,0))
#print leg.getFootPos()
#print leg.getAngles()

#cp = CP(1.4,-.2,-.30)
#leg.setFootPos(cp);
#leg.draw(); 
#print cp, leg.getFootPos()
#print leg.getVolumes(), leg.strokesValid()

#print simulate(leg, SPEED, CP(STANCE, STRIDE/2, -HHH), CP(STANCE, -STRIDE/2, -HHH))
#print simulate(leg, SPEED, CP(STANCE, STRIDE/2, -HHL), CP(STANCE, -STRIDE/2, -HHL))

#print calcRanges(leg)
#for c in leg.cylinders:
#	print c.forceBounds

#print calcRanges(leg)
leg.setAngles(0, 0.2, -2.3)
print leg.getTorqueBounds()
leg.draw()
setUpFigure()
show()

