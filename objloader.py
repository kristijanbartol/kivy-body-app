from kivy.logger import Logger


# NOTE: The indices were wrong (in the Sensors implementation)!!!!!!! (6376->4376, 6375->4375)
WAIST_INDICES = [3500, 1336, 917, 916, 919, 918, 665, 662, 657, 654, 631, 632, 720, 799, 796, 890, 889, 3124, 3018, \
        3019, 3502, 6473, 6474, 6545, 4376, 4375, 4284, 4285, 4208, 4120, 4121, 4142, 4143, 4150, 4151, 4406, 4405, \
        4403, 4402, 4812]

CHEST_INDICES = [3076, 2870, 1254, 1255, 1349, 1351, 3033, 3030, 3037, 3034, 3039, 611, 2868, 2864, 2866, 1760, 1419, 741, \
        738, 759, 2957, 2907, 1435, 1436, 1437, 1252, 1235, 749, 752, 3015, 4238, 4718, 4735, 4908, 4909, 6366, 4252, 4251, \
        4224, 4133, 4132, 4896, 5230, 4683, 4682, 4089, 4101, 6485, 6481, 6482, 6477, 6478, 4828, 4825, 4740, 4737, 6332]

HIP_INDICES = [1806, 1805, 1804, 1803, 1802, 1801, 1800, 1798, 1797, 1796, 1794, 1791, 1788, 1787, 3101, 3114, 3121, \
        3098, 3099, 3159, 6522, 6523, 6542, 6537, 6525, 5252, 5251, 5255, 5256, 5258, 5260, 5261, 5264, 5263, 5266, \
        5265, 5268, 5267]

THIGH_INDICES = [877, 874, 873, 847, 848, 849, 902, 851, 852, 897, 900, 933, 936, 1359, 963, 908, 911, 1366]

CALF_INDICES = [1154, 1372, 1074, 1077, 1470, 1094, 1095, 1473, 1465, 1466, 1108, 1111, 1530, 1089, 1086]

ANKLE_INDICES = [3322, 3323, 3190, 3188, 3185, 3206, 3182, 3183, 3194, 3195, 3196, 3176, 3177, 3193, 3319]

WRIST_INDICES = [1922, 1970, 1969, 2244, 1945, 1943, 1979, 1938, 1935, 2286, 2243, 2242, 1930, 1927, 1926, 1924]

ELBOW_INDICES = [1573, 1915, 1914, 1577, 1576, 1912, 1911, 1624, 1625, 1917, 1611, 1610, 1607, 1608, 1916, 1574]

BICEP_INDICES = [789, 1311, 1315, 1379, 1378, 1394, 1393, 1389, 1388, 1233, 1232, 1385, 1381, 1382, 1397, 1396, 628, 627]

NECK_INDICES = [3068, 1311, 215, 216, 440, 441, 452, 218, 219, 222, 425, 426, 453, 829, 3944, 3921, 3920, 3734, \
        3731, 3730, 3943, 3935, 3934, 3728, 3729, 4807]

HEAD_INDICES = [336, 232, 235, 1, 2, 6, 7, 136, 160, 161, 166, 167, 269, 179, 182, 252, 253, 384, 3765, 3766, 3694, \
        3693, 3782, 3681, 3678, 3671, 3672, 3648, 3518, 3513, 3514, 3515, 3745, 3744]

class MeshData(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        self.vertices = []
        self.indices = []
        self.smpl_to_mesh_vertex_map = {}
        self.smpl_faces_data = []
        
        '''
        # Default basic material of mesh object
        self.diffuse_color = (1.0, 1.0, 1.0)
        self.ambient_color = (1.0, 1.0, 1.0)
        self.specular_color = (1.0, 1.0, 1.0)
        self.specular_coefficent = 16.0
        self.transparency = 1.0
        '''
        
    '''
    def set_materials(self, mtl_dict):
        self.diffuse_color = mtl_dict.get('Kd') or self.diffuse_color
        self.diffuse_color = [float(v) for v in self.diffuse_color]
        self.ambient_color = mtl_dict.get('Ka') or self.ambient_color
        self.ambient_color = [float(v) for v in self.ambient_color]
        self.specular_color = mtl_dict.get('Ks') or self.specular_color
        self.specular_color = [float(v) for v in self.specular_color]
        self.specular_coefficent = float(mtl_dict.get('Ns', self.specular_coefficent))
        transparency = mtl_dict.get('d')
        if not transparency: 
            transparency = 1.0 - float(mtl_dict.get('Tr', 0))
        self.transparency = float(transparency)

    def calculate_normals(self):
        for i in range(len(self.indices) / (3)):
            fi = i * 3
            v1i = self.indices[fi]
            v2i = self.indices[fi + 1]
            v3i = self.indices[fi + 2]

            vs = self.vertices
            p1 = [vs[v1i + c] for c in range(3)]
            p2 = [vs[v2i + c] for c in range(3)]
            p3 = [vs[v3i + c] for c in range(3)]

            u, v = [0, 0, 0], [0, 0, 0]
            for j in range(3):
                v[j] = p2[j] - p1[j]
                u[j] = p3[j] - p1[j]

            n = [0, 0, 0]
            n[0] = u[1] * v[2] - u[2] * v[1]
            n[1] = u[2] * v[0] - u[0] * v[2]
            n[2] = u[0] * v[1] - u[1] * v[0]

            for k in range(3):
                self.vertices[v1i + 3 + k] = n[k]
                self.vertices[v2i + 3 + k] = n[k]
                self.vertices[v3i + 3 + k] = n[k]
    '''


class ObjFile:
    def finish_object(self):
        #if self._current_object is None:
        #    return

        mesh = MeshData()
        idx = 0
        for f in self.faces:
            verts = f[0]
            norms = f[1]
            tcs = f[2]
            
            triangle_data = []
            include = False
            for i in range(3):
                # get normal components
                n = (0.0, 0.0, 0.0)
                if norms[i] != -1:
                    n = self.normals[norms[i] - 1]

                # get texture coordinate components
                t = (0.0, 0.0)
                if tcs[i] != -1:
                    t = self.texcoords[tcs[i] - 1]

                # get vertex components
                vertex_idx = verts[i] - 1
                v = self.vertices[vertex_idx]

                vertex_data = [v[0], v[1], v[2], n[0], n[1], n[2], t[0], t[1]]
                triangle_data.extend(vertex_data)
                #mesh.vertices.extend(data)
                
                # TODO: If the verts is in (any) body measurement list, add
                # 'data' list to extend the list of data for that body measurement.
                # For this, you need to create another class property to store these
                # information about each body measurement.
                if vertex_idx in WAIST_INDICES: #and vertex_idx not in mesh.smpl_to_mesh_vertex_map:
                    #mesh.smpl_to_mesh_vertex_map[vertex_idx] = int(len(mesh.vertices) / 8) - 1
                    mesh.smpl_to_mesh_vertex_map[vertex_idx] = [x for x in range(len(mesh.vertices) - 8, len(mesh.vertices))]
                    include = True

            mesh.vertices.extend(triangle_data)
            if include:
                mesh.smpl_faces_data.extend(triangle_data)

            tri = [idx, idx + 1, idx + 2]
            mesh.indices.extend(tri)
            idx += 3

        '''
        material = self.mtl.get(self.obj_material)
        if material:
            mesh.set_materials(material)
        '''
        self.objects[self._current_object] = mesh
        # mesh.calculate_normals()
        self.faces = []

    def __init__(self, resource, mode='str', swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.objects = {}
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        self._current_object = 'smpl'
        
        self.obj_material = None

        material = None
        if mode == 'str':
            lines = resource.split('\n')
        else:
            lines = open(resource, 'r').readlines()
        
        lines.append('mtllib monkey.mtl')

        for line in lines:
            if line.startswith('#'):
                continue
            if line.startswith('s'):
                continue
            values = line.split()
            if not values:
                continue
            if values[0] == 'o':
                self.finish_object()
                self._current_object = values[1]
            elif values[0] == 'mtllib':
                self.mtl = MTL(values[1])
            #elif values[0] in ('usemtl', 'usemat'):
            #    material = values[1]
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if int(w[0]) > 6890:
                        print('')
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(-1)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(-1)
                self.faces.append((face, norms, texcoords, material))
        self.finish_object()


def MTL(filename):
    contents = {}
    mtl = None
    #return
    for line in open(filename, "r"):
        if line.startswith('#'):
            continue
        values = line.split()
        if not values:
            continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError("mtl file doesn't start with newmtl stmt")
        mtl[values[0]] = values[1:]
    return contents

    def __getitem__(self, key):
        return self.contents[key]
    
    def get(self, key, default=None):
        return self.contents.get(key, default)

