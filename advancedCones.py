bl_info = {
    "name": "Advanced Cones",
	"description": "Tool to generate various nose cone shapes",
	"author": "Mackenzie Crawford",
	"version": (2, 0, 0),
	"blender": (2, 80, 0),
	"location": "View3D > Add > Mesh",
	"support": "COMMUNITY",
    "category": "Add Mesh"
}

import bpy
#from bpy.types import Menu
import bmesh
import math
import mathutils

def build_geometry(verts, edges, steps, rotation, name):
	#takes set of points and edges given, makes it into an actual object, solid-of-revolutions it, appropriately sets its location
	
	#create a faces array, since there was no need to define it in each class
	faces = []
	
	mesh = bpy.data.meshes.new("mesh")
	mesh.from_pydata(verts, edges, faces) 
	obj = bpy.data.objects.new(name, mesh)
	if (2, 80, 0) < bpy.app.version:
		#use the new API
		bpy.context.collection.objects.link(obj)
	else:
		#use the old one
		bpy.context.scene.objects.link(obj)

	bm = bmesh.new()
	bm.from_mesh(obj.data)

	geom = bm.verts[:] + bm.edges[:]

	bmesh.ops.spin(bm, geom=geom, cent=obj.location, axis=(1,0,0), dvec=(0,0,0), angle=-2*math.pi, steps=steps, use_duplicate=0)
	bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)
	
	#rotate to vertical. Hacky temporary solution, will simply draw vertically to begin with later but I'd have to change a bunch of the math code...
	bmesh.ops.rotate(bm, cent=obj.location, matrix=mathutils.Matrix.Rotation(math.radians(90.0), 3, 'Y'), verts=bm.verts[:])
	
	bm.to_mesh(obj.data)
	
	if (2, 80, 0) < bpy.app.version:
		#use the new API
		obj.location = bpy.context.scene.cursor.location
	else:
		#use the old one
		obj.location = bpy.context.scene.cursor_location
	
	obj.rotation_euler[0] = math.pi * rotation[0]/180
	obj.rotation_euler[1] = math.pi * rotation[1]/180
	obj.rotation_euler[2] = math.pi * rotation[2]/180
	bm.free()
	
	current_mode = bpy.context.mode
	if (current_mode == "EDIT_MESH"):
		#preserve previous selection list
		active_obj = bpy.context.active_object
		oldSelection = bpy.context.selected_objects
		
		#we must deselect all objects, because when we do bpy.ops.object.join(), all selected objects will be merged, but we only want to merge our object with the active object
		for someObj in oldSelection:
			if (2, 80, 0) < bpy.app.version:
				#use the new API
				someObj.select_set(state=False)
			else:
				#use the old one
				someObj.select = False
		
		#select the active object, and the new cone object
		
		if (2, 80, 0) < bpy.app.version:
			#use the new API
			obj.select_set(state=True)
			active_obj.select_set(state=True)
		else:
			#use the old one
			obj.select = True
			active_obj.select = True
	
		#have to be in object mode to merge. Switch modes, do the join, then return to edit mode
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.join()
		bpy.ops.object.mode_set(mode='EDIT')
		
		#restore previous selection
		for someObj in oldSelection:
			#someObj.select = True
			if (2, 80, 0) < bpy.app.version:
				#use the new API
				someObj.select_set(state=True)
			else:
				#use the old one
				someObj.select = True

class TangentOgiveGen(bpy.types.Operator):
	#Tangent Ogive Generator
	bl_idname = "mesh.add_tangent_ogive"
	bl_label = "Add Tangent Ogive"
	bl_menulabel = "Tangent Ogive"
	bl_options = {'REGISTER', 'UNDO'}

	baseRadius = bpy.props.FloatProperty(name="Base Radius", default=1, min=0, max=2147483647, step=1)
	apexLength = bpy.props.FloatProperty(name="Apex Length", default=2, min=0, max=2147483647, step=1)
	sphereRadius = bpy.props.FloatProperty(name="Sphere Radius", default=0.2, min=0, max=2147483647, step=1)
	sphereRings = bpy.props.IntProperty(name="Sphere Rings", default=32, min=1, max=2147483647)
	ogiveRings = bpy.props.IntProperty(name="Ogive Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	rotation = bpy.props.FloatVectorProperty(name="Rotation", default=(0,0,0), min=-2147483648, max=2147483647, step=10, subtype="XYZ")
	blunted = bpy.props.BoolProperty(name="Spherically Blunted", default=False)
	
	def draw(self, context):
		box = self.layout.column()
		box.prop(self, "baseRadius")
		box.prop(self, "apexLength")
		box.prop(self, "blunted")
		if (self.blunted == True):
			box.prop(self, "sphereRadius")
			box.prop(self, "sphereRings")
		box.prop(self, "ogiveRings")
		box.prop(self, "segments")
		box.prop(self, "rotation")
	
	def execute(self, context):
		verts = []
		edges = []
	
		if self.baseRadius > 0:
			if self.sphereRadius >= self.baseRadius: #if we don't do this, the universe explodes
				self.sphereRadius = self.baseRadius-0.001

			ogiveRadius = (math.pow(self.baseRadius, 2)+math.pow(self.apexLength, 2))/(2*self.baseRadius)
			xc = self.apexLength - math.sqrt(math.pow(ogiveRadius-self.sphereRadius, 2) - math.pow(ogiveRadius-self.baseRadius, 2)) #center point of sphere cap
			yt = self.sphereRadius*(ogiveRadius-self.baseRadius)/(ogiveRadius-self.sphereRadius) #y coord of tangent point
			xt = xc-math.sqrt(math.pow(self.sphereRadius, 2)-math.pow(yt, 2)) #x coord of tangent point
			xa = xc-self.sphereRadius #distance from hypothetical apex point to the top of the sphere cap
			
			sphereStepSize=(xt-xa)/self.sphereRings
			stepSize = (self.apexLength-xt)/self.ogiveRings
			
			i=1
			
			if self.blunted == True:
				xc = self.apexLength - xc + self.sphereRadius
				x = self.sphereRadius
				y = 0
				verts.append((-xc, y, 0))
				edges.append((i-1, i))
				i=i+1
				
				#calculate angle between the top, the sphere center, and the tangency point
				Ax = -xa + self.apexLength
				Bx = xc - self.sphereRadius
				Cx = -xt + self.apexLength
				Cy = yt
				
				angleAB = math.atan2(Ax - Bx, 0)
				angleBC = -math.atan2(Bx - Cx, Cy)
				angle = math.degrees(angleAB - angleBC)
				
				theta = math.radians(angle/self.sphereRings)
				while i < self.sphereRings+1:
					newX = (x) * math.cos(theta) - (y) * math.sin(theta)
					newY = (y) * math.cos(theta) + (x) * math.sin(theta)
					
					verts.append((-newX-xc+self.sphereRadius, newY, 0))
					edges.append((i-1, i))
					
					x = newX
					y = newY
					
					i=i+1
					
				#fill in base of the cap
				verts.append((-self.apexLength+xt, yt, 0))
				edges.append((i-1, i))
				i=i+1
				
				x = xt
			else:
				x = 0

			#draw ogive section
			while x < self.apexLength:
				verts.append((x-self.apexLength, math.sqrt(math.pow(ogiveRadius, 2) - math.pow(self.apexLength-x, 2)) + self.baseRadius - ogiveRadius, 0))
				edges.append((i-1, i))
				x=x+stepSize
				i=i+1
			
			#fill in base
			verts.append((0, self.baseRadius, 0))
			edges.append((i-1, i))
			edges.pop()
		
		build_geometry(verts, edges, self.segments, self.rotation, "Tangent Ogive")

		return {'FINISHED'}
		
class SecantOgiveGen(bpy.types.Operator):
	#Secant Ogive Generator
	bl_idname = "mesh.add_secant_ogive"
	bl_label = "Add Secant Ogive"
	bl_menulabel = "Secant Ogive"
	bl_options = {'REGISTER', 'UNDO'}
	
	baseRadius = bpy.props.FloatProperty(name="Base Radius", default=1, min=0, max=2147483647, step=1)
	apexLength = bpy.props.FloatProperty(name="Apex Length", default=2, min=0, max=2147483647, step=1)
	ogiveRadius = bpy.props.FloatProperty(name="Ogive Radius", default=2.5, min=0, max=2147483647, step=1)
	ogiveRings = bpy.props.IntProperty(name="Ogive Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	rotation = bpy.props.FloatVectorProperty(name="Rotation", default=(0,0,0), min=-2147483648, max=2147483647, step=10, subtype="XYZ")
	
	def draw(self, context):
		box = self.layout.column()
		box.prop(self, "baseRadius")
		box.prop(self, "apexLength")
		box.prop(self, "ogiveRadius")
		box.prop(self, "ogiveRings")
		box.prop(self, "segments")
		box.prop(self, "rotation")

	def execute(self, context):
		try:
			verts = []
			edges = []
			
			stepSize = self.apexLength/self.ogiveRings		
			alpha = math.atan(self.baseRadius/self.apexLength) - math.acos((math.sqrt(math.pow(self.apexLength, 2) + math.pow(self.baseRadius, 2))/(2*self.ogiveRadius)))
			
			x=0
			i=1
			while x < self.apexLength:
				verts.append((x-self.apexLength, math.sqrt(math.pow(self.ogiveRadius, 2) - math.pow(self.ogiveRadius*math.cos(alpha)-x, 2))+(self.ogiveRadius*math.sin(alpha)), 0))
				edges.append((i-1, i))
				x=x+stepSize
				i=i+1
				
			#fill in base
			verts.append((0, self.baseRadius, 0))
			edges.append((i-1, i))	
			
			edges.pop()
			
			build_geometry(verts, edges, self.segments, self.rotation, "Secant Ogive")
		except:
			#ogive radius was too small for the given base radius and apex length. Resize
			self.ogiveRadius = math.sqrt(math.pow(self.apexLength, 2) + math.pow(self.baseRadius, 2))/2 + 0.01 #interesting problem for anyone interested: programmatically derive the lowest possible offset here to make the program not crash
			self.execute(context)

		return {'FINISHED'}
		
class ProlateHemispheroidGen(bpy.types.Operator):
	#Prolate Hemispheroid Generator
	bl_idname = "mesh.add_prolate_hemispheroid"
	bl_label = "Add Prolate Hemispheroid"
	bl_menulabel = "Prolate Hemispheroid"
	bl_options = {'REGISTER', 'UNDO'}
	
	radius = bpy.props.FloatProperty(name="Radius", default=1, min=0, max=2147483647, step=1)
	length = bpy.props.FloatProperty(name="Length", default=2, min=0, max=2147483647, step=1)
	rings = bpy.props.IntProperty(name="Rings", default=32, min=3, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=1, max=2147483647)
	smoothTip = bpy.props.BoolProperty(name="Smooth tip", description="Takes the final 1/n-length step, and further divides it into an additional n rings", default=True)
	rotation = bpy.props.FloatVectorProperty(name="Rotation", default=(0,0,0), min=-2147483648, max=2147483647, step=10, subtype="XYZ")
	
	def draw(self, context):
		box = self.layout.column()
		box.prop(self, "radius")
		box.prop(self, "length")
		box.prop(self, "rings")
		box.prop(self, "segments")
		box.prop(self, "smoothTip")
		box.prop(self, "rotation")

	def execute(self, context):
		verts = []
		edges = []

		x = self.length
		i=1
		
		verts.append((-x, 0, 0))
		edges.append((i-1, i))
		
		if self.smoothTip == True:
			#smooth tip takes the final 1/n-length step, and further divides it into an additional n rings
			#allows drastic improvement in resolution in the most curved portion, without affecting the rest of the object
			stepSize = self.length/math.pow(self.rings, 2)
			
			while i<=self.rings:
				verts.append((-x, self.radius*math.sqrt(1-(math.pow(x, 2)/math.pow(self.length, 2))), 0))
				edges.append((i-1, i))
				x=x-stepSize
				i=i+1
				
			j=1
		else:
			j=0
		
		stepSize = self.length/self.rings
		
		while j<=self.rings:
			verts.append((-x, self.radius*math.sqrt(1-(math.pow(x, 2)/math.pow(self.length, 2))), 0))
			edges.append((i-1, i))
			x=x-stepSize
			i=i+1
			j=j+1
		
		build_geometry(verts, edges, self.segments, self.rotation, "Prolate Hemispheroid")
	
		return {'FINISHED'}
		
class ParabolicConeGen(bpy.types.Operator):
	#Parabolic Cone Generator
	bl_idname = "mesh.add_parabolic_cone"
	bl_label = "Add Parabolic Cone"
	bl_menulabel = "Parabolic Cone"
	bl_options = {'REGISTER', 'UNDO'}
	
	radius = bpy.props.FloatProperty(name="Radius", default=1, min=0, max=2147483647, step=1)
	length = bpy.props.FloatProperty(name="Length", default=2, min=0, max=2147483647, step=1)
	K = bpy.props.FloatProperty(name="K'", default=0.5, min=0, max=1, step=1)
	rings = bpy.props.IntProperty(name="Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	rotation = bpy.props.FloatVectorProperty(name="Rotation", default=(0,0,0), min=-2147483648, max=2147483647, step=10, subtype="XYZ")
	blunted = bpy.props.BoolProperty(name="Spherically Blunted", default=True)
	
	def draw(self, context):
		box = self.layout.column()
		box.prop(self, "radius")
		box.prop(self, "length")
		box.prop(self, "K")
		box.prop(self, "rings")
		box.prop(self, "segments")
		box.prop(self, "rotation")

	def execute(self, context):
		verts = []
		edges = []
		
		stepSize = self.length/self.rings
		
		x=0
		i=1
		while x<self.length:
			verts.append((x-self.length, ((self.radius*2*x)/self.length - self.K*math.pow(x/self.length, 2))/(2-self.K), 0))
			edges.append((i-1, i))
			x=x+stepSize
			i=i+1
		#fill in base
		verts.append((0, self.radius, 0))
		edges.append((i-1, i))
		edges.pop()

		build_geometry(verts, edges, self.segments, self.rotation, "Parabolic Cone")
		
		return {'FINISHED'}

class PowerSeriesConeGen(bpy.types.Operator):
	#Power Series Cone Generator
	bl_idname = "mesh.add_power_series_cone"
	bl_label = "Add Power Series Cone"
	bl_menulabel = "Power Series Cone"
	bl_options = {'REGISTER', 'UNDO'}

	radius = bpy.props.FloatProperty(name="Radius", default=1, min=0, max=2147483647, step=1)
	length = bpy.props.FloatProperty(name="Length", default=2, min=0, max=2147483647, step=1)
	n = bpy.props.FloatProperty(name="n", default=0.5, min=0, max=1, step=1)
	rings = bpy.props.IntProperty(name="Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	rotation = bpy.props.FloatVectorProperty(name="Rotation", default=(0,0,0), min=-2147483648, max=2147483647, step=10, subtype="XYZ")
	
	def draw(self, context):
		box = self.layout.column()
		box.prop(self, "radius")
		box.prop(self, "length")
		box.prop(self, "n")
		box.prop(self, "rings")
		box.prop(self, "segments")
		box.prop(self, "rotation")
	
	def execute(self, context):
		verts = []
		edges = []
		
		stepSize = self.length/self.rings
		
		x=0
		i=1
		while x<self.length:
			verts.append((x-self.length, self.radius*math.pow(x/self.length, self.n), 0))
			edges.append((i-1, i))
			x=x+stepSize
			i=i+1
		#fill in base
		verts.append((0, self.radius, 0))
		edges.append((i-1, i))
		edges.pop()

		build_geometry(verts, edges, self.segments, self.rotation, "Power Series Cone")
		
		return {'FINISHED'}
		
class HaackSeriesConeGen(bpy.types.Operator):
	#Haack Series Cone Generator"""
	bl_idname = "mesh.add_haack_series_cone"
	bl_label = "Add Haack Series Cone"
	bl_menulabel = "Haack Series Cone"
	bl_options = {'REGISTER', 'UNDO'}

	radius = bpy.props.FloatProperty(name="Radius", default=1, min=0, max=2147483647, step=1)
	length = bpy.props.FloatProperty(name="Length", default=2, min=0, max=2147483647, step=1)
	C = bpy.props.FloatProperty(name="C", default=0.5, min=0, max=2147483647, step=1)
	rings = bpy.props.IntProperty(name="Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	rotation = bpy.props.FloatVectorProperty(name="Rotation", default=(0,0,0), min=-2147483648, max=2147483647, step=10, subtype="XYZ")
	
	def draw(self, context):
		box = self.layout.column()
		box.prop(self, "radius")
		box.prop(self, "length")
		box.prop(self, "C")
		box.prop(self, "blunted")
		box.prop(self, "rings")
		box.prop(self, "segments")
		box.prop(self, "rotation")
	
	def execute(self, context):
		verts = []
		edges = []
		
		stepSize = self.length/self.rings
		
		x=0
		i=1
		while x<self.length:
			theta = math.acos(1-(2*x/self.length))
			verts.append((x-self.length, self.radius/math.sqrt(math.pi)*math.sqrt(theta-(math.sin(2*theta)/2)+(self.C*math.pow(math.sin(theta), 3))), 0))
			edges.append((i-1, i))
			x=x+stepSize
			i=i+1
		#fill in base
		verts.append((0, self.radius, 0))
		edges.append((i-1, i))
		edges.pop()

		build_geometry(verts, edges, self.segments, self.rotation, "Haack Series Cone")
		
		return {'FINISHED'}
		
class NConicGen(bpy.types.Operator):
	#N-Conic Generator
	bl_idname = "mesh.add_nconic"
	bl_label = "Add n-conic"
	bl_menulabel = "n-conic"
	bl_options = {'REGISTER', 'UNDO'}
	
	n = bpy.props.IntProperty(name="n", default=2, min=1, max=10, step=1)
	
	apexLength = bpy.props.FloatProperty(name="Apex length", default = 2, min=0, max=2147483647, step=1)
	
	#apparently all of these have to be manually declared? Isn't there any way to do this procedurally??
	radius0 = bpy.props.FloatProperty(name="Base radius", default=1, min=0, max=2147483647, step=1)
	radius1 = bpy.props.FloatProperty(name="Radius 1", default=0.75, min=0, max=2147483647, step=1)
	radius2 = bpy.props.FloatProperty(name="Radius 2", default=0.6, min=0, max=2147483647, step=1)
	radius3 = bpy.props.FloatProperty(name="Radius 3", default=0.5, min=0, max=2147483647, step=1)
	radius4 = bpy.props.FloatProperty(name="Radius 4", default=0.3, min=0, max=2147483647, step=1)
	radius5 = bpy.props.FloatProperty(name="Radius 5", default=0.2, min=0, max=2147483647, step=1)
	radius6 = bpy.props.FloatProperty(name="Radius 6", default=0.1, min=0, max=2147483647, step=1)
	radius7 = bpy.props.FloatProperty(name="Radius 7", default=0.05, min=0, max=2147483647, step=1)
	radius8 = bpy.props.FloatProperty(name="Radius 8", default=0.01, min=0, max=2147483647, step=1)
	radius9 = bpy.props.FloatProperty(name="Radius 9", default=0, min=0, max=2147483647, step=1)
	
	#we don't actually use length0 for anything, but we will fill a space in the array with Nothing for math reasons
	length1 = bpy.props.FloatProperty(name="Length 1", default=1, min=0, max=2147483647, step=1)
	length2 = bpy.props.FloatProperty(name="Length 2", default=0.5, min=0, max=2147483647, step=1)
	length3 = bpy.props.FloatProperty(name="Length 3", default=0.25, min=0, max=2147483647, step=1)
	length4 = bpy.props.FloatProperty(name="Length 4", default=0.125, min=0, max=2147483647, step=1)
	length5 = bpy.props.FloatProperty(name="Length 5", default=0.0625, min=0, max=2147483647, step=1)
	length6 = bpy.props.FloatProperty(name="Length 6", default=0.03125, min=0, max=2147483647, step=1)
	length7 = bpy.props.FloatProperty(name="Length 7", default=0.015625, min=0, max=2147483647, step=1)
	length8 = bpy.props.FloatProperty(name="Length 8", default=0.0078125, min=0, max=2147483647, step=1)
	length9 = bpy.props.FloatProperty(name="Length 9", default=0.00390625, min=0, max=2147483647, step=1)
	
	sphereRadius = bpy.props.FloatProperty(name="Sphere Radius", default=0.2, min=0, max=2147483647, step=1)
	sphereRings = bpy.props.IntProperty(name="Sphere Rings", default=32, min=1, max=2147483647)
	blunted = bpy.props.BoolProperty(name="Spherically Blunted", default=False)
	
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	rotation = bpy.props.FloatVectorProperty(name="Rotation", default=(0,0,0), min=-2147483648, max=2147483647, step=10, subtype="XYZ")
	
	def draw(self, context):
		box = self.layout.column()
		box.prop(self, "n")
		box.prop(self, "apexLength")
		box.prop(self, "radius0")
		for i in range(1, self.n):
			box.prop(self, "radius" + str(i))
			box.prop(self, "length" + str(i))
		
		if (self.n == 1): #currently only support capping for n=1, had trouble getting the math working for the rest
			box.prop(self, "blunted")
			
		if (self.blunted == True):
			box.prop(self, "sphereRadius")
			box.prop(self, "sphereRings")
		
		box.prop(self, "segments")
		box.prop(self, "rotation")
		
	def execute(self, context):
		verts = []
		edges = []
	
		radii = [self.radius0, self.radius1, self.radius2, self.radius3, self.radius4, self.radius5, self.radius6, self.radius7, self.radius8, self.radius9]
		lengths = [None, self.length1, self.length2, self.length3, self.length4, self.length5, self.length6, self.length7, self.length8, self.length9]
		
		#validate apex length
		totalLength = 0
		for i in range(1, self.n):
			totalLength = totalLength + lengths[i]
		
		if totalLength > self.apexLength:
			self.apexLength = totalLength
		
		i = 1
		
		#draw the tip first
		if (self.blunted == True):
			#draw cap
			if (self.n == 1):
				#tangency point
				xt = (math.pow(self.apexLength, 2)/self.radius0) * math.sqrt(math.pow(self.sphereRadius, 2) / (math.pow(self.radius0, 2) + math.pow(self.apexLength, 2)))
				yt = xt * self.radius0 / self.apexLength
		
				xc = xt + math.sqrt(math.pow(self.sphereRadius, 2) - math.pow(yt, 2)) #center of spherical cap
				xa = xc - self.sphereRadius
				
				xc = self.apexLength - xc + self.sphereRadius
				x = self.sphereRadius
				y = 0
				verts.append((-xc, y, 0))
				edges.append((i-1, i))
				i=i+1
			
				#calculate angle between the top, the sphere center, and the tangency point
				Ax = -xa + self.apexLength
				Bx = xc - self.sphereRadius
				Cx = -xt + self.apexLength
				Cy = yt
			
				angleAB = math.atan2(Ax - Bx, 0)
				angleBC = -math.atan2(Bx - Cx, Cy)
				angle = math.degrees(angleAB - angleBC)
			
				theta = math.radians(angle/self.sphereRings)
				while i < self.sphereRings+1:
					newX = (x) * math.cos(theta) - (y) * math.sin(theta)
					newY = (y) * math.cos(theta) + (x) * math.sin(theta)
				
					verts.append((-newX-xc+self.sphereRadius, newY, 0))
					edges.append((i-1, i))
					
					x = newX
					y = newY
				
					i=i+1
				
				#fill in base of the cap
				verts.append((-self.apexLength+xt, yt, 0))
				edges.append((i-1, i))
				i=i+1
		else:
			#draw the tip
			verts.append((-self.apexLength, 0, 0))
			edges.append((i-1, i))
			i=i+1
			
		#now draw the middle parts
		position = self.apexLength
		for j in range(self.n-1, 0, -1):
			position = position - lengths[j]
			verts.append((-self.apexLength+lengths[j], radii[j], 0))
			edges.append((i-1, i))
			i=i+1
			
		#draw the cone base
		verts.append((0, radii[0], 0))
		edges.append((i-1, i))
		
		edges.pop()
		
		build_geometry(verts, edges, self.segments, self.rotation, "n-conic")
	
		return {'FINISHED'}

class VIEW3D_MT_mesh_advanced_cones_add(bpy.types.Menu):
	#define the Advanced Cones menu
	bl_idname = "VIEW3D_MT_mesh_advanced_cones_add"
	bl_label = "Advanced Cones"
	bl_menulabel = "Advanced Cones"
	
	def draw(self, context):
		layout = self.layout
		layout.operator_context = 'INVOKE_REGION_WIN'
		
		for i in range(1, len(classes)): #we don't include index 0, since thats the menu itself
			layout.operator(classes[i].bl_idname, text=classes[i].bl_menulabel)

classes = (VIEW3D_MT_mesh_advanced_cones_add, TangentOgiveGen, SecantOgiveGen, ProlateHemispheroidGen, ParabolicConeGen, PowerSeriesConeGen, HaackSeriesConeGen, NConicGen)
			
def menu_func(self, context):
	layout = self.layout
	layout.operator_context = 'INVOKE_REGION_WIN'
	
	layout.menu("VIEW3D_MT_mesh_advanced_cones_add", text="Advanced Cones", icon="MESH_CONE")

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	if (2, 80, 0) < bpy.app.version:
		#use the new API
		bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)
	else:
		#use the old one
		bpy.types.INFO_MT_mesh_add.prepend(menu_func)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
		
	if (2, 80, 0) < bpy.app.version:
		#use the new API
		bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
	else:
		#use the old one
		bpy.types.INFO_MT_mesh_add.remove(menu_func)