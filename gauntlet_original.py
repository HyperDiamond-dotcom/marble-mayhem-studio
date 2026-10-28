"""Original Marble Mayhem — fully 3D helical racing animation.
Run: blender -b -P gauntlet_original.py -- --preview
No external source code or assets. Choreographed movement; true 3D geometry,
but not yet rigid-body collision physics.
"""
import bpy, math, os, sys
from math import sin,cos,pi
from mathutils import Vector
PREVIEW="--preview" in sys.argv
OUT=os.environ.get("MARBLE_OUT","output")
os.makedirs(OUT,exist_ok=True)
FPS=15 if PREVIEW else 24
NFR=60 if PREVIEW else 1680
START=9 if PREVIEW else 0
RES=(432,768) if PREVIEW else (1080,1920)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.engine="CYCLES";s.cycles.device="CPU"
s.cycles.samples=20 if PREVIEW else 48
s.view_layers[0].cycles.use_denoising=False
s.render.resolution_x,s.render.resolution_y=RES
s.render.resolution_percentage=100;s.render.fps=FPS
s.frame_start=1;s.frame_end=NFR
s.render.image_settings.file_format="PNG";s.render.filepath=os.path.join(OUT,"f_")
s.view_settings.view_transform="Standard";s.view_settings.exposure=-0.75
world=bpy.data.worlds.new("Studio");s.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get("Background");bg.inputs["Color"].default_value=(.055,.075,.12,1);bg.inputs["Strength"].default_value=.45

def mat(name,c,metal=0,rough=.2,em=0):
 m=bpy.data.materials.new(name);m.use_nodes=True
 b=m.node_tree.nodes.get("Principled BSDF");b.inputs["Base Color"].default_value=(*c,1)
 b.inputs["Metallic"].default_value=metal;b.inputs["Roughness"].default_value=rough
 if em:
  try:b.inputs["Emission Color"].default_value=(*c,1);b.inputs["Emission Strength"].default_value=em
  except:pass
 return m
white=mat("Ivory enamel ramp",(.38,.48,.62),.08,.34)
steel=mat("Brushed metallic frame",(.18,.28,.4),.48)
chrome=mat("Bright rail chrome",(.48,.55,.65),.55)
cyan=mat("Cyan luminous trim",(.04,.57,.84),.1,.3,.75)
pink=mat("Vivid magenta",(.65,.06,.34),.13,.28,.7)
gold=mat("Golden obstacles",(1,.54,.09),.55)
colors=[(.96,.16,.24),(.18,.55,1),(.21,.96,.3),(1,.74,.07),(.78,.25,1)]
ballm=[mat("Glass-like marble "+str(i),c,.25,.09,.2) for i,c in enumerate(colors)]
TURNS=5.7;H=26;W=3.35;COUNT=900
def theta(u):return 2*pi*TURNS*u+.18*sin(8*pi*u)
def radi(u):return 5.7+.5*sin(4*pi*u)+.22*cos(11*pi*u)
def side(u):a=theta(u);return Vector((cos(a),sin(a),0))
def path(u):
 a=theta(u);r=radi(u)
 return Vector((r*cos(a),r*sin(a),H*(1-u)+.2*sin(12*pi*u)))
def lane(u,i):return path(u)+side(u)*((i-2)*.63)
def tube(name,pts,r,m):
 cu=bpy.data.curves.new(name,"CURVE");cu.dimensions="3D";cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new("POLY");sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(name,cu);s.collection.objects.link(o);o.data.materials.append(m)
 return o
def block(name,loc,dims,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 b=o.modifiers.new("Soft edges","BEVEL");b.width=.045;b.segments=2
 return o
def pillar(loc,r,height,m,name):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=height,location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(m);return o
# True 3D continuous helical ramp, not a 2D projected track.
verts=[];faces=[]
for k in range(COUNT+1):
 u=k/COUNT;c=path(u);rad=side(u)
 verts.extend([tuple(c-rad*W/2),tuple(c+rad*W/2)])
 if k<COUNT:
  j=2*k;faces.append((j,j+1,j+3,j+2))
mesh=bpy.data.meshes.new("3D helical ramp");mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new("Five-lane multi-storey track",mesh);s.collection.objects.link(o);o.data.materials.append(white)
sol=o.modifiers.new("Solid enamel track","SOLIDIFY");sol.thickness=.13
for e in (-1,1):
 for dz,r,m in ((.17,.078,chrome),(-.12,.04,cyan)):
  tube("Sweeping 3D safety rail",[path(k/COUNT)+side(k/COUNT)*e*W/2+Vector((0,0,dz)) for k in range(COUNT+1)],r,m)
for i in range(1,5):
 off=(i-2.5)*.63
 tube("Glow lane delimiter",[path(k/COUNT)+side(k/COUNT)*off+Vector((0,0,.017)) for k in range(COUNT+1)],.014,cyan if i%2 else pink)
pillar((0,0,H/2),.26,H+2,steel,"Main tower")
for k in range(2,19,2):
 p=path(k/20)
 pillar((p.x,p.y,(p.z-.5)/2),.055,p.z-.5,steel,"Vertical support")
block("Shadow stage",(0,0,-1.3),(24,24,.3),steel)
for z in (4,12,20,25):
 bpy.ops.mesh.primitive_torus_add(major_radius=7.5,minor_radius=.05,location=(0,0,z))
 bpy.context.object.data.materials.append(pink if z%2 else cyan)
# Animated obstacles
haz=[]
for j,u in enumerate((.13,.25,.38,.52,.65,.78,.89)):
 p=path(u)+Vector((0,0,.60))
 ob=pillar(p,.43,.22,gold if j%2 else pink,"Spinning hazard disc")
 haz.append(ob)
# Distinct mechanical gates and rotating hammer arms provide visual story beats.
gear_arms=[]
for j,h in enumerate(haz):
 u=(.13,.25,.38,.52,.65,.78,.89)[j]
 p=path(u)+Vector((0,0,.6))
 for k in range(2):
  obj=block("Industrial hazard paddle "+str(j)+"."+str(k),p,(1.75,.18,.18),gold if j%2 else chrome)
  gear_arms.append((obj,p,j,k))
# Cyan and magenta overhead warning gates define dramatic course sections.
for j,u in enumerate((.09,.32,.56,.83,.96)):
 mid=path(u);r=side(u);a=mid-r*(W/2+.15);b=mid+r*(W/2+.15)
 tube("Warning gate "+str(j),[a+Vector((0,0,.08)),a+Vector((0,0,1.1)),(a+b)/2+Vector((0,0,1.34)),b+Vector((0,0,1.1)),b+Vector((0,0,.08))],.075,pink if j%2 else cyan)
# The final finish portal (with large 3D end-ring) is shared with full length.
finish=path(.991)
tube("Victory illuminated arch",[finish-side(.991)*(W/2+.2)+Vector((0,0,.15)),finish-side(.991)*(W/2+.2)+Vector((0,0,1.8)),finish+Vector((0,0,2.5)),finish+side(.991)*(W/2+.2)+Vector((0,0,1.8)),finish+side(.991)*(W/2+.2)+Vector((0,0,.15))],.13,gold)
for k in range(12):
 v=.08+.075*k
 p=path(v)+Vector((0,0,.12))
 ballmark=pillar(p,.06,.07,gold if k%3==0 else cyan,"Course checkpoint marker")
for i,c in enumerate(colors):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=.285,location=lane(.005,i))
 ob=bpy.context.object;ob.name=["RED","BLUE","GREEN","GOLD","PURPLE"][i]+" racing marble"
 ob.data.materials.append(ballm[i]);bpy.ops.object.shade_smooth()
 if i==0:balls=[]
 balls.append(ob)
d=bpy.data.cameras.new("Tracking camera");d.type="PERSP";d.lens=46
cam=bpy.data.objects.new("Tracking camera",d);s.collection.objects.link(cam);s.camera=cam
def light(name,col,power):
 data=bpy.data.lights.new(name,"AREA");data.energy=power;data.color=col;data.shape="DISK";data.size=8
 ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob);return ob
key=light("White key",(1,1,1),1100)
fill=light("Cyan fill",(.28,.82,1),700)
rim=light("Pink rim",(1,.25,.65),650)
def look(o,p):o.rotation_euler=(Vector(p)-Vector(o.location)).to_track_quat("-Z","Y").to_euler()
def clamp(v,a,b):return max(a,min(b,v))
def progress(t,i):
 u=clamp((t-3)/61,0,1)
 wiggle=.010*sin(10*pi*u+i*1.23)*sin(pi*u)
 bias=[-.006,.004,.002,-.002,.001][i]*u
 boost=(.016 if i==2 else -.012 if i==1 else 0)*u**6
 return clamp(.004+(1-.008)*(u+wiggle+bias+boost),.004,.996)
for frame in range(1,NFR+1):
 t=START+(frame-1)/FPS
 ps=[progress(t,i) for i in range(5)]
 for i,ob in enumerate(balls):
  u=ps[i];ob.location=lane(u,i)+Vector((0,0,.285));ob.rotation_euler=(13*u,8*u+i,17*u)
  ob.keyframe_insert("location",frame=frame);ob.keyframe_insert("rotation_euler",frame=frame)
 for i,ob in enumerate(haz):
  ob.rotation_euler[2]=(1 if i%2 else -1)*(t+i)
  ob.keyframe_insert("rotation_euler",frame=frame)
 for obj,p,j,k in gear_arms:
  obj.location=p
  obj.rotation_euler[2]=((1 if j%2 else -1)*t*2.9)+(k*math.pi/2)+j
  obj.keyframe_insert("rotation_euler",frame=frame)
 u=clamp(sum(ps)/5,.02,.98);tar=path(u);rad=side(u)
 motion=(path(min(.998,u+.008))-path(max(.002,u-.008))).normalized()
 # Fast editorial camera cuts: tight low tracking, top-down reveal, reverse chase.
 shot=int(max(0,t-START)/1.24)%4 if PREVIEW else int(max(0,t)/7)%4
 if shot==0:
  cam.location=tar+rad*5.1-motion*1.8+Vector((0,0,1.7));cam.data.lens=49
 elif shot==1:
  cam.location=tar+rad*7.2-motion*.5+Vector((0,0,6.7));cam.data.lens=40
 elif shot==2:
  cam.location=tar+rad*5.25+motion*2.8+Vector((0,0,2.15));cam.data.lens=49
 else:
  cam.location=tar+rad*5.9-motion*2.9+Vector((0,0,.9));cam.data.lens=46
 look(cam,tar+Vector((0,0,.3)))
 cam.data.keyframe_insert("lens",frame=frame)
 cam.keyframe_insert("location",frame=frame);cam.keyframe_insert("rotation_euler",frame=frame)
 key.location=tar+rad*3+Vector((0,0,5))
 fill.location=tar-rad*3+Vector((0,0,4))
 rim.location=tar-motion*3+Vector((0,0,4))
 for l in (key,fill,rim):
  look(l,tar);l.keyframe_insert("location",frame=frame);l.keyframe_insert("rotation_euler",frame=frame)
# Don't interpolate through editorial cuts; use hold-to-cut camera lens, not zoom smoothing.
if cam.data.animation_data and cam.data.animation_data.action:
 try:
  for fc in cam.data.animation_data.action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation="CONSTANT"
 except Exception: pass
print("Rendering original Marble Mayhem 3D scene",NFR,"frames")
bpy.ops.render.render(animation=True)
print("Rendering completed")
