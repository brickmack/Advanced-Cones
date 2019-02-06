bl_info = {
    "name": "Advanced Cones",
	"description": "Tool to generate various nose cone shapes",
	"author": "Mackenzie Crawford",
	"version": (1, 3, 0),
	"blender": (2, 80, 0),
	"location": "View3D > Add > Mesh",
	"support": "COMMUNITY",
    "category": "Add Mesh"
}

import bpy
import bmesh
import math
import mathutils

def build_geometry(verts, edges, faces, steps, name):
	#takes set of points and edges given, makes it into an actual object, solid-of-revolutions it, appropriately sets its location
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
	
	obj.location = bpy.context.scene.cursor_location
	bm.free()

class TangentOgiveGen(bpy.types.Operator):
	"""Tangent Ogive Generator"""      # blender will use this as a tooltip for menu items and buttons.
	bl_idname = "mesh.add_tangent_ogive"        # unique identifier for buttons and menu items to reference.
	bl_label = "Add Tangent Ogive"         # display name when searching
	bl_menulabel = "Tangent Ogive"     # display name in menu
	bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

	baseRadius = bpy.props.FloatProperty(name="Base Radius", default=1, min=0, max=2147483647, step=1)
	apexLength = bpy.props.FloatProperty(name="Apex Length", default=2, min=0, max=2147483647, step=1)
	sphereRadius = bpy.props.FloatProperty(name="Sphere Radius", default=0.2, min=0, max=2147483647, step=1)
	sphereRings = bpy.props.IntProperty(name="Sphere Rings", default=32, min=0, max=2147483647)
	ogiveRings = bpy.props.IntProperty(name="Ogive Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)

	def execute(self, context):
		if self.sphereRadius >= self.baseRadius: #if we don't do this, the universe explodes
			self.sphereRadius = self.baseRadius-0.001

		ogiveRadius = (math.pow(self.baseRadius, 2)+math.pow(self.apexLength, 2))/(2*self.baseRadius)

		xc = self.apexLength - math.sqrt(math.pow(ogiveRadius-self.sphereRadius, 2) - math.pow(ogiveRadius-self.baseRadius, 2)) #center point of sphere cap
		yt = self.sphereRadius*(ogiveRadius-self.baseRadius)/(ogiveRadius-self.sphereRadius) #y coord of tangent point
		xt = xc-math.sqrt(math.pow(self.sphereRadius, 2)-math.pow(yt, 2)) #x coord of tangent point
		xa = xc-self.sphereRadius #distance from hypothetical apex point to the top of the sphere cap
		
		sphereStepSize=(xt-xa)/self.sphereRings
		stepSize = (self.apexLength-xt)/self.ogiveRings

		verts = []
		edges = []
		faces = []

		x=xa
		i=1
		#draw sphere section
		while x<xt:
			verts.append((x-self.apexLength, math.sqrt(math.pow(self.sphereRadius, 2)-math.pow(x-xc, 2)), 0))
			edges.append((i-1, i))
			x=x+sphereStepSize
			i=i+1

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

		build_geometry(verts, edges, faces, self.segments, "Tangent Ogive")

		return {'FINISHED'}
		
class SecantOgiveGen(bpy.types.Operator):
	"""Secant Ogive Generator"""
	bl_idname = "mesh.add_secant_ogive"
	bl_label = "Add Secant Ogive"
	bl_menulabel = "Secant Ogive"
	bl_options = {'REGISTER', 'UNDO'}
	
	baseRadius = bpy.props.FloatProperty(name="Base Radius", default=1, min=0, max=2147483647, step=1)
	apexLength = bpy.props.FloatProperty(name="Apex Length", default=2, min=0, max=2147483647, step=1)
	ogiveRadius = bpy.props.FloatProperty(name="Ogive Radius", default=2.5, min=0, max=2147483647, step=1)
	ogiveRings = bpy.props.IntProperty(name="Ogive Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)

	def execute(self, context):
		try:
			verts = []
			edges = []
			faces = []
			
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
			
			build_geometry(verts, edges, faces, self.segments, "Secant Ogive")
		except:
			#ogive radius was too small for the given base radius and apex length. Resize
			self.ogiveRadius = math.sqrt(math.pow(self.apexLength, 2) + math.pow(self.baseRadius, 2))/2 + 0.01 #interesting problem for anyone interested: programmatically derive the lowest possible offset here to make the program not crash
			self.execute(context)

		return {'FINISHED'}
		
class ProlateHemispheroidGen(bpy.types.Operator):
	"""Prolate Hemispheroid Generator"""
	bl_idname = "mesh.add_prolate_hemispheroid"
	bl_label = "Add Prolate Hemispheroid"
	bl_menulabel = "Prolate Hemispheroid"
	bl_options = {'REGISTER', 'UNDO'}
	
	radius = bpy.props.FloatProperty(name="Radius", default=1, min=0, max=2147483647, step=1)
	length = bpy.props.FloatProperty(name="Length", default=2, min=0, max=2147483647, step=1)
	rings = bpy.props.IntProperty(name="Rings", default=32, min=3, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=1, max=2147483647)
	smoothTip = bpy.props.BoolProperty(name="Smooth tip", description="Takes the final 1/n-length step, and further divides it into an additional n rings", default=True)

	def execute(self, context):
		verts = []
		edges = []
		faces = []
		
		stepSize = self.length/self.rings
		
		x=0
		i=1
		while i<=self.rings:
			verts.append((x, self.radius*math.sqrt(1-(math.pow(x, 2)/math.pow(self.length, 2))), 0))
			edges.append((i-1, i))
			x=x+stepSize
			i=i+1

		if self.smoothTip == True:
			#smooth tip takes the final 1/n-length step, and further divides it into an additional n rings
			#allows drastic improvement in resolution in the most curved portion, without affecting the rest of the object
			x=x-stepSize
			stepSize = stepSize/self.rings
			
			while i<=(self.rings)*2:
				verts.append((x, self.radius*math.sqrt(1-(math.pow(x, 2)/math.pow(self.length, 2))), 0))
				edges.append((i-1, i))
				x=x+stepSize
				i=i+1
		
		verts.append((x, 0, 0))
		edges.append((i-1, i))
		
		edges.pop()
		
		build_geometry(verts, edges, faces, self.segments, "Prolate Hemispheroid")
	
		return {'FINISHED'}
		
class ParabolicConeGen(bpy.types.Operator):
	"""Parabolic Cone Generator"""
	bl_idname = "mesh.add_parabolic_cone"
	bl_label = "Add Parabolic Cone"
	bl_menulabel = "Parabolic Cone"
	bl_options = {'REGISTER', 'UNDO'}
	
	radius = bpy.props.FloatProperty(name="Radius", default=1, min=0, max=2147483647, step=1)
	length = bpy.props.FloatProperty(name="Length", default=2, min=0, max=2147483647, step=1)
	K = bpy.props.FloatProperty(name="K'", default=0.5, min=0, max=1, step=1)
	rings = bpy.props.IntProperty(name="Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)

	def execute(self, context):
		verts = []
		edges = []
		faces = []
		
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

		build_geometry(verts, edges, faces, self.segments, "Parabolic Cone")
		
		return {'FINISHED'}

class PowerSeriesConeGen(bpy.types.Operator):
	"""Power Series Cone Generator"""
	bl_idname = "mesh.add_power_series_cone"
	bl_label = "Add Power Series Cone"
	bl_menulabel = "Power Series Cone"
	bl_options = {'REGISTER', 'UNDO'}

	radius = bpy.props.FloatProperty(name="Radius", default=1, min=0, max=2147483647, step=1)
	length = bpy.props.FloatProperty(name="Length", default=2, min=0, max=2147483647, step=1)
	n = bpy.props.FloatProperty(name="n", default=0.5, min=0, max=1, step=1)
	rings = bpy.props.IntProperty(name="Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	
	def execute(self, context):
		verts = []
		edges = []
		faces = []
		
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

		build_geometry(verts, edges, faces, self.segments, "Power Series Cone")
		
		return {'FINISHED'}
		
class HaackSeriesConeGen(bpy.types.Operator):
	"""Haack Series Cone Generator"""
	bl_idname = "mesh.add_haack_series_cone"
	bl_label = "Add Haack Series Cone"
	bl_menulabel = "Haack Series Cone"
	bl_options = {'REGISTER', 'UNDO'}

	radius = bpy.props.FloatProperty(name="Radius", default=1, min=0, max=2147483647, step=1)
	length = bpy.props.FloatProperty(name="Length", default=2, min=0, max=2147483647, step=1)
	C = bpy.props.FloatProperty(name="C", default=0.5, min=0, max=2147483647, step=1)
	rings = bpy.props.IntProperty(name="Rings", default=32, min=1, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	
	def execute(self, context):
		verts = []
		edges = []
		faces = []
		
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

		build_geometry(verts, edges, faces, self.segments, "Haack Series Cone")
		
		return {'FINISHED'}
		
class SphericallyBluntedConeGen(bpy.types.Operator):
	"""Spherically Blunted Cone Generator"""
	bl_idname = "mesh.add_spherically_blunted_cone"
	bl_label = "Add Spherically Blunted Cone"
	bl_menulabel = "Spherically Blunted Cone"
	bl_options = {'REGISTER', 'UNDO'}
	
	baseRadius = bpy.props.FloatProperty(name="Base Radius", default=1, min=0, max=2147483647, step=1)
	apexLength = bpy.props.FloatProperty(name="Apex Length", default=2, min=0, max=2147483647, step=1)
	sphereRadius = bpy.props.FloatProperty(name="Sphere Radius", default=0.2, min=0, max=2147483647, step=1)
	sphereRings = bpy.props.IntProperty(name="Sphere Rings", default=32, min=0, max=2147483647)
	segments = bpy.props.IntProperty(name="Segments", default=32, min=3, max=2147483647)
	
	def execute(self, context):
		if self.sphereRadius >= self.baseRadius: #if we don't do this, the universe explodes
			self.sphereRadius = self.baseRadius-0.001
	
		xt = (math.pow(self.apexLength, 2)/self.baseRadius) * math.sqrt(math.pow(self.sphereRadius, 2) / (math.pow(self.baseRadius, 2) + math.pow(self.apexLength, 2)))
		yt = xt * self.baseRadius / self.apexLength
		
		xc = xt + math.sqrt(math.pow(self.sphereRadius, 2) - math.pow(yt, 2)) #center of spherical cap
		xa = xc - self.sphereRadius
		
		sphereStepSize=(xt-xa)/self.sphereRings
		
		verts = []
		edges = []
		faces = []
		
		x=xa
		i=1
		#draw sphere section
		while x<xt:
			verts.append((x-self.apexLength, math.sqrt(math.pow(self.sphereRadius, 2)-math.pow(x-xc, 2)), 0))
			edges.append((i-1, i))
			x=x+sphereStepSize
			i=i+1
		
		#fill in base
		verts.append((0, self.baseRadius, 0))
		edges.append((i-1, i))
		edges.pop()
		
		build_geometry(verts, edges, faces, self.segments, "Blunted Cone")
		
		return {'FINISHED'}
		

classes = (TangentOgiveGen, SecantOgiveGen, ProlateHemispheroidGen, ParabolicConeGen, PowerSeriesConeGen, HaackSeriesConeGen, SphericallyBluntedConeGen)

		
def menu_func(self, context):
	for cls in classes:
		self.layout.operator(cls.bl_idname, text=cls.bl_menulabel)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
	
	if (2, 80, 0) < bpy.app.version:
		#use the new API
		bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)
	else:
		#use the old one
		bpy.types.INFO_MT_mesh_add.prepend(menu_func)

def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)
		
	if (2, 80, 0) < bpy.app.version:
		#use the new API
		bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
	else:
		#use the old one
		bpy.types.INFO_MT_mesh_add.remove(menu_func)