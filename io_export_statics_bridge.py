# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Export: Statics Bridge",
    "author": "Peter Gutfeldt",
    "version": (1, 1, 4),
    "location": "File > Export > Statics Bridge Code (.txt)",
    "category": "Import-Export"
    }

import bpy


# = ================= =
# =  BRIDGE EXPORTER  =
# = ================= =

def write_bridge(uName, context, filepath):

    # start bridge export
    
    ob = context.object # selected object
    truss = ob.data # mesh data of truss
    
    numVerts = len(truss.vertices.items()) # calculate number of joints
    numEdges = len(truss.edges.items()) # calculate number of members
    
    # open output file
    f = open(filepath, "w")
    
    # print header
    print(uName)
    print(str(numVerts) + "\t\t%Number of Nodes")
    print(str(numEdges) + "\t\t%Number of Elements")
    f.write(uName + "\n")
    f.write(str(numVerts) + "\t\t%Number of Nodes\n")
    f.write(str(numEdges) + "\t\t%Number of Elements\n")

    # print node list header
    print("\nNode position")
    print("number\txvalue\tyvalue")
    f.write("\nNode position\n")
    f.write("number\txvalue\tyvalue\n")

    # TO PIN JOINTS: move vert to Z = 1 if pinned in X ONLY, move to Z = 2 if pinned in Y ONLY, move to Z = 3 if pinned in BOTH X AND Y
    xPins = [] # indices of joints pinned in X
    yPins = [] # indices of joints pinned in Y
    x = 0 # X pos of iterated joint
    y = 0 # Y pos of iterated joint
    z = 0 # Z pos of iterated joint
    numPins = 0 # total of constraints on joints

    # print joints
    for i in range(numVerts):
        x = truss.vertices.values()[i].co[0] # }
        y = truss.vertices.values()[i].co[1] # } get X,Y,Z coords of vertex
        z = truss.vertices.values()[i].co[2] # }
        print(str(i + 1) + "\t%.2f\t%.2f" % (x, y)) #          } print node position
        f.write(str(i + 1) + "\t%.2f\t%.2f" % (x, y) + "\n") # }
    
        # check for constraints (Z=0 => no constraints
        #   Z=1 => X ONLY constrained
        #   Z=2 => Y ONLY constrained
        #   Z=3 => X AND Y constrained
        if z > 2.5:
            xPins.append(i)
            yPins.append(i)
            numPins += 2
        elif z > 1.5:
            yPins.append(i)
            numPins += 1
        elif z > 0.5:
            xPins.append(i)
            numPins += 1

    # print member list header
    print("\nElements")
    print("number\tnode1\tnode2")
    f.write("\nElements\n")
    f.write("number\tnode1\tnode2\n")

    # print member list
    for i in range(numEdges):
        print(str(i + 1) + "\t" + str(truss.edges[i].vertices[0] + 1) + "\t" + str(truss.edges[i].vertices[1] + 1))
        f.write(str(i + 1) + "\t" + str(truss.edges[i].vertices[0] + 1) + "\t" + str(truss.edges[i].vertices[1] + 1) + "\n")

    # print constraints header
    print("\nDisplacements")
    print(str(numPins))
    print("Node#\t(x=1,y=2)\tvalue")
    f.write("\nDisplacements\n")
    f.write(str(numPins) + "\n")
    f.write("Node#\t(x=1,y=2)\tvalue\n")

    # print X constraints
    for i in range(len(xPins)):
        print(str(xPins[i] + 1) + "\t1\t0")
        f.write(str(xPins[i] + 1) + "\t1\t0\n")

    # print Y constraints
    for i in range(len(yPins)):
        print(str(yPins[i] + 1) + "\t2\t0")
        f.write(str(yPins[i] + 1) + "\t2\t0\n")
    
    f.close() # close output file

    # bridge export completed

    return 'FINISHED'

    
# = =============== =
# =  MAIN OPERATOR  =
# = =============== =

class ExportAsBridge(bpy.types.Operator):
    """Export code for statics bridge project"""        # tooltip
    bl_idname = "export.bridge_code"                    # identifier
    bl_label = "Export bridge code from selected mesh"  # display name in UI

    def execute(self, context):

        wm = context.window_manager
        uName = wm.header_name                                       # get header name from prop
        filepath = bpy.path.abspath("//") + "input.txt"              # get export path
        write_bridge(uName, context, filepath)                  # perform export
        self.report({'INFO'}, 'bridge code exported to ' + filepath) # print success and outpath

        return {'FINISHED'} # report success

    @classmethod
    def poll(cls, context): # enables/disables operator if mesh selected
        obj = context.active_object
        return (obj is not none and obj.type == 'MESH')

        
# = ===================== =
# =  MAKE SETTINGS PANEL  =
# = ===================== =

# set up string prop for name
bpy.types.WindowManager.header_name = bpy.props.StringProperty(name='Name',
                                                               default='Peter Gutfeldt',
                                                               description='Your name[s], for use in file header.'
                                                               )

class BridgeExportPanel(bpy.types.Panel): # the settings panel
    bl_label = 'Export Bridge Code' # rollout name
    bl_space_type = 'VIEW_3D'       # 3D view window
    bl_region_type = 'UI'           # add to "[N]" (right hand) panel (UI panel)

    def draw(self, context): # draw panel
        wm = bpy.context.window_manager
        col = self.layout.column(align=True)
        col.prop(wm, 'header_name')
        col.operator(ExportAsBridge.bl_idname, text="Export to input.txt", icon="LIBRARY_DATA_DIRECT")
        

def menu_func(self, context): # add option to file > export
    self.layout.operator(ExportAsBridge.bl_idname, text="Statics Bridge Code (.txt)")

def register():
    bpy.utils.register_class(ExportAsBridge)
    bpy.utils.register_class(BridgeExportPanel)
    bpy.types.INFO_MT_file_export.append(menu_func) 

def unregister():
    bpy.utils.unregister_class(ExportAsBridge)
    bpy.utils.unregister_class(BridgeExportPanel)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
